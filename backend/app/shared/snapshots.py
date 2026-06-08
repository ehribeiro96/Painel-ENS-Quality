from __future__ import annotations

from typing import Any

from app.domains.assets.models import Asset
from app.domains.users.models import User


def _json_value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def asset_snapshot(asset: Asset) -> dict[str, Any]:
    return {
        "id": str(asset.id),
        "hostname": asset.hostname,
        "patrimony": asset.patrimony,
        "serial": asset.serial,
        "manufacturer": asset.manufacturer,
        "model": asset.model,
        "asset_type": _json_value(asset.asset_type),
        "status": _json_value(asset.status),
        "location": asset.location,
        "current_user_id": str(asset.current_user_id) if asset.current_user_id else None,
        "deleted_at": asset.deleted_at.isoformat() if asset.deleted_at else None,
    }


def user_snapshot(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "job_title": user.job_title,
        "department": user.department,
        "business_unit": user.business_unit,
        "manager_name": user.manager_name,
        "phone": user.phone,
        "status": _json_value(user.status),
        "role": _json_value(user.role),
        "source": user.source,
        "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
    }
