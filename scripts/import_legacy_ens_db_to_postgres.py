from __future__ import annotations

import argparse
import asyncio
import json
import re
import sqlite3
import sys
from collections import Counter
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
from app.domains.audit.service import AuditService  # noqa: E402
from app.domains.users.models import User  # noqa: E402
from app.shared.enums import AuditAction, Role, UserStatus  # noqa: E402
from sqlalchemy import func, select  # noqa: E402

REPORT_DIR = ROOT / "uat_evidence" / "legacy_ens_db_import"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LEGACY_SOURCE = "legacy_ens_db"
SENSITIVE_LEGACY_FIELDS = ["password_hash", "eh_admin", "must_change"]
SENSITIVE_ACCOUNT_SKIP_REASON = "SKIPPED_SENSITIVE_ACCOUNT_UPDATE"


@dataclass
class LegacyCandidate:
    source_record_id: int | None
    name: str
    email: str
    job_title: str | None
    department: str | None
    business_unit: str | None
    manager_name: str | None
    phone: str | None
    status: UserStatus
    login_hint: str | None
    metadata: dict[str, Any]
    valid: bool
    errors: list[str]


@dataclass(frozen=True)
class ImportPolicy:
    skip_sensitive_existing_users: bool = True
    sensitive_emails: frozenset[str] = frozenset()


def mask_email(email: str | None) -> str:
    value = (email or "").strip()
    if "@" not in value:
        return "<invalid_or_empty>"
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        return f"***@{domain}"
    return f"{local[:2]}***@{domain}"


def mask_name(name: str | None) -> str:
    value = (name or "").strip()
    if not value:
        return "<empty>"
    tokens = value.split()
    return " ".join(f"{token[:2]}***" if len(token) > 2 else "***" for token in tokens[:2])


def clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def map_status(value: Any) -> UserStatus:
    normalized = (clean(value) or "").lower()
    if normalized in {"off", "inactive", "inativo", "disabled"}:
        return UserStatus.INACTIVE
    return UserStatus.ACTIVE


def candidate_from_row(row: sqlite3.Row) -> LegacyCandidate:
    name = clean(row["nome_exibicao"]) or clean(row["name"]) or " ".join(
        item for item in [clean(row["first_name"]), clean(row["last_name"])] if item
    )
    email = (clean(row["email"]) or "").lower()
    phone = clean(row["telefone_ad"]) or clean(row["phone"])
    job_title = clean(row["campo_assinatura"]) or clean(row["role"]) or clean(row["posicao_organograma"])
    department = clean(row["department"]) or clean(row["diretoria"])
    business_unit = clean(row["uf"]) or clean(row["local_descricao"])
    errors: list[str] = []
    if not name:
        errors.append("missing_name")
    if not email:
        errors.append("missing_email")
    elif not EMAIL_RE.match(email):
        errors.append("invalid_email")

    metadata = {
        "source_record_id": row["id"],
        "legacy_imported_at": datetime.now(UTC).isoformat(),
        "import_mode": "legacy_seed",
        "source_database": "ens.db",
        "matricula": clean(row["matricula"]),
        "login": clean(row["matricula"]),
        "login_hint": clean(row["matricula"]),
        "status_legacy": clean(row["status"]),
        "diretoria": clean(row["diretoria"]),
        "local_descricao": clean(row["local_descricao"]),
        "endereco": clean(row["endereco"]),
        "legacy_updated_at": clean(row["updated_at"]),
        "extra": {
            "posicao_organograma": clean(row["posicao_organograma"]),
            "first_name": clean(row["first_name"]),
            "last_name": clean(row["last_name"]),
        },
    }
    metadata = {key: value for key, value in metadata.items() if value not in (None, "")}
    if isinstance(metadata.get("extra"), dict):
        metadata["extra"] = {key: value for key, value in metadata["extra"].items() if value not in (None, "")}
        if not metadata["extra"]:
            metadata.pop("extra")

    return LegacyCandidate(
        source_record_id=row["id"],
        name=name or "",
        email=email,
        job_title=job_title,
        department=department,
        business_unit=business_unit,
        manager_name=clean(row["manager"]),
        phone=phone,
        status=map_status(row["status"]),
        login_hint=clean(row["matricula"]),
        metadata=metadata,
        valid=not errors,
        errors=errors,
    )


