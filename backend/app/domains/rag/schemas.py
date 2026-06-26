
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RagCollectionId = Literal['courses', 'institutional', 'marketing', 'insights']


class RagCollectionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: RagCollectionId
    label: str
    description: str
    document_count: int = Field(ge=0)
    tool_names: list[str] = Field(default_factory=list)
    updated_at: datetime


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    collections: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1)


class RagDocumentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    collection: RagCollectionId
    title: str
    summary: str
    citation: str
    content: str
    tags: list[str] = Field(default_factory=list)
    updated_at: datetime


class RagSearchResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document: RagDocumentDTO
    score: int = Field(ge=0)
    matched_terms: list[str] = Field(default_factory=list)


class RagSearchResponse(BaseModel):
    query: str
    collections: list[RagCollectionId] = Field(default_factory=list)
    limit: int
    total: int
    items: list[RagSearchResultDTO] = Field(default_factory=list)


class RagCourseContextDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: str
    collection: RagCollectionId
    title: str
    summary: str
    audience: str
    key_documents: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    updated_at: datetime


class RagAuditEntryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    actor_role: str
    collection: RagCollectionId | None = None
    document_id: str | None = None
    course_id: str | None = None
    result: str
    occurred_at: datetime
    details: dict[str, object] = Field(default_factory=dict)


class RagAuditRecentResponse(BaseModel):
    items: list[RagAuditEntryDTO] = Field(default_factory=list)
    total: int


class RagError(BaseModel):
    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)
