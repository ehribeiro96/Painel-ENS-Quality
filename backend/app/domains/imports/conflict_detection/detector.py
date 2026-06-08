from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.domains.assets.models import Asset
from app.shared.enums import ImportDecision


@dataclass(frozen=True)
class DetectionResult:
    decision: ImportDecision
    matched_asset_id: UUID | None
    merge_action: str | None
    issues: list[dict[str, Any]] = field(default_factory=list)


def detect_row_conflict(
    normalized: dict[str, Any],
    existing_by_serial: dict[str, Asset],
    existing_by_patrimony: dict[str, Asset],
    existing_by_hostname: dict[str, Asset],
    seen_identities: set[tuple[str, str]],
) -> DetectionResult:
    identities = [
        ("serial", normalized.get("serial")),
        ("patrimony", normalized.get("patrimony")),
        ("hostname", normalized.get("hostname")),
        ("source_external_key", normalized.get("source_external_key")),
    ]
    active_identities = [(key, str(value)) for key, value in identities if value]

    duplicate_keys = [identity for identity in active_identities if identity in seen_identities]
    for identity in active_identities:
        seen_identities.add(identity)
    if duplicate_keys:
        return DetectionResult(
            decision=ImportDecision.CONFLICT,
            matched_asset_id=None,
            merge_action=None,
            issues=[{"code": "duplicate_in_file", "identities": duplicate_keys}],
        )

    matched_assets = set()
    if normalized.get("serial") and normalized["serial"] in existing_by_serial:
        matched_assets.add(existing_by_serial[normalized["serial"]])
    if normalized.get("patrimony") and normalized["patrimony"] in existing_by_patrimony:
        matched_assets.add(existing_by_patrimony[normalized["patrimony"]])
    if normalized.get("hostname") and normalized["hostname"] in existing_by_hostname:
        matched_assets.add(existing_by_hostname[normalized["hostname"]])

    if len(matched_assets) > 1:
        return DetectionResult(
            decision=ImportDecision.CONFLICT,
            matched_asset_id=None,
            merge_action=None,
            issues=[{"code": "multiple_assets_match", "asset_ids": [str(asset.id) for asset in matched_assets]}],
        )

    if len(matched_assets) == 1:
        matched = next(iter(matched_assets))
        protected_issues = []
        imported_location = normalized.get("location")
        if imported_location and matched.location and imported_location != matched.location:
            protected_issues.append({"code": "location_divergence", "current": matched.location, "incoming": imported_location})
        source_state = (normalized.get("source_metadata") or {}).get("source_state")
        if source_state and getattr(matched.status, "value", matched.status) != normalized.get("status"):
            protected_issues.append({"code": "status_divergence", "current": getattr(matched.status, "value", matched.status), "incoming": source_state})
        return DetectionResult(
            decision=ImportDecision.SAFE_UPDATE,
            matched_asset_id=matched.id,
            merge_action="UPDATE_TRUSTED_FIELDS",
            issues=protected_issues,
        )

    if normalized.get("source_external_key") and not any(normalized.get(key) for key in ("serial", "patrimony", "hostname")):
        return DetectionResult(
            decision=ImportDecision.REVIEW_REQUIRED,
            matched_asset_id=None,
            merge_action="REVIEW_IP_ONLY_SOURCE_KEY",
            issues=[
                {
                    "code": "weak_source_external_identity",
                    "field": "identity",
                    "message": "Linha sem identidade patrimonial forte; IP/name de origem preservado como chave externa para revisao.",
                    "identity_type": "source_external_key",
                    "identity_value": normalized.get("source_external_key"),
                    "suggested_action": "Revisar antes de aplicar ou completar serial/patrimonio/hostname.",
                }
            ],
        )

    return DetectionResult(decision=ImportDecision.CREATE, matched_asset_id=None, merge_action="CREATE_ASSET")
