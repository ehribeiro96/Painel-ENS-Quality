from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import app.core.database.base  # noqa: E402,F401
from app.core.database.session import AsyncSessionLocal  # noqa: E402
from app.domains.macros.models import MacroTemplate  # noqa: E402
from app.domains.macros.renderer import extract_placeholders  # noqa: E402
from app.domains.macros.service import category_from_name, slugify  # noqa: E402
from sqlalchemy import select  # noqa: E402

REPORT_DIR = ROOT / "uat_evidence" / "macros_import"
MACROS_SOURCE = "macros_json"


@dataclass
class MacroCandidate:
    name: str
    slug: str
    category: str
    description: str | None
    template_text: str
    required_fields: list[str]
    optional_fields: list[str]
    context_type: str | None
    version: str
    valid: bool
    errors: list[str]


def load_json(path: Path) -> Any:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def iter_macro_items(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        if isinstance(raw.get("macros"), list):
            return [item for item in raw["macros"] if isinstance(item, dict)]
        items: list[dict[str, Any]] = []
        for key, value in raw.items():
            if isinstance(value, str):
                items.append({"name": key, "template_text": value})
            elif isinstance(value, dict):
                items.append({"name": key, **value})
        return items
    return []


def candidate_from_item(item: dict[str, Any]) -> MacroCandidate:
    name = str(item.get("name") or item.get("title") or item.get("label") or "").strip()
    template_text = str(
        item.get("template_text")
        or item.get("texto")
        or item.get("text")
        or item.get("content")
        or item.get("body")
        or item.get("macro")
        or ""
    ).strip()
    if slugify(name) in {"atualizacao-de-inventario", "atualizar-inventario"}:
        name = "[Ativos] Atualizar inventário"
    errors: list[str] = []
    if not name:
        errors.append("missing_name")
    if not template_text:
        errors.append("missing_template_text")
    fields = extract_placeholders(template_text) if template_text else []
    category = str(item.get("category") or category_from_name(name)).strip() or "Geral"
    context_type = item.get("context_type")
    if not context_type and name.startswith("[Ativos]"):
        context_type = "asset_movement"
    return MacroCandidate(
        name=name,
        slug=str(item.get("slug") or slugify(name)).strip(),
        category=category,
        description=item.get("description"),
        template_text=template_text,
        required_fields=list(item.get("required_fields") or item.get("campos") or fields),
        optional_fields=list(item.get("optional_fields") or []),
        context_type=context_type,
        version=str(item.get("version") or "macros_json.1"),
        valid=not errors,
        errors=errors,
    )


def read_candidates(path: Path) -> list[MacroCandidate]:
    return [candidate_from_item(item) for item in iter_macro_items(load_json(path))]


def build_candidate_diagnostics(candidates: list[MacroCandidate]) -> dict[str, Any]:
    seen_slugs: set[str] = set()
    duplicate_slugs: list[str] = []
    invalid_macros: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate.slug in seen_slugs and candidate.slug not in duplicate_slugs:
            duplicate_slugs.append(candidate.slug)
        seen_slugs.add(candidate.slug)
        if not candidate.valid:
            invalid_macros.append({"name": candidate.name, "slug": candidate.slug, "errors": candidate.errors})
    return {
        "total_candidates": len(candidates),
        "valid_candidates": sum(1 for candidate in candidates if candidate.valid),
        "invalid_candidates": len(invalid_macros),
        "duplicate_slugs": duplicate_slugs,
        "invalid_macros": invalid_macros,
        "names": [candidate.name for candidate in candidates],
        "slugs": [candidate.slug for candidate in candidates],
        "count_explanation": (
            "total_candidates counts every parsed macro candidate from the selected json_path; "
            "valid_candidates excludes only entries with missing required data, while duplicate_slugs are reported separately."
        ),
    }


def write_report(payload: dict[str, Any], mode: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"macros_json_{mode.lower()}_{timestamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


async def compare_or_apply(candidates: list[MacroCandidate], *, apply: bool, update_existing: bool) -> dict[str, Any]:
    result = {
        "total_read": len(candidates),
        "valid": 0,
        "created": 0,
        "updated": 0,
        "ignored": 0,
        "invalid": 0,
        "failures": 0,
        "required_apply_confirmation": "APPLY_MACROS_JSON",
    }
    seen_slugs: set[str] = set()
    async with AsyncSessionLocal() as session:
        try:
            for candidate in candidates:
                if not candidate.valid or candidate.slug in seen_slugs:
                    result["invalid"] += 1
                    continue
                result["valid"] += 1
                seen_slugs.add(candidate.slug)
                existing = await session.scalar(select(MacroTemplate).where(MacroTemplate.slug == candidate.slug))
                if existing is None:
                    result["created"] += 1
                    if apply:
                        session.add(
                            MacroTemplate(
                                name=candidate.name,
                                slug=candidate.slug,
                                category=candidate.category,
                                description=candidate.description,
                                template_text=candidate.template_text,
                                required_fields=candidate.required_fields,
                                optional_fields=candidate.optional_fields,
                                context_type=candidate.context_type,
                                source=MACROS_SOURCE,
                                version=candidate.version,
                            )
                        )
                    continue
                if update_existing:
                    result["updated"] += 1
                    if apply:
                        existing.name = candidate.name
                        existing.category = candidate.category
                        existing.description = candidate.description
                        existing.template_text = candidate.template_text
                        existing.required_fields = candidate.required_fields
                        existing.optional_fields = candidate.optional_fields
                        existing.context_type = candidate.context_type
                        existing.version = candidate.version
                else:
                    result["ignored"] += 1
            if apply:
                await session.commit()
            else:
                await session.rollback()
        except Exception:
            await session.rollback()
            raise
    return result


async def run(path: Path, mode: str, confirm_apply: str | None, update_existing: bool) -> int:
    if mode == "Apply" and confirm_apply != "APPLY_MACROS_JSON":
        raise RuntimeError("Apply requires --confirm-apply APPLY_MACROS_JSON")
    candidates = read_candidates(path)
    payload: dict[str, Any] = {
        "json_path": str(path),
        "mode": mode,
        "source": MACROS_SOURCE,
        "diagnostics": build_candidate_diagnostics(candidates),
        "macros": [
            {
                "name": candidate.name,
                "slug": candidate.slug,
                "category": candidate.category,
                "required_fields": candidate.required_fields,
                "valid": candidate.valid,
                "errors": candidate.errors,
            }
            for candidate in candidates
        ],
    }
    if mode != "AnalyzeOnly":
        payload["postgres_result"] = await compare_or_apply(candidates, apply=mode == "Apply", update_existing=update_existing)
    path_out = write_report(payload, mode)
    print(f"{mode} completed. Report: {path_out}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import macros.json into PostgreSQL macro_templates.")
    parser.add_argument("--json-path", required=True, type=Path)
    parser.add_argument("--mode", choices=["AnalyzeOnly", "DryRun", "Apply"], default="AnalyzeOnly")
    parser.add_argument("--confirm-apply", default=None)
    parser.add_argument("--update-existing", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(run(args.json_path, args.mode, args.confirm_apply, args.update_existing))


if __name__ == "__main__":
    raise SystemExit(main())
