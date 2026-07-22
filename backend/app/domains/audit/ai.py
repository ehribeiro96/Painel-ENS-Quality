from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import UUID

from app.core.database.session import AsyncSessionLocal
from app.domains.audit.models import AuditLog
from app.domains.audit.service import AuditService
from app.shared.enums import AuditAction
from sqlalchemy.ext.asyncio import AsyncSession

AiAuditEvent = Literal[
    "CHAT_MESSAGE",
    "CHAT_CONVERSATION",
    "MACRO_GENERATION",
    "IMPORT_ANALYSIS",
    "AI_PROVIDER_CALL",
    "AI_APPROVAL",
    "AI_REJECTION",
]
AiAuditStatus = Literal["SUCCESS", "FAILED", "DENIED"]
_SAFE_ERROR_CODE = re.compile(r"^[a-z][a-z0-9_-]{2,79}$")
_SAFE_PROVIDER = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
_SAFE_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+\-]{0,127}$")
_SAFE_RESOURCE_TYPE = re.compile(r"^[A-Z][A-Za-z0-9]{0,63}$")


class AiAuditUser(Protocol):
    id: UUID
    role: object


@dataclass
class AiAuditActor:
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
    if not _SAFE_PROVIDER.fullmatch(provider) or (model is not None and not _SAFE_MODEL.fullmatch(model)):
        raise ValueError("invalid_ai_audit_identifier")
    if not _SAFE_RESOURCE_TYPE.fullmatch(resource_type):
        raise ValueError("invalid_ai_audit_identifier")
    try:
        canonical_resource_id = resource_id if isinstance(resource_id, UUID) else UUID(resource_id) if resource_id else None
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("invalid_ai_audit_identifier") from exc
    timestamp = datetime.now(UTC)
    return await AuditService(session).record(
        action=AuditAction.CREATE,
        entity="AiAuditEvent",
        entity_id=canonical_resource_id,
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
            "resource_id": str(canonical_resource_id) if canonical_resource_id is not None else None,
            "status": status,
            "duration_ms": max(0, duration_ms),
            "error": sanitize_ai_error(error),
        },
    )


async def record_ai_operation_audits(
    session: AsyncSession,
    *,
    event: Literal["CHAT_MESSAGE", "CHAT_CONVERSATION", "MACRO_GENERATION", "IMPORT_ANALYSIS"],
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


async def persist_failed_ai_operation_audits(
    *,
    event: Literal["CHAT_MESSAGE", "CHAT_CONVERSATION", "MACRO_GENERATION", "IMPORT_ANALYSIS"],
    user_id: UUID,
    user_role: object,
    provider: str,
    model: str | None,
    resource_type: str,
    resource_id: UUID | str | None,
    duration_ms: int,
    error: Exception | str,
) -> bool:
    """Persist FAILED audits outside the rolled-back request transaction."""
    try:
        async with AsyncSessionLocal() as session:
            try:
                await record_ai_operation_audits(
                    session,
                    event=event,
                    user=AiAuditActor(user_id, user_role),
                    provider=provider,
                    model=model,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status="FAILED",
                    duration_ms=duration_ms,
                    error=error,
                )
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise
    except Exception:
        logging.getLogger(__name__).error(
            "ai_failure_audit_persistence_failed",
            extra={"event": event, "resource_type": resource_type, "resource_id": str(resource_id) if resource_id else None},
        )
        return False
