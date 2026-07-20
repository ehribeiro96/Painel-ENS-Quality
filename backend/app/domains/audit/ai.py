from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import UUID

from app.domains.audit.models import AuditLog
from app.domains.audit.service import AuditService
from app.shared.enums import AuditAction
from sqlalchemy.ext.asyncio import AsyncSession

AiAuditEvent = Literal[
    "CHAT_MESSAGE",
    "MACRO_GENERATION",
    "IMPORT_ANALYSIS",
    "AI_PROVIDER_CALL",
    "AI_APPROVAL",
    "AI_REJECTION",
]
AiAuditStatus = Literal["SUCCESS", "FAILED"]
_SAFE_ERROR_CODE = re.compile(r"^[a-z][a-z0-9_-]{2,79}$")


class AiAuditUser(Protocol):
    id: UUID
    role: object


def sanitize_ai_error(error: Exception | str | None) -> str | None:
    if error is None:
        return None
    code = str(error).strip().split(":", 1)[0]
    return code if _SAFE_ERROR_CODE.fullmatch(code) else "ai_operation_failed"


async def record_ai_audit(
    session: AsyncSession,
    *,
    event: AiAuditEvent,
    user: AiAuditUser,
    provider: str,
    model: str | None,
    resource_type: str,
    resource_id: UUID | str | None,
    status: AiAuditStatus,
    duration_ms: int,
    error: Exception | str | None = None,
) -> AuditLog:
    timestamp = datetime.now(UTC)
    return await AuditService(session).record(
        action=AuditAction.CREATE,
        entity="AiAuditEvent",
        entity_id=resource_id if isinstance(resource_id, UUID) else None,
        actor_id=user.id,
        source="ai-governance",
        after={
            "event": event,
            "user_id": str(user.id),
            "role": str(getattr(user.role, "value", user.role)),
            "timestamp": timestamp.isoformat(),
            "action": event,
            "provider": provider,
            "model": model,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id is not None else None,
            "status": status,
            "duration_ms": max(0, duration_ms),
            "error": sanitize_ai_error(error),
        },
    )


async def record_ai_operation_audits(
    session: AsyncSession,
    *,
    event: Literal["CHAT_MESSAGE", "MACRO_GENERATION", "IMPORT_ANALYSIS"],
    user: AiAuditUser,
    provider: str,
    model: str | None,
    resource_type: str,
    resource_id: UUID | str | None,
    status: AiAuditStatus,
    duration_ms: int,
    error: Exception | str | None = None,
) -> tuple[AuditLog, AuditLog]:
    common = {
        "user": user,
        "provider": provider,
        "model": model,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "status": status,
        "duration_ms": duration_ms,
        "error": error,
    }
    provider_event = await record_ai_audit(session, event="AI_PROVIDER_CALL", **common)
    domain_event = await record_ai_audit(session, event=event, **common)
    return provider_event, domain_event
