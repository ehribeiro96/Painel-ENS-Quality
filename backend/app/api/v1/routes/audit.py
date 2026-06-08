from __future__ import annotations

from app.api.v1.dependencies.auth import require_role
from app.core.database.session import get_session
from app.domains.audit.models import AuditLog
from app.domains.audit.schemas import AuditLogRead
from app.domains.users.models import User
from app.shared.enums import Role
from app.shared.pagination import Page, PageParams
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("", response_model=Page[AuditLogRead])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(Role.ADMIN, Role.MANAGER)),
) -> Page[AuditLog]:
    params = PageParams(page=page, page_size=page_size)
    total = await session.scalar(select(func.count()).select_from(AuditLog))
    result = await session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(params.offset).limit(params.page_size))
    return Page(items=list(result.scalars()), total=total or 0, page=page, page_size=page_size)
