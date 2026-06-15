from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domains.assets.models import Asset
from app.domains.imports.classification.identity_classifier import identity_for
from app.domains.imports.conflict_detection.detector import detect_row_conflict as _legacy_detect_row_conflict
from app.shared.enums import ImportDecision


def _enrich_issue(issue: dict[str, Any], *, conflict_key: str, reason: str, recommended_action: str) -> dict[str, Any]:
    enriched = dict(issue)
    enriched.setdefault("reason", reason)
    enriched.setdefault("conflict_key", conflict_key)
    enriched.setdefault("recommended_action", recommended_action)
    return enriched


def build_internal_duplicate_plan(normalized_rows: list[dict[str, object]]) -> dict[int, dict[str, object]]:
    plan: dict[int, dict[str, object]] = {}

    def group_by(field: str) -> dict[str, list[int]]:
        groups: dict[str, list[int]] = {}
        for index, row in enumerate(normalized_rows):
            value = row.get(field)
            if value:
                groups.setdefault(str(value), []).append(index)
        return groups

    for serial, indexes in group_by("serial").items():
        hostnames = {str(normalized_rows[index].get("hostname")) for index in indexes if normalized_rows[index].get("hostname")}
        if len(hostnames) > 1:
            issue = {
                "code": "serial_hostname_divergence",
                "identity_type": "serial",
                "identity_value": serial,
                "rows": [row + 2 for row in indexes],
                "hostnames": sorted(hostnames),
                "message": f"Conflito real: serial {serial} aparece com hostnames diferentes.",
                "reason": "Serial duplicado com hostnames divergentes no arquivo.",
                "conflict_key": f"serial:{serial}",
                "recommended_action": "Revisar manualmente antes do apply.",
                "suggested_action": "Revisar manualmente antes do apply.",
            }
            for index in indexes:
                plan[index] = {"decision": ImportDecision.CONFLICT, "issue": issue}

    for hostname, indexes in group_by("hostname").items():
        serials = {str(normalized_rows[index].get("serial")) for index in indexes if normalized_rows[index].get("serial")}
        if len(serials) > 1:
            issue = {
                "code": "hostname_serial_divergence",
                "identity_type": "hostname",
                "identity_value": hostname,
                "rows": [row + 2 for row in indexes],
                "serials": sorted(serials),
                "message": f"Conflito real: hostname {hostname} aparece com seriais diferentes.",
                "reason": "Hostname duplicado com seriais divergentes no arquivo.",
                "conflict_key": f"hostname:{hostname}",
                "recommended_action": "Revisar manualmente antes do apply.",
                "suggested_action": "Revisar manualmente antes do apply.",
            }
            for index in indexes:
                plan[index] = {"decision": ImportDecision.CONFLICT, "issue": issue}

    primary_groups: dict[tuple[str, str], list[int]] = {}
    for index, row in enumerate(normalized_rows):
        identity_type, identity_value = identity_for(row)
        if identity_type and identity_value:
            primary_groups.setdefault((identity_type, identity_value), []).append(index)

    for (identity_type, identity_value), indexes in primary_groups.items():
        if len(indexes) < 2 or any(index in plan for index in indexes):
            continue
        canonical = max(indexes, key=lambda index: _canonical_score(normalized_rows[index]))
        for index in indexes:
            if index == canonical:
                continue
            issue = {
                "code": "skipped_duplicate_in_file",
                "identity_type": identity_type,
                "identity_value": identity_value,
                "rows": [row + 2 for row in indexes],
                "canonical_row": canonical + 2,
                "message": f"Duplicidade no arquivo: {identity_type} {identity_value} aparece em múltiplas linhas. O sistema manterá a linha {canonical + 2} e ignorará esta duplicata equivalente.",
                "reason": "Duplicata equivalente no arquivo; linha secundária ignorada.",
                "conflict_key": f"{identity_type}:{identity_value}",
                "recommended_action": "Nenhuma ação necessária se os dados forem equivalentes.",
                "suggested_action": "Nenhuma ação necessária se os dados forem equivalentes.",
            }
            plan[index] = {"decision": ImportDecision.SKIPPED_DUPLICATE_IN_FILE, "issue": issue}
    return plan


def _canonical_score(row: dict[str, object]) -> tuple[int, int, float, int, int, int]:
    useful_fields = sum(1 for value in row.values() if value not in (None, "", {}, []))
    return (
        1 if row.get("serial") else 0,
        1 if row.get("hostname") else 0,
        _last_seen_score(row),
        useful_fields,
        1 if row.get("asset_type") and row.get("asset_type") != "OTHER" else 0,
        1 if row.get("status") else 0,
    )


def _last_seen_score(row: dict[str, object]) -> float:
    from datetime import datetime

    import pandas as pd

    value = row.get("last_login") or (row.get("source_metadata") or {}).get("last_seen")
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except ValueError:
        parsed = pd.to_datetime(str(value), errors="coerce")
        if pd.isna(parsed):
            return 0.0
        return parsed.timestamp()


def detect_row_conflict(
    normalized: dict[str, Any],
    existing_by_serial: dict[str, Asset],
    existing_by_patrimony: dict[str, Asset],
    existing_by_hostname: dict[str, Asset],
    seen_identities: set[tuple[str, str]],
) -> tuple[ImportDecision, UUID | None, str | None, list[dict[str, Any]]]:
    result = _legacy_detect_row_conflict(normalized, existing_by_serial, existing_by_patrimony, existing_by_hostname, seen_identities)
    if result.decision == ImportDecision.CONFLICT and result.issues:
        identity_type, identity_value = identity_for(normalized)
        conflict_key = f"{identity_type}:{identity_value}" if identity_type and identity_value else "import-conflict"
        issues = [
            _enrich_issue(
                issue,
                conflict_key=conflict_key,
                reason=issue.get("reason") or "Conflito detectado durante a importacao.",
                recommended_action=issue.get("recommended_action") or "Revisar manualmente antes do apply.",
            )
            for issue in result.issues
        ]
        return result.decision, result.matched_asset_id, result.merge_action, issues
    if result.decision == ImportDecision.REVIEW_REQUIRED and result.issues:
        issues = [
            _enrich_issue(
                issue,
                conflict_key=str(issue.get("identity_value") or "source_external_key"),
                reason=issue.get("reason") or "Linha sem identidade patrimonial forte; revisão necessária.",
                recommended_action=issue.get("recommended_action") or "Revisar antes de aplicar.",
            )
            for issue in result.issues
        ]
        return result.decision, result.matched_asset_id, result.merge_action, issues
    return result.decision, result.matched_asset_id, result.merge_action, result.issues
