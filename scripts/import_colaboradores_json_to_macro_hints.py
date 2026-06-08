from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import app.core.database.base  # noqa: E402,F401
from app.core.database.session import AsyncSessionLocal  # noqa: E402
from app.domains.macros.models import MacroAutocompleteHint  # noqa: E402
from app.domains.macros.service import normalize_label  # noqa: E402
from sqlalchemy import select  # noqa: E402

REPORT_DIR = ROOT / "uat_evidence" / "macro_hints_import"
HINT_SOURCE = "colaboradores_json"
HINT_TYPE = "collaborator_name"


def load_labels(path: Path) -> list[str]:
    raw: Any = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(raw, list):
        values = raw
    elif isinstance(raw, dict):
        values = raw.get("colaboradores") or raw.get("items") or raw.get("names") or []
    else:
        values = []
    labels: list[str] = []
    for item in values:
        if isinstance(item, str):
            label = item.strip()
        elif isinstance(item, dict):
            label = str(item.get("name") or item.get("nome") or item.get("label") or "").strip()
        else:
            label = ""
        if label:
            labels.append(label)
    return labels


def write_report(payload: dict[str, Any], mode: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"colaboradores_hints_{mode.lower()}_{timestamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


async def compare_or_apply(labels: list[str], *, apply: bool) -> dict[str, int]:
    result = {"total_read": len(labels), "valid": 0, "created": 0, "ignored": 0, "invalid": 0}
    seen: set[str] = set()
    async with AsyncSessionLocal() as session:
        try:
            for label in labels:
                normalized = normalize_label(label)
                if not normalized or normalized in seen:
                    result["invalid"] += 1
                    continue
                seen.add(normalized)
                result["valid"] += 1
                existing = await session.scalar(
                    select(MacroAutocompleteHint).where(
                        MacroAutocompleteHint.hint_type == HINT_TYPE,
                        MacroAutocompleteHint.source == HINT_SOURCE,
                        MacroAutocompleteHint.normalized_label == normalized,
                    )
                )
                if existing:
                    result["ignored"] += 1
                    continue
                result["created"] += 1
                if apply:
                    session.add(
                        MacroAutocompleteHint(
                            label=label,
                            normalized_label=normalized,
                            hint_type=HINT_TYPE,
                            source=HINT_SOURCE,
                        )
                    )
            if apply:
                await session.commit()
            else:
                await session.rollback()
        except Exception:
            await session.rollback()
            raise
    return result


async def run(path: Path, mode: str, confirm_apply: str | None) -> int:
    if mode == "Apply" and confirm_apply != "APPLY_COLABORADORES_HINTS":
        raise RuntimeError("Apply requires --confirm-apply APPLY_COLABORADORES_HINTS")
    labels = load_labels(path)
    payload: dict[str, Any] = {
        "json_path": str(path),
        "mode": mode,
        "source": HINT_SOURCE,
        "hint_type": HINT_TYPE,
        "total_labels": len(labels),
        "masked_samples": [f"{label[:2]}***" for label in labels[:5]],
    }
    if mode != "AnalyzeOnly":
        payload["postgres_result"] = await compare_or_apply(labels, apply=mode == "Apply")
    path_out = write_report(payload, mode)
    print(f"{mode} completed. Report: {path_out}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import colaboradores.json as macro autocomplete hints.")
    parser.add_argument("--json-path", required=True, type=Path)
    parser.add_argument("--mode", choices=["AnalyzeOnly", "DryRun", "Apply"], default="AnalyzeOnly")
    parser.add_argument("--confirm-apply", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(run(args.json_path, args.mode, args.confirm_apply))


if __name__ == "__main__":
    raise SystemExit(main())
