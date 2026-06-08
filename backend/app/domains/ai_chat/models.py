from __future__ import annotations

import uuid
from typing import Any

from app.shared.models import Base, EntityMixin
from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AiChatConversation(EntityMixin, Base):
    __tablename__ = "ai_chat_conversations"
    __table_args__ = (
        Index("ix_ai_chat_conversations_user_created", "user_id", "created_at"),
        Index("ix_ai_chat_conversations_deleted_at", "deleted_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(180))
    provider: Mapped[str] = mapped_column(String(40), default="mock", nullable=False)
    model: Mapped[str | None] = mapped_column(String(120))
    system_prompt_version: Mapped[str] = mapped_column(String(40), default="mvp-1", nullable=False)
    extra_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    messages = relationship(
        "AiChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AiChatMessage.created_at",
        lazy="selectin",
    )


class AiChatMessage(EntityMixin, Base):
    __tablename__ = "ai_chat_messages"
    __table_args__ = (
        Index("ix_ai_chat_messages_conversation_created", "conversation_id", "created_at"),
        CheckConstraint("role in ('system', 'user', 'assistant')", name="ck_ai_chat_messages_role"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_chat_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(40))
    model: Mapped[str | None] = mapped_column(String(120))
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    conversation = relationship("AiChatConversation", back_populates="messages")
