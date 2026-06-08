"""ai chat

Revision ID: 0006_ai_chat
Revises: 0005_macros_module
Create Date: 2026-06-03
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_ai_chat"
down_revision = "0005_macros_module"
branch_labels = None
depends_on = None


def audit_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "ai_chat_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(180), nullable=True),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("system_prompt_version", sa.String(40), nullable=False, server_default="mvp-1"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        *audit_columns(),
    )
    op.create_index("ix_ai_chat_conversations_user_created", "ai_chat_conversations", ["user_id", "created_at"])
    op.create_index("ix_ai_chat_conversations_deleted_at", "ai_chat_conversations", ["deleted_at"])

    op.create_table(
        "ai_chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_chat_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(40), nullable=True),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        *audit_columns(),
        sa.CheckConstraint("role in ('system', 'user', 'assistant')", name="ck_ai_chat_messages_role"),
    )
    op.create_index("ix_ai_chat_messages_conversation_created", "ai_chat_messages", ["conversation_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_chat_messages_conversation_created", table_name="ai_chat_messages")
    op.drop_table("ai_chat_messages")
    op.drop_index("ix_ai_chat_conversations_deleted_at", table_name="ai_chat_conversations")
    op.drop_index("ix_ai_chat_conversations_user_created", table_name="ai_chat_conversations")
    op.drop_table("ai_chat_conversations")
