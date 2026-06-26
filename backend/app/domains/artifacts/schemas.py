from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    filename: str = Field(max_length=255)
    content_type: str = Field(max_length=120)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)
    created_at: datetime
    updated_at: datetime
    download_count: int = 0
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None


class ArtifactCreateResponse(ArtifactRead):
    pass


class ArtifactListResponse(BaseModel):
    items: list[ArtifactRead]
    total: int


class ArtifactDownloadUrlResponse(BaseModel):
    artifact_id: UUID
    url: str
    expires_at: datetime


class ArtifactDeleteResponse(BaseModel):
    ok: bool = True
    artifact_id: UUID
    deleted_at: datetime


class ArtifactError(BaseModel):
    code: str
    message: str
