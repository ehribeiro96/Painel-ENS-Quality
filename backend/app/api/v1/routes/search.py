from __future__ import annotations

from app.api.v1.dependencies.auth import get_current_user
from app.core.database.session import get_session
from app.domains.assets.models import Asset
from app.domains.users.models import User
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def global_search(
    q: str = Query(..., min_length=2, max_length=120),
    limit: int = Query(8, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    term = f"%{q.strip()}%"
    asset_result = await session.execute(
        select(Asset)
        .outerjoin(User, Asset.current_user_id == User.id)
        .where(
            Asset.deleted_at.is_(None),
            or_(
                Asset.hostname.ilike(term),
                Asset.serial.ilike(term),
                Asset.patrimony.ilike(term),
                Asset.location.ilike(term),
                User.name.ilike(term),
                User.email.ilike(term),
            ),
        )
        .order_by(Asset.updated_at.desc())
        .limit(limit)
    )
    user_result = await session.execute(
        select(User)
        .where(
            User.deleted_at.is_(None),
            or_(
                User.name.ilike(term),
                User.email.ilike(term),
                User.department.ilike(term),
                User.business_unit.ilike(term),
            ),
        )
        .order_by(User.name)
        .limit(limit)
    )
    assets = [
        {
            "id": str(asset.id),
            "type": "asset",
            "title": asset.hostname or asset.patrimony or asset.serial or str(asset.id),
            "subtitle": " | ".join(filter(None, [asset.patrimony, asset.serial, asset.location])),
            "href": f"/assets/{asset.id}",
        }
        for asset in asset_result.scalars()
    ]
    users = [
        {
            "id": str(user.id),
            "type": "user",
            "title": user.name,
            "subtitle": " | ".join(filter(None, [user.email, user.department, user.business_unit])),
            "href": f"/users/{user.id}",
        }
        for user in user_result.scalars()
    ]
    return {"query": q, "items": assets + users}
