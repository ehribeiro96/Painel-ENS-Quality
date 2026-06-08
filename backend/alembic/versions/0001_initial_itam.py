"""initial itam schema

Revision ID: 0001_initial_itam
Revises:
Create Date: 2026-05-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial_itam"
down_revision = None
branch_labels = None
depends_on = None

asset_status = postgresql.ENUM(
    "IN_USE", "STOCK", "MAINTENANCE", "DEFECTIVE", "DISCARDED", "RESERVED", "CONFIG_PENDING", name="assetstatus", create_type=False
)
asset_type = postgresql.ENUM(
    "NOTEBOOK", "DESKTOP", "MONITOR", "DOCK", "MOBILE", "PRINTER", "PERIPHERAL", "OTHER", name="assettype", create_type=False
)
user_status = postgresql.ENUM("ACTIVE", "INACTIVE", "ON_LEAVE", name="userstatus", create_type=False)
role = postgresql.ENUM("ADMIN", "TECHNICIAN", "VIEWER", "MANAGER", name="role", create_type=False)
audit_action = postgresql.ENUM(
    "LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE", "MOVE", "IMPORT", "SIGNATURE_GENERATE", "STATUS_CHANGE", name="auditaction", create_type=False
)


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
    bind = op.get_bind()
    for enum in (asset_status, asset_type, user_status, role, audit_action):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("job_title", sa.String(160)),
        sa.Column("department", sa.String(160)),
        sa.Column("business_unit", sa.String(160)),
        sa.Column("manager_name", sa.String(160)),
        sa.Column("phone", sa.String(80)),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("status", user_status, nullable=False),
        sa.Column("role", role, nullable=False),
        *audit_columns(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_name", "users", ["name"])

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("hostname", sa.String(120)),
        sa.Column("patrimony", sa.String(120)),
        sa.Column("serial", sa.String(160)),
        sa.Column("manufacturer", sa.String(160)),
        sa.Column("model", sa.String(160)),
        sa.Column("asset_type", asset_type, nullable=False),
        sa.Column("status", asset_status, nullable=False),
        sa.Column("location", sa.String(160)),
        sa.Column("operating_system", sa.String(160)),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("last_login", sa.String(160)),
        sa.Column("notes", sa.Text()),
        sa.Column("current_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        *audit_columns(),
    )
    op.create_index("ix_assets_identity", "assets", ["serial", "patrimony", "hostname"])
    op.create_index("ix_assets_status_type", "assets", ["status", "asset_type"])
    op.create_index("ix_assets_patrimony", "assets", ["patrimony"], unique=True)
    op.create_index("ix_assets_serial", "assets", ["serial"], unique=True)

    op.create_table(
        "asset_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("previous_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("new_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("previous_status", asset_status, nullable=False),
        sa.Column("new_status", asset_status, nullable=False),
        sa.Column("previous_location", sa.String(160)),
        sa.Column("new_location", sa.String(160)),
        sa.Column("responsible_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("justification", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text()),
        *audit_columns(),
    )
    op.create_index("ix_asset_movements_asset_id", "asset_movements", ["asset_id"])
    op.create_index("ix_asset_movements_asset_created_at", "asset_movements", ["asset_id", "created_at"])
    op.create_index("ix_asset_movements_responsible_created_at", "asset_movements", ["responsible_id", "created_at"])

    op.create_table(
        "import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(80), nullable=False),
        sa.Column("filename", sa.String(260), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("valid_rows", sa.Integer(), nullable=False),
        sa.Column("invalid_rows", sa.Integer(), nullable=False),
        sa.Column("report", postgresql.JSONB(), nullable=False),
        *audit_columns(),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action", audit_action, nullable=False),
        sa.Column("entity", sa.String(120), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("before", postgresql.JSONB()),
        sa.Column("after", postgresql.JSONB()),
        sa.Column("ip_address", sa.String(80)),
        sa.Column("request_id", sa.String(120)),
        sa.Column("correlation_id", sa.String(120)),
        sa.Column("source", sa.String(80), nullable=False, server_default="api"),
        *audit_columns(),
    )
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity"])
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])
    op.create_index("ix_audit_logs_correlation_id", "audit_logs", ["correlation_id"])
    op.create_index("ix_audit_logs_actor_created_at", "audit_logs", ["actor_id", "created_at"])
    op.create_index("ix_audit_logs_entity_created_at", "audit_logs", ["entity", "entity_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("import_jobs")
    op.drop_table("asset_movements")
    op.drop_table("assets")
    op.drop_table("users")
    bind = op.get_bind()
    for enum in (audit_action, role, user_status, asset_type, asset_status):
        enum.drop(bind, checkfirst=True)
