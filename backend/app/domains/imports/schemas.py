from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ImportJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created_rows: int
    updated_rows: int
    skipped_rows: int
    conflict_rows: int
    failed_rows: int
    report: dict[str, Any]
    created_at: datetime


class ImportStagingAssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    row_number: int
    raw_payload: dict[str, Any]
    normalized_payload: dict[str, Any]
    identity_type: str | None
    identity_value: str | None
    identity_confidence: str | None = None
    decision: str
    row_status: str
    matched_asset_id: UUID | None
    merge_action: str | None
    issues: list[dict[str, Any]]


class ImportMappingUpdate(BaseModel):
    mapping: dict[str, str] = Field(default_factory=dict)
    import_mode: str | None = None


class ImportApplyResponse(BaseModel):
    job: ImportJobRead
    report: dict[str, Any]


class ImportPreview(BaseModel):
    job: ImportJobRead
    columns: list[str]
    detected_mapping: dict[str, str]
    items: list[ImportStagingAssetRead]


class ImportConflictRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    staging_asset_id: UUID | None
    conflict_type: str
    severity: str
    details: dict[str, Any]


class ImportValidationErrorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    staging_asset_id: UUID | None
    row_number: int | None
    field_name: str | None
    error_code: str
    message: str
