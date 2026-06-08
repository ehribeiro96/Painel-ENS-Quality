from __future__ import annotations

from app.domains.assets.models import Asset
from app.domains.movements.models import AssetMovement
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def summary(self) -> dict[str, int]:
        rows = await self.session.execute(select(Asset.status, func.count()).where(Asset.deleted_at.is_(None)).group_by(Asset.status))
        by_status = {status.value: count for status, count in rows.all()}
        no_user = await self.session.scalar(select(func.count()).select_from(Asset).where(Asset.deleted_at.is_(None), Asset.current_user_id.is_(None)))
        return {
            "total_assets": sum(by_status.values()),
            "in_use": by_status.get("IN_USE", 0),
            "stock": by_status.get("STOCK", 0),
            "maintenance": by_status.get("MAINTENANCE", 0),
            "defective": by_status.get("DEFECTIVE", 0),
            "without_user": no_user or 0,
        }

    async def group_by(self, column_name: str) -> list[dict[str, str | int]]:
        column = getattr(Asset, column_name)
        rows = await self.session.execute(select(column, func.count()).where(Asset.deleted_at.is_(None)).group_by(column).order_by(func.count().desc()))
        return [{"name": str(name), "value": count} for name, count in rows.all()]

    async def recent_movements(self, limit: int = 10) -> list[AssetMovement]:
        result = await self.session.execute(select(AssetMovement).order_by(AssetMovement.created_at.desc()).limit(limit))
        return list(result.scalars())
