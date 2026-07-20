"""enforce one macro generation per asset movement

Revision ID: 0007_macro_movement_unique
Revises: 0006_ai_chat
Create Date: 2026-07-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_macro_movement_unique"
down_revision = "0006_ai_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_macro_generations_asset_movement",
        "macro_generations",
        ["context_type", "context_id"],
        unique=True,
        postgresql_where=sa.text("context_type = 'asset_movement' AND context_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_macro_generations_asset_movement", table_name="macro_generations")
