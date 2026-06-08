"""macros module

Revision ID: 0005_macros_module
Revises: 0004_user_source_metadata
Create Date: 2026-06-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_macros_module"
down_revision = "0004_user_source_metadata"
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
        "macro_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("slug", sa.String(220), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column("required_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("optional_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("context_type", sa.String(80), nullable=True),
        sa.Column("source", sa.String(80), nullable=False),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *audit_columns(),
    )
    op.create_index("ix_macro_templates_slug", "macro_templates", ["slug"], unique=True)
    op.create_index("ix_macro_templates_category", "macro_templates", ["category"])
    op.create_index("ix_macro_templates_active", "macro_templates", ["is_active"])

    op.create_table(
        "macro_generations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("macro_templates.id"), nullable=False),
        sa.Column("context_type", sa.String(80), nullable=True),
        sa.Column("context_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rendered_text", sa.Text(), nullable=False),
        sa.Column("input_values", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("ticket_number", sa.String(80), nullable=True),
        sa.Column("copied", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("copied_at", sa.DateTime(timezone=True), nullable=True),
        *audit_columns(),
    )
    op.create_index("ix_macro_generations_template_created", "macro_generations", ["template_id", "created_at"])
    op.create_index("ix_macro_generations_context", "macro_generations", ["context_type", "context_id"])

    op.create_table(
        "macro_autocomplete_hints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("label", sa.String(180), nullable=False),
        sa.Column("normalized_label", sa.String(180), nullable=False),
        sa.Column("hint_type", sa.String(80), nullable=False),
        sa.Column("source", sa.String(80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_macro_hints_lookup", "macro_autocomplete_hints", ["hint_type", "normalized_label"])
    op.create_index("ix_macro_hints_unique", "macro_autocomplete_hints", ["hint_type", "source", "normalized_label"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_macro_hints_unique", table_name="macro_autocomplete_hints")
    op.drop_index("ix_macro_hints_lookup", table_name="macro_autocomplete_hints")
    op.drop_table("macro_autocomplete_hints")
    op.drop_index("ix_macro_generations_context", table_name="macro_generations")
    op.drop_index("ix_macro_generations_template_created", table_name="macro_generations")
    op.drop_table("macro_generations")
    op.drop_index("ix_macro_templates_active", table_name="macro_templates")
    op.drop_index("ix_macro_templates_category", table_name="macro_templates")
    op.drop_index("ix_macro_templates_slug", table_name="macro_templates")
    op.drop_table("macro_templates")
