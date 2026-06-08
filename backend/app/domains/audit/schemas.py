from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.shared.enums import AuditAction
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: UUID | None
    action: AuditAction
    entity: str
    entity_id: UUID | None
    before: dict[str, Any] | None
    after: dict[str, Any] | None
    ip_address: str | None
    request_id: str | None
    correlation_id: str | None
    source: str
    created_at: datetime
