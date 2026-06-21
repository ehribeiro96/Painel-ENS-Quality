from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.api.v1.dependencies.auth import require_role
from app.core.database.session import get_session
from app.domains.audit.models import AuditLog
from app.domains.audit.schemas import AuditLogRead
from app.domains.users.models import User
from app.shared.enums import AuditAction, Role
from app.shared.pagination import Page, PageParams
from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


def build_audit_filters(
    *,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    action: AuditAction | None = None,
    user_id: UUID | None = None,
    source: str | None = None,
    correlation_id: str | None = None,
    request_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
) -> list:
    filters = []
    if entity_type:
        filters.append(AuditLog.entity == entity_type)
    if entity_id:
        filters.append(AuditLog.entity_id == entity_id)
    if action:
        filters.append(AuditLog.action == action)
    if user_id:
        filters.append(AuditLog.actor_id == user_id)
    if source:
        filters.append(AuditLog.source == source)
    if correlation_id:
        filters.append(AuditLog.correlation_id == correlation_id)
    if request_id:
        filters.append(AuditLog.request_id == request_id)
    if date_from:
        filters.append(AuditLog.created_at >= date_from)
    if date_to:
        filters.append(AuditLog.created_at <= date_to)
    if search:
        term = f"%{search.strip()}%"
        if search.strip():
            filters.append(
                or_(
                    AuditLog.entity.ilike(term),
                    AuditLog.source.ilike(term),
                    AuditLog.request_id.ilike(term),
                    AuditLog.correlation_id.ilike(term),
                    cast(AuditLog.entity_id, String).ilike(term),
                    cast(AuditLog.actor_id, String).ilike(term),
                )
            )
    return filters


@router.get("", response_model=Page[AuditLogRead])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    action: AuditAction | None = None,
    user_id: UUID | None = None,
    source: str | None = None,
    correlation_id: str | None = None,
    request_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(Role.ADMIN, Role.MANAGER)),
) -> Page[AuditLog]:
    params = PageParams(page=page, page_size=page_size)
    filters = build_audit_filters(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        source=source,
        correlation_id=correlation_id,
        request_id=request_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    total = await session.scalar(select(func.count()).select_from(AuditLog).where(*filters))
    result = await session.execute(
        select(AuditLog)
        .where(*filters)
        .order_by(AuditLog.created_at.desc())
        .offset(params.offset)
        .limit(params.page_size)
    )
    return Page(items=list(result.scalars()), total=total or 0, page=page, page_size=page_size)