def connect_sqlite(sqlite_path: Path) -> sqlite3.Connection:
    if not sqlite_path.exists() or not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite file not found: {sqlite_path}")
    conn = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def read_candidates(sqlite_path: Path) -> tuple[list[LegacyCandidate], dict[str, Any]]:
    conn = connect_sqlite(sqlite_path)
    try:
        tables = [
            dict(row)
            for row in conn.execute(
                "select name, type, sql from sqlite_master where type in ('table','index') order by type,name"
            )
        ]
        columns = {
            "colaboradores": [dict(row) for row in conn.execute("pragma table_info('colaboradores')")]
        }
        rows = list(conn.execute("select * from colaboradores"))
        candidates = [candidate_from_row(row) for row in rows]

        emails = [candidate.email for candidate in candidates if candidate.email]
        logins = [candidate.login_hint.lower() for candidate in candidates if candidate.login_hint]
        duplicate_emails = sorted(email for email, count in Counter(emails).items() if count > 1)
        duplicate_logins = sorted(login for login, count in Counter(logins).items() if count > 1)
        quality = {
            "total_rows": len(candidates),
            "valid_candidates": sum(1 for candidate in candidates if candidate.valid),
            "invalid_candidates": sum(1 for candidate in candidates if not candidate.valid),
            "without_email": sum(1 for candidate in candidates if "missing_email" in candidate.errors),
            "without_name": sum(1 for candidate in candidates if "missing_name" in candidate.errors),
            "duplicate_emails": len(duplicate_emails),
            "duplicate_logins": len(duplicate_logins),
            "status_distribution": dict(Counter(candidate.status.value for candidate in candidates)),
            "masked_samples": [
                {
                    "source_record_id": candidate.source_record_id,
                    "name": f"{candidate.name[:2]}***" if candidate.name else "<empty>",
                    "email": mask_email(candidate.email),
                    "status": candidate.status.value,
                }
                for candidate in candidates[:5]
            ],
        }
        inventory = {
            "tables": tables,
            "columns": columns,
            "quality": quality,
            "candidate_fields": {
                "name": ["nome_exibicao", "name", "first_name + last_name"],
                "email": ["email"],
                "job_title": ["campo_assinatura", "role", "posicao_organograma"],
                "department": ["department", "diretoria"],
                "business_unit": ["uf", "local_descricao"],
                "phone": ["telefone_ad", "phone"],
                "manager_name": ["manager"],
                "status": ["status"],
                "login_hint": ["matricula"],
                "source_metadata": ["id", "matricula", "diretoria", "local_descricao", "endereco", "updated_at"],
            },
            "sensitive_fields_discarded": SENSITIVE_LEGACY_FIELDS,
            "mapped_fields": {
                "source": LEGACY_SOURCE,
                "source_metadata": [
                    "source_record_id",
                    "legacy_imported_at",
                    "matricula",
                    "login",
                    "status_legacy",
                    "import_mode",
                    "source_database",
                ],
            },
        }
        return candidates, inventory
    finally:
        conn.close()


