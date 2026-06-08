"""add user source metadata

Revision ID: 0004_user_source_metadata
Revises: 0003_startup_auth_obs
Create Date: 2026-06-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_user_source_metadata"
down_revision = "0003_startup_auth_obs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("source", sa.String(80), nullable=True))
    op.add_column("users", sa.Column("source_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "source_metadata")
    op.drop_column("users", "source")
