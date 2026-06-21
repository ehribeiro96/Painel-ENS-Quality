from __future__ import annotations

from uuid import UUID

from app.api.v1.dependencies.auth import get_current_user, require_role
from app.core.database.session import get_session
from app.domains.assets.models import Asset
from app.domains.assets.schemas import AssetCreate, AssetMove, AssetRead, AssetUpdate
from app.domains.assets.service import AssetService
from app.domains.macros.models import MacroGeneration
from app.domains.movements.models import AssetMovement
from app.domains.movements.schemas import MovementRead
from app.domains.users.models import User
from app.shared.audit_context import build_audit_context
from app.shared.enums import AssetStatus, AssetType, Role
from app.shared.pagination import Page, PageParams
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=Page[AssetRead])
async def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: str | None = None,
    status_filter: AssetStatus | None = Query(default=None, alias="status"),
    asset_type: AssetType | None = None,
    location: str | None = None,
    without_user: bool = False,
    sort_by: str = Query("updated_at", pattern="^(hostname|patrimony|serial|status|location|updated_at|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Page[Asset]:
    return await AssetService(session).list(
        PageParams(page=page, page_size=page_size),
        search,
        status_filter,
        asset_type,
        location,
        without_user,
        sort_by,
        sort_order,
    )


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> Asset:
    async def operation() -> Asset:
        return await AssetService(session).create(payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(asset_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> Asset:
    asset = await AssetService(session).get(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="asset_not_found")
    return asset


@router.put("/{asset_id}", response_model=AssetRead)
async def update_asset(
    asset_id: UUID,
    payload: AssetUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> Asset:
    service = AssetService(session)
    asset = await service.get(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="asset_not_found")
    async def operation() -> Asset:
        return await service.update(asset, payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, response_model=None)
async def delete_asset(
    asset_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
) -> None:
    service = AssetService(session)
    asset = await service.get(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="asset_not_found")
    async def operation() -> None:
        await service.soft_delete(asset, current_user.id, build_audit_context(request, current_user.id))

    await commit_or_rollback(session, operation)


@router.post("/{asset_id}/move", response_model=MovementRead)
async def move_asset(
    asset_id: UUID,
    payload: AssetMove,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> AssetMovement:
    service = AssetService(session)
    asset = await service.get_for_update(asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="asset_not_found")
    if payload.new_user_id is not None:
        target_user = await session.scalar(select(User).where(User.id == payload.new_user_id, User.deleted_at.is_(None)))
        if target_user is None:
            raise HTTPException(status_code=422, detail="target_user_not_found")

    async def operation() -> AssetMovement:
        return await service.move(asset, payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.get("/{asset_id}/history", response_model=list[MovementRead])
async def asset_history(asset_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> list[MovementRead]:
    result = await session.execute(select(AssetMovement).where(AssetMovement.asset_id == asset_id).order_by(AssetMovement.created_at.desc()))
    movements = list(result.scalars())
    if not movements:
        return []

    user_ids = {
        user_id
        for movement in movements
        for user_id in (movement.previous_user_id, movement.new_user_id, movement.responsible_id)
        if user_id is not None
    }
    users_by_id: dict[UUID, str] = {}
    if user_ids:
        users_result = await session.execute(select(User.id, User.name).where(User.id.in_(user_ids)))
        users_by_id = {user_id: name for user_id, name in users_result.all()}

    movement_ids = [movement.id for movement in movements]
    generations_result = await session.execute(
        select(MacroGeneration)
        .where(MacroGeneration.context_type == "asset_movement", MacroGeneration.context_id.in_(movement_ids))
        .order_by(MacroGeneration.created_at.desc())
    )
    generations_by_movement: dict[UUID, MacroGeneration] = {}
    for generation in generations_result.scalars():
        if generation.context_id is not None and generation.context_id not in generations_by_movement:
            generations_by_movement[generation.context_id] = generation

    asset = await session.scalar(select(Asset).where(Asset.id == asset_id))
    asset_label = None
    if asset is not None:
        asset_label = next((value for value in (asset.hostname, asset.patrimony, asset.serial) if value), None)

    items: list[MovementRead] = []
    for movement in movements:
        generation = generations_by_movement.get(movement.id)
        items.append(
            MovementRead.model_validate(movement).model_copy(
                update={
                    "previous_user_name": users_by_id.get(movement.previous_user_id) if movement.previous_user_id else None,
                    "new_user_name": users_by_id.get(movement.new_user_id) if movement.new_user_id else None,
                    "responsible_name": users_by_id.get(movement.responsible_id) if movement.responsible_id else None,
                    "asset_label": asset_label,
                    "macro_generation_id": generation.id if generation else None,
                    "macro_copied": generation.copied if generation else None,
                    "macro_copied_at": generation.copied_at if generation else None,
                }
            )
        )
    return items
