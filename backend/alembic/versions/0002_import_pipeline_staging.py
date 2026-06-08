"""add import pipeline staging tables

Revision ID: 0002_import_pipeline_staging
Revises: 0001_initial_itam
Create Date: 2026-05-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_import_pipeline_staging"
down_revision = "0001_initial_itam"
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
    op.add_column("import_jobs", sa.Column("created_rows", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("import_jobs", sa.Column("updated_rows", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("import_jobs", sa.Column("skipped_rows", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("import_jobs", sa.Column("conflict_rows", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("import_jobs", sa.Column("failed_rows", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "import_staging_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_jobs.id"), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column("normalized_payload", postgresql.JSONB(), nullable=False),
        sa.Column("identity_type", sa.String(40)),
        sa.Column("identity_value", sa.String(160)),
        sa.Column("decision", sa.String(40), nullable=False),
        sa.Column("row_status", sa.String(40), nullable=False, server_default="STAGED"),
        sa.Column("matched_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id")),
        sa.Column("merge_action", sa.String(40)),
        sa.Column("issues", postgresql.JSONB(), nullable=False, server_default="[]"),
        *audit_columns(),
    )
    op.create_index("ix_import_staging_assets_job_id", "import_staging_assets", ["job_id"])
    op.create_index("ix_import_staging_job_decision", "import_staging_assets", ["job_id", "decision"])
    op.create_index("ix_import_staging_identity", "import_staging_assets", ["identity_type", "identity_value"])
    op.create_index("ix_import_staging_assets_matched_asset_id", "import_staging_assets", ["matched_asset_id"])

    op.create_table(
        "import_conflicts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_jobs.id"), nullable=False),
        sa.Column("staging_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_staging_assets.id")),
        sa.Column("conflict_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default="{}"),
        *audit_columns(),
    )
    op.create_index("ix_import_conflicts_job_id", "import_conflicts", ["job_id"])
    op.create_index("ix_import_conflicts_staging_asset_id", "import_conflicts", ["staging_asset_id"])
    op.create_index("ix_import_conflicts_job_severity", "import_conflicts", ["job_id", "severity"])

    op.create_table(
        "import_validation_errors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_jobs.id"), nullable=False),
        sa.Column("staging_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_staging_assets.id")),
        sa.Column("row_number", sa.Integer()),
        sa.Column("field_name", sa.String(120)),
        sa.Column("error_code", sa.String(80), nullable=False),
        sa.Column("message", sa.String(500), nullable=False),
        *audit_columns(),
    )
    op.create_index("ix_import_validation_errors_job_id", "import_validation_errors", ["job_id"])
    op.create_index("ix_import_validation_errors_staging_asset_id", "import_validation_errors", ["staging_asset_id"])
    op.create_index("ix_import_validation_errors_error_code", "import_validation_errors", ["error_code"])


def downgrade() -> None:
    op.drop_table("import_validation_errors")
    op.drop_table("import_conflicts")
    op.drop_table("import_staging_assets")
    op.drop_column("import_jobs", "failed_rows")
    op.drop_column("import_jobs", "conflict_rows")
    op.drop_column("import_jobs", "skipped_rows")
    op.drop_column("import_jobs", "updated_rows")
    op.drop_column("import_jobs", "created_rows")
