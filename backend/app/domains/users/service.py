from __future__ import annotations

from uuid import UUID

from app.core.security.passwords import hash_password
from app.domains.audit.service import AuditService
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate, UserUpdate
from app.shared.audit_context import AuditContext
from app.shared.enums import AuditAction
from app.shared.models import utc_now
from app.shared.pagination import Page, PageParams
from app.shared.snapshots import user_snapshot
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, params: PageParams, search: str | None = None) -> Page[User]:
        filters = [User.deleted_at.is_(None)]
        if search:
            term = f"%{search}%"
            filters.append(or_(User.name.ilike(term), User.email.ilike(term), User.department.ilike(term)))
        total = await self.session.scalar(select(func.count()).select_from(User).where(*filters))
        result = await self.session.execute(
            select(User).where(*filters).order_by(User.name).offset(params.offset).limit(params.page_size)
        )
        return Page(items=list(result.scalars()), total=total or 0, page=params.page, page_size=params.page_size)

    async def get(self, user_id: UUID) -> User | None:
        return await self.session.scalar(select(User).where(User.id == user_id, User.deleted_at.is_(None)))

    async def create(self, payload: UserCreate, actor_id: UUID | None, audit_context: AuditContext | None = None) -> User:
        data = payload.model_dump(exclude={"password"})
        data["source"] = data.get("source") or "manual"
        user = User(**data, password_hash=hash_password(payload.password) if payload.password else None)
        user.created_by = actor_id
        user.updated_by = actor_id
        self.session.add(user)
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.CREATE,
            entity="User",
            entity_id=user.id,
            actor_id=actor_id,
            after=user_snapshot(user),
            context=audit_context,
        )
        return user

    async def update(self, user: User, payload: UserUpdate, actor_id: UUID | None, audit_context: AuditContext | None = None) -> User:
        before = user_snapshot(user)
        changes = payload.model_dump(exclude_unset=True)
        if user.source and user.source != "manual" and changes.get("source") == "manual":
            changes.pop("source")
        changes = {key: value for key, value in changes.items() if value != ""}
        for key, value in changes.items():
            setattr(user, key, value)
        user.updated_by = actor_id
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.UPDATE,
            entity="User",
            entity_id=user.id,
            actor_id=actor_id,
            before=before,
            after=user_snapshot(user),
            context=audit_context,
        )
        return user

    async def soft_delete(self, user: User, actor_id: UUID | None, audit_context: AuditContext | None = None) -> None:
        before = user_snapshot(user)
        user.deleted_at = utc_now()
        user.deleted_by = actor_id
        await AuditService(self.session).record(
            action=AuditAction.DELETE,
            entity="User",
            entity_id=user.id,
            actor_id=actor_id,
            before=before,
            after=user_snapshot(user),
            context=audit_context,
        )
