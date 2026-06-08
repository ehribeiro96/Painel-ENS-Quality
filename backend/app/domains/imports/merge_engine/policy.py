from __future__ import annotations

from typing import Any

from app.domains.assets.models import Asset
from app.shared.enums import AssetStatus, AssetType
from app.shared.snapshots import asset_snapshot

TRUSTED_UPDATE_FIELDS = (
    "hostname",
    "patrimony",
    "serial",
    "manufacturer",
    "model",
    "asset_type",
    "operating_system",
    "ip_address",
    "last_login",
)


def build_asset_from_import(normalized: dict[str, Any], actor_id: Any) -> Asset:
    status = AssetStatus(normalized.get("status") or AssetStatus.CONFIG_PENDING.value)
    location = normalized.get("location")
    if not location:
        location = (normalized.get("source_metadata") or {}).get("unit")
    return Asset(
        hostname=normalized.get("hostname"),
        patrimony=normalized.get("patrimony"),
        serial=normalized.get("serial"),
        manufacturer=normalized.get("manufacturer"),
        model=normalized.get("model"),
        asset_type=AssetType(normalized.get("asset_type") or AssetType.OTHER.value),
        status=status,
        location=location,
        operating_system=normalized.get("operating_system"),
        ip_address=normalized.get("ip_address"),
        last_login=normalized.get("last_login"),
        notes=normalized.get("notes"),
        created_by=actor_id,
        updated_by=actor_id,
    )


def apply_trusted_updates(asset: Asset, normalized: dict[str, Any], actor_id: Any) -> tuple[dict[str, Any], dict[str, Any], bool]:
    before = asset_snapshot(asset)
    changed = False
    for field in TRUSTED_UPDATE_FIELDS:
        incoming = normalized.get(field)
        if incoming in (None, ""):
            continue
        current = getattr(asset, field)
        if field == "asset_type":
            incoming = AssetType(incoming)
        if current != incoming:
            setattr(asset, field, incoming)
            changed = True
    if changed:
        asset.updated_by = actor_id
    return before, asset_snapshot(asset), changed
