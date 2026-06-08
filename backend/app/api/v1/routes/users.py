from __future__ import annotations

from uuid import UUID

from app.api.v1.dependencies.auth import get_current_user, require_role
from app.core.database.session import get_session
from app.domains.assets.models import Asset
from app.domains.assets.schemas import AssetRead
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate, UserRead, UserUpdate
from app.domains.users.service import UserService
from app.shared.audit_context import build_audit_context
from app.shared.enums import Role
from app.shared.pagination import Page, PageParams
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=Page[UserRead])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Page[User]:
    return await UserService(session).list(PageParams(page=page, page_size=page_size), search)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> User:
    if current_user.role != Role.ADMIN and payload.role != Role.VIEWER:
        raise HTTPException(status_code=403, detail="role_assignment_requires_admin")

    async def operation() -> User:
        return await UserService(session).create(payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, response_model=None)
async def delete_user(
    user_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
) -> None:
    if user_id == current_user.id:
        raise HTTPException(status_code=422, detail="cannot_delete_current_user")
    service = UserService(session)
    user = await service.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")

    async def operation() -> None:
        await service.soft_delete(user, current_user.id, build_audit_context(request, current_user.id))

    await commit_or_rollback(session, operation)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> User:
    user = await UserService(session).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> User:
    service = UserService(session)
    user = await service.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    async def operation() -> User:
        return await service.update(user, payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.get("/{user_id}/assets", response_model=list[AssetRead])
async def user_assets(user_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> list[Asset]:
    result = await session.execute(
        select(Asset)
        .options(selectinload(Asset.current_user))
        .where(Asset.current_user_id == user_id, Asset.deleted_at.is_(None))
        .order_by(Asset.hostname)
    )
    return list(result.scalars())
