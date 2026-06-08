from __future__ import annotations

from uuid import UUID

from app.core.observability.metrics import metrics
from app.domains.assets.models import Asset
from app.domains.assets.schemas import AssetCreate, AssetMove, AssetUpdate
from app.domains.audit.service import AuditService
from app.domains.movements.models import AssetMovement
from app.domains.users.models import User
from app.shared.audit_context import AuditContext
from app.shared.enums import AssetStatus, AssetType, AuditAction
from app.shared.models import utc_now
from app.shared.pagination import Page, PageParams
from app.shared.snapshots import asset_snapshot
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class AssetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        params: PageParams,
        search: str | None = None,
        status: AssetStatus | None = None,
        asset_type: AssetType | None = None,
        location: str | None = None,
        without_user: bool = False,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> Page[Asset]:
        filters = [Asset.deleted_at.is_(None)]
        query = select(Asset)
        count_query = select(func.count()).select_from(Asset)
        if search:
            term = f"%{search}%"
            query = query.outerjoin(User, Asset.current_user_id == User.id)
            count_query = count_query.outerjoin(User, Asset.current_user_id == User.id)
            filters.append(
                or_(
                    Asset.hostname.ilike(term),
                    Asset.serial.ilike(term),
                    Asset.patrimony.ilike(term),
                    Asset.model.ilike(term),
                    Asset.location.ilike(term),
                    User.name.ilike(term),
                    User.email.ilike(term),
                )
            )
        if status:
            filters.append(Asset.status == status)
        if asset_type:
            filters.append(Asset.asset_type == asset_type)
        if location:
            filters.append(Asset.location.ilike(f"%{location}%"))
        if without_user:
            filters.append(Asset.current_user_id.is_(None))
        sort_columns = {
            "hostname": Asset.hostname,
            "patrimony": Asset.patrimony,
            "serial": Asset.serial,
            "status": Asset.status,
            "location": Asset.location,
            "updated_at": Asset.updated_at,
            "created_at": Asset.created_at,
        }
        sort_column = sort_columns.get(sort_by, Asset.updated_at)
        order_clause = sort_column.asc().nullslast() if sort_order == "asc" else sort_column.desc().nullslast()
        total = await self.session.scalar(count_query.where(*filters))
        result = await self.session.execute(
            query.options(selectinload(Asset.current_user))
            .where(*filters)
            .order_by(order_clause, Asset.id)
            .offset(params.offset)
            .limit(params.page_size)
        )
        return Page(items=list(result.scalars()), total=total or 0, page=params.page, page_size=params.page_size)

    async def get(self, asset_id: UUID) -> Asset | None:
        return await self.session.scalar(
            select(Asset).options(selectinload(Asset.current_user)).where(Asset.id == asset_id, Asset.deleted_at.is_(None))
        )

    async def get_for_update(self, asset_id: UUID) -> Asset | None:
        return await self.session.scalar(
            select(Asset)
            .options(selectinload(Asset.current_user))
            .where(Asset.id == asset_id, Asset.deleted_at.is_(None))
            .with_for_update()
        )

    async def create(self, payload: AssetCreate, actor_id: UUID | None, audit_context: AuditContext | None = None) -> Asset:
        asset = Asset(**payload.model_dump())
        asset.created_by = actor_id
        asset.updated_by = actor_id
        self.session.add(asset)
        await self.session.flush()
        if asset.current_user_id is not None:
            await self.session.refresh(asset, attribute_names=["current_user"])
        await AuditService(self.session).record(
            action=AuditAction.CREATE,
            entity="Asset",
            entity_id=asset.id,
            actor_id=actor_id,
            after=asset_snapshot(asset),
            context=audit_context,
        )
        return asset

    async def update(self, asset: Asset, payload: AssetUpdate, actor_id: UUID | None, audit_context: AuditContext | None = None) -> Asset:
        changes = payload.model_dump(exclude_unset=True)
        before = asset_snapshot(asset)
        for key, value in changes.items():
            setattr(asset, key, value)
        asset.updated_by = actor_id
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.UPDATE,
            entity="Asset",
            entity_id=asset.id,
            actor_id=actor_id,
            before=before,
            after=asset_snapshot(asset),
            context=audit_context,
        )
        return asset

    async def move(self, asset: Asset, payload: AssetMove, actor_id: UUID | None, audit_context: AuditContext | None = None) -> AssetMovement:
        before = asset_snapshot(asset)
        movement = AssetMovement(
            asset_id=asset.id,
            previous_user_id=asset.current_user_id,
            new_user_id=payload.new_user_id,
            previous_status=asset.status,
            new_status=payload.new_status,
            previous_location=asset.location,
            new_location=payload.new_location,
            responsible_id=actor_id,
            justification=payload.justification,
            notes=payload.notes,
            created_by=actor_id,
            updated_by=actor_id,
        )
        asset.current_user_id = payload.new_user_id
        asset.status = payload.new_status
        asset.location = payload.new_location
        asset.updated_by = actor_id
        self.session.add(movement)
        await self.session.flush()
        metrics.increment("itam_movement_operations_total", {"status": payload.new_status.value})
        await AuditService(self.session).record(
            action=AuditAction.MOVE,
            entity="Asset",
            entity_id=asset.id,
            actor_id=actor_id,
            before=before,
            after=asset_snapshot(asset),
            context=audit_context,
        )
        return movement

    async def soft_delete(self, asset: Asset, actor_id: UUID | None, audit_context: AuditContext | None = None) -> None:
        before = asset_snapshot(asset)
        asset.deleted_at = utc_now()
        asset.deleted_by = actor_id
        await AuditService(self.session).record(
            action=AuditAction.DELETE,
            entity="Asset",
            entity_id=asset.id,
            actor_id=actor_id,
            before=before,
            after=asset_snapshot(asset),
            context=audit_context,
        )
