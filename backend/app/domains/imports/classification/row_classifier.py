from __future__ import annotations

from uuid import UUID

from app.domains.assets.models import Asset
from app.domains.imports.classification.conflict_detector import detect_row_conflict
from app.domains.imports.validators.asset_validator import validate_normalized_asset, validate_raw_row_security
from app.shared.enums import ImportDecision


def classify_row(
    raw_row: dict[str, object],
    normalized: dict[str, object],
    duplicate_action: dict[str, object] | None,
    existing_by_serial: dict[str, Asset],
    existing_by_patrimony: dict[str, Asset],
    existing_by_hostname: dict[str, Asset],
    seen_identities: set[tuple[str, str]],
) -> tuple[ImportDecision, list[dict[str, object]], UUID | None, str | None]:
    validation_issues = _dedupe_issues(validate_raw_row_security(raw_row) + validate_normalized_asset(normalized))
    if validation_issues:
        return ImportDecision.INVALID, validation_issues, None, None

    if duplicate_action:
        decision = duplicate_action["decision"]
        issue = duplicate_action["issue"]
        if decision == ImportDecision.SKIPPED_DUPLICATE_IN_FILE:
            return ImportDecision.SKIPPED_DUPLICATE_IN_FILE, [issue], None, "SKIP_DUPLICATE_IN_FILE"
        if decision == ImportDecision.CONFLICT:
            return ImportDecision.CONFLICT, [issue], None, "REVIEW"

    decision, matched_asset_id, merge_action, issues = detect_row_conflict(
        normalized,
        existing_by_serial,
        existing_by_patrimony,
        existing_by_hostname,
        seen_identities,
    )
    return decision, issues, matched_asset_id, merge_action


def _dedupe_issues(issues: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, object]] = []
    for issue in issues:
        key = (str(issue.get("field") or "row"), str(issue.get("code") or "validation_error"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(issue)
    return deduped
