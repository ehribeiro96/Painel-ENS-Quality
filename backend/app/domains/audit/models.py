from __future__ import annotations

import uuid
from typing import Any

from app.shared.enums import AuditAction
from app.shared.models import Base, EntityMixin
from sqlalchemy import Enum, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class AuditLog(EntityMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_actor_created_at", "actor_id", "created_at"),
        Index("ix_audit_logs_entity_created_at", "entity", "entity_id", "created_at"),
    )

    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    entity: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(String(80))
    request_id: Mapped[str | None] = mapped_column(String(120), index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(120), index=True)
    source: Mapped[str] = mapped_column(String(80), default="api", nullable=False, index=True)
