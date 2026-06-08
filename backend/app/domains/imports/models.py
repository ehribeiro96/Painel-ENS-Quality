from __future__ import annotations

import uuid
from typing import Any

from app.shared.models import Base, EntityMixin
from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ImportJob(EntityMixin, Base):
    __tablename__ = "import_jobs"

    source: Mapped[str] = mapped_column(String(80), default="LANSWEEPER", nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(260), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="RECEIVED", nullable=False, index=True)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conflict_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    report: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    staging_assets = relationship("ImportStagingAsset", back_populates="job", cascade="all, delete-orphan")
    conflicts = relationship("ImportConflict", back_populates="job", cascade="all, delete-orphan")
    validation_errors = relationship("ImportValidationError", back_populates="job", cascade="all, delete-orphan")


class ImportStagingAsset(EntityMixin, Base):
    __tablename__ = "import_staging_assets"
    __table_args__ = (
        Index("ix_import_staging_job_decision", "job_id", "decision"),
        Index("ix_import_staging_identity", "identity_type", "identity_value"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("import_jobs.id"), nullable=False, index=True)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    normalized_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    identity_type: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    identity_value: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    decision: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    row_status: Mapped[str] = mapped_column(String(40), default="STAGED", nullable=False, index=True)
    matched_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True, index=True)
    merge_action: Mapped[str | None] = mapped_column(String(40), nullable=True)
    issues: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)

    job = relationship("ImportJob", back_populates="staging_assets")

    @property
    def identity_confidence(self) -> str | None:
        return self.normalized_payload.get("identity_confidence")


class ImportConflict(EntityMixin, Base):
    __tablename__ = "import_conflicts"
    __table_args__ = (
        Index("ix_import_conflicts_job_severity", "job_id", "severity"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("import_jobs.id"), nullable=False, index=True)
    staging_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("import_staging_assets.id"), nullable=True, index=True)
    conflict_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    job = relationship("ImportJob", back_populates="conflicts")


class ImportValidationError(EntityMixin, Base):
    __tablename__ = "import_validation_errors"

    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("import_jobs.id"), nullable=False, index=True)
    staging_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("import_staging_assets.id"), nullable=True, index=True)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    field_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    job = relationship("ImportJob", back_populates="validation_errors")
