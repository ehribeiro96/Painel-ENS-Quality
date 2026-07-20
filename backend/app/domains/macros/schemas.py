from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MacroTemplateBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str | None = Field(default=None, max_length=220)
    category: str = Field(default="Geral", max_length=80)
    description: str | None = Field(default=None, max_length=500)
    template_text: str = Field(min_length=1, max_length=10000)
    required_fields: list[str] = Field(default_factory=list)
    optional_fields: list[str] = Field(default_factory=list)
    context_type: str | None = Field(default=None, max_length=80)
    source: str = Field(default="api", max_length=80)
    version: str = Field(default="1", max_length=80)
    is_active: bool = True


class MacroTemplateCreate(MacroTemplateBase):
    pass


class MacroTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    template_text: str | None = Field(default=None, min_length=1, max_length=10000)
    required_fields: list[str] | None = None
    optional_fields: list[str] | None = None
    context_type: str | None = Field(default=None, max_length=80)
    version: str | None = Field(default=None, max_length=80)
    is_active: bool | None = None


class MacroTemplateRead(MacroTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime


class MacroRenderRequest(BaseModel):
    template_id: UUID | None = None
    template_text: str | None = Field(default=None, max_length=10000)
    values: dict[str, object] = Field(default_factory=dict)
    required_fields: list[str] | None = None


class MacroRenderResponse(BaseModel):
    rendered_text: str
    pending_fields: list[str] = Field(default_factory=list)


class MacroGenerateRequest(BaseModel):
    template_id: UUID
    values: dict[str, object] = Field(default_factory=dict)
    context_type: str | None = Field(default=None, max_length=80)
    context_id: UUID | None = None
    ticket_number: str | None = Field(default=None, max_length=80)


class MacroGenerationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    template_id: UUID
    context_type: str | None
    context_id: UUID | None
    rendered_text: str
    input_values: dict[str, object]
    generated_by: UUID | None
    ticket_number: str | None
    copied: bool
    copied_at: datetime | None
    created_at: datetime


class MacroAutocompleteHintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    label: str
    hint_type: str
    source: str


class SuggestedMovementMacro(BaseModel):
    movement_id: UUID
    generation_id: UUID | None = None
    template_id: UUID | None
    template_name: str | None
    rendered_text: str
    pending_fields: list[str]
    values: dict[str, object]


MacroPractice = Literal["incident", "service_request", "problem", "change", "access", "other"]
MacroLevel = Literal["low", "medium", "high", "unknown"]
MacroPriority = Literal["P1", "P2", "P3", "P4", "unknown"]


class ItilMacroGenerateRequest(BaseModel):
    practice: MacroPractice | Literal["automatic"] = "automatic"
    summary: str = Field(min_length=3, max_length=4000)
    configuration_item: str | None = Field(default=None, max_length=300)
    requester: str | None = Field(default=None, max_length=300)
    actions_taken: str | None = Field(default=None, max_length=4000)
    result: str | None = Field(default=None, max_length=4000)
    additional_information: str | None = Field(default=None, max_length=4000)


class ItilMacroOutput(BaseModel):
    practice: MacroPractice
    category: str | None = None
    subcategory: str | None = None
    service: str | None = None
    configuration_item: str | None = None
    impact: MacroLevel = "unknown"
    urgency: MacroLevel = "unknown"
    priority: MacroPriority = "unknown"
    title: str
    user_report: str | None = None
    diagnosis: str | None = None
    actions_taken: list[str] = Field(default_factory=list)
    result: str | None = None
    current_status: str | None = None
    resolution: str | None = None
    next_action: str | None = None
    closure_criteria: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    macro_text: str = Field(min_length=1, max_length=12000)
