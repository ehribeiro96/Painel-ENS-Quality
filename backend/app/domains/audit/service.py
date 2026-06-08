from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domains.audit.models import AuditLog
from app.shared.audit_context import AuditContext
from app.shared.enums import AuditAction
from sqlalchemy.ext.asyncio import AsyncSession


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        *,
        action: AuditAction,
        entity: str,
        entity_id: UUID | None,
        actor_id: UUID | None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        ip_address: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        source: str = "api",
        context: AuditContext | None = None,
    ) -> AuditLog:
        if context is not None:
            actor_id = actor_id or context.actor_id
            ip_address = ip_address or context.ip_address
            request_id = request_id or context.request_id
            correlation_id = correlation_id or context.correlation_id
            source = context.source

        log = AuditLog(
            action=action,
            entity=entity,
            entity_id=entity_id,
            actor_id=actor_id,
            before=before,
            after=after,
            ip_address=ip_address,
            request_id=request_id,
            correlation_id=correlation_id,
            source=source,
            created_by=actor_id,
            updated_by=actor_id,
        )
        self.session.add(log)
        return log
