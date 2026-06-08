from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from app.shared.models import Base, EntityMixin, utc_now
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class MacroTemplate(EntityMixin, Base):
    __tablename__ = "macro_templates"
    __table_args__ = (
        Index("ix_macro_templates_slug", "slug", unique=True),
        Index("ix_macro_templates_category", "category"),
        Index("ix_macro_templates_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    required_fields: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    optional_fields: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    context_type: Mapped[str | None] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(80), default="api", nullable=False)
    version: Mapped[str] = mapped_column(String(80), default="1", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    generations = relationship("MacroGeneration", back_populates="template")


class MacroGeneration(EntityMixin, Base):
    __tablename__ = "macro_generations"
    __table_args__ = (
        Index("ix_macro_generations_template_created", "template_id", "created_at"),
        Index("ix_macro_generations_context", "context_type", "context_id"),
    )

    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("macro_templates.id"), nullable=False)
    context_type: Mapped[str | None] = mapped_column(String(80))
    context_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    rendered_text: Mapped[str] = mapped_column(Text, nullable=False)
    input_values: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    ticket_number: Mapped[str | None] = mapped_column(String(80))
    copied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    copied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    template = relationship("MacroTemplate", back_populates="generations")


class MacroAutocompleteHint(Base):
    __tablename__ = "macro_autocomplete_hints"
    __table_args__ = (
        Index("ix_macro_hints_lookup", "hint_type", "normalized_label"),
        Index("ix_macro_hints_unique", "hint_type", "source", "normalized_label", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(180), nullable=False)
    normalized_label: Mapped[str] = mapped_column(String(180), nullable=False)
    hint_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