def write_report(payload: dict[str, Any], mode: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"legacy_ens_db_{mode.lower()}_{timestamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def merge_user(existing: User, candidate: LegacyCandidate) -> dict[str, Any]:
    changed: dict[str, Any] = {}
    for attr in ("name", "job_title", "department", "business_unit", "manager_name", "phone"):
        incoming = getattr(candidate, attr)
        current = getattr(existing, attr)
        if incoming and not current:
            setattr(existing, attr, incoming)
            changed[attr] = incoming
    if not existing.source:
        existing.source = LEGACY_SOURCE
        changed["source"] = LEGACY_SOURCE
    existing_metadata = dict(existing.source_metadata or {})
    next_metadata = {**existing_metadata, **candidate.metadata}
    if next_metadata != existing_metadata:
        existing.source_metadata = next_metadata
        changed["source_metadata"] = "updated"
    return changed


def planned_user_changes(existing: User, candidate: LegacyCandidate) -> dict[str, Any]:
    changed: dict[str, Any] = {}
    for attr in ("name", "job_title", "department", "business_unit", "manager_name", "phone"):
        incoming = getattr(candidate, attr)
        current = getattr(existing, attr)
        if incoming and not current:
            changed[attr] = incoming
    if not existing.source:
        changed["source"] = LEGACY_SOURCE
    existing_metadata = dict(existing.source_metadata or {})
    next_metadata = {**existing_metadata, **candidate.metadata}
    if next_metadata != existing_metadata:
        changed["source_metadata"] = "updated"
    return changed


def is_sensitive_existing_user(existing: User, policy: ImportPolicy) -> bool:
    email = (existing.email or "").strip().lower()
    role = str(existing.role or "").upper()
    return role.endswith("ADMIN") or email in policy.sensitive_emails


def sensitive_skip_record(existing: User, candidate: LegacyCandidate, changed: dict[str, Any]) -> dict[str, Any]:
    return {
        "email": mask_email(candidate.email),
        "current_name": mask_name(existing.name),
        "legacy_name": mask_name(candidate.name),
        "reason": SENSITIVE_ACCOUNT_SKIP_REASON,
        "fields_that_would_update": sorted(changed.keys()),
        "decision": "skipped",
    }


async def apply_to_postgres(candidates: list[LegacyCandidate], *, apply: bool, policy: ImportPolicy | None = None) -> dict[str, Any]:
    policy = policy or ImportPolicy()
    result = {
        "total_read": len(candidates),
        "valid_candidates": 0,
        "created": 0,
        "updated": 0,
        "ignored": 0,
        "duplicates": 0,
        "invalid": 0,
        "without_email": 0,
        "without_name": 0,
        "failures": 0,
        "planned_creates": 0,
        "planned_updates": 0,
        "sensitive_existing_users_detected": 0,
        "sensitive_updates_skipped": 0,
        "skipped_sensitive_accounts": [],
        "apply_blockers": [],
        "ready_for_apply": False,
        "policy": {
            "skip_sensitive_existing_users": policy.skip_sensitive_existing_users,
            "sensitive_email_count": len(policy.sensitive_emails),
        },
    }
    seen_emails: set[str] = set()

    async with AsyncSessionLocal() as session:
        try:
            for candidate in candidates:
                if "missing_email" in candidate.errors:
                    result["without_email"] += 1
                if "missing_name" in candidate.errors:
                    result["without_name"] += 1
                if not candidate.valid:
                    result["invalid"] += 1
                    continue
                result["valid_candidates"] += 1
                if candidate.email in seen_emails:
                    result["duplicates"] += 1
                    continue
                seen_emails.add(candidate.email)

                existing = (
                    await session.execute(select(User).where(func.lower(User.email) == candidate.email.lower()))
                ).scalar_one_or_none()
                if existing is None:
                    if apply:
                        session.add(
                            User(
                                name=candidate.name,
                                email=candidate.email,
                                job_title=candidate.job_title,
                                department=candidate.department,
                                business_unit=candidate.business_unit,
                                manager_name=candidate.manager_name,
                                phone=candidate.phone,
                                status=candidate.status,
                                role=Role.VIEWER,
                                source=LEGACY_SOURCE,
                                source_metadata=candidate.metadata,
                                created_by=None,
                                updated_by=None,
                            )
                        )
                    result["created"] += 1
                    result["planned_creates"] += 1
                    continue

                changed = planned_user_changes(existing, candidate)
                if changed and policy.skip_sensitive_existing_users and is_sensitive_existing_user(existing, policy):
                    result["sensitive_existing_users_detected"] += 1
                    result["sensitive_updates_skipped"] += 1
                    result["skipped_sensitive_accounts"].append(sensitive_skip_record(existing, candidate, changed))
                    result["ignored"] += 1
                    continue

                if changed:
                    if apply:
                        merge_user(existing, candidate)
                    result["updated"] += 1
                    result["planned_updates"] += 1
                else:
                    result["ignored"] += 1

            result["ready_for_apply"] = not result["apply_blockers"] and result["failures"] == 0 and result["invalid"] == 0
            if apply:
                await AuditService(session).record(
                    action=AuditAction.IMPORT,
                    entity="User",
                    entity_id=None,
                    actor_id=None,
                    after={"source": "legacy_ens_db", "result": result},
                    source=LEGACY_SOURCE,
                )
                await session.commit()
            else:
                await session.rollback()
        except Exception:
            await session.rollback()
            raise

    return result


async def run(sqlite_path: Path, mode: str, confirm_apply: str | None, policy: ImportPolicy | None = None) -> int:
    if mode == "Apply" and confirm_apply != "APPLY_LEGACY_ENS_DB":
        raise RuntimeError("Apply requires --confirm-apply APPLY_LEGACY_ENS_DB")

    policy = policy or ImportPolicy()
    candidates, inventory = read_candidates(sqlite_path)
    payload: dict[str, Any] = {
        "sqlite_path": str(sqlite_path),
        "sqlite_size_bytes": sqlite_path.stat().st_size,
        "mode": mode,
        "classification": "LEGACY_SQLITE_SEED_SOURCE",
        "inventory": inventory,
        "policy": {
            "skip_sensitive_existing_users": policy.skip_sensitive_existing_users,
            "sensitive_email_count": len(policy.sensitive_emails),
        },
    }

    if mode == "AnalyzeOnly":
        path = write_report(payload, mode)
        print(f"AnalyzeOnly completed. Report: {path}")
        return 0

    apply = mode == "Apply"
    result = await apply_to_postgres(candidates, apply=apply, policy=policy)
    payload["postgres_result"] = result
    path = write_report(payload, mode)
    print(f"{mode} completed. Report: {path}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import legacy ENS SQLite collaborators into PostgreSQL.")
    parser.add_argument("--sqlite-path", required=True, type=Path)
    parser.add_argument("--mode", choices=["AnalyzeOnly", "DryRun", "Apply"], default="AnalyzeOnly")
    parser.add_argument("--confirm-apply", default=None)
    parser.add_argument(
        "--skip-sensitive-existing-users",
        action="store_true",
        default=True,
        help="Skip updates to existing admin/sensitive users. Enabled by default.",
    )
    parser.add_argument(
        "--sensitive-email",
        action="append",
        default=[],
        help="Treat this existing user email as sensitive. May be passed multiple times.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = ImportPolicy(
        skip_sensitive_existing_users=args.skip_sensitive_existing_users,
        sensitive_emails=frozenset(email.strip().lower() for email in args.sensitive_email if email.strip()),
    )
    return asyncio.run(run(args.sqlite_path, args.mode, args.confirm_apply, policy))


if __name__ == "__main__":
    raise SystemExit(main())
