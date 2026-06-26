from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_PROMPT_LENGTH = 2000
MAX_COPY_LENGTH = 2000
MAX_ITEMS_PER_JOB = 12

ALLOWED_TEMPLATES = (
    '01_feed_instagram',
    '02_story_instagram',
    '03_banner_interno_desktop',
    '04_banner_interno_mobile',
    '05_AIDA_whatsapp',
    '05_whatsapp',
    '08_topo_email',
)
ALLOWED_CHANNELS = ALLOWED_TEMPLATES
ALLOWED_KVS = (
    'graduacao',
    'imersoes',
    'institucional',
    'pos',
    'qualificacoes',
    'tudo-sobre-seguros',
)
ALLOWED_MODES = ('peca_unica', 'enxoval')
ALLOWED_STATUSES = ('queued', 'running', 'completed', 'failed', 'cancelled', 'expired')
ALLOWED_ITEM_STATUSES = ('queued', 'running', 'completed', 'failed', 'cancelled')

DesignerJobStatus = Literal['queued', 'running', 'completed', 'failed', 'cancelled', 'expired']
DesignerJobItemStatus = Literal['queued', 'running', 'completed', 'failed', 'cancelled']
DesignerMode = Literal['peca_unica', 'enxoval']


class DesignerError(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class DesignerHealthDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    service: str
    mode: str
    deterministic: bool
    provider_real_enabled: bool
    template_count: int = Field(ge=0)
    job_count: int = Field(ge=0)
    note: str


class DesignerTemplateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    template_id: str
    canal: str
    kv: str
    label: str
    description: str
    mode_options: list[DesignerMode] = Field(default_factory=list)
    box2_allowed: bool = True
    persona_image_allowed: bool = True
    prompt_budget: int = Field(default=MAX_PROMPT_LENGTH, ge=1)
    copy_budget: int = Field(default=MAX_COPY_LENGTH, ge=1)


class DesignerTemplatesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[DesignerTemplateDTO] = Field(default_factory=list)
    total: int = Field(ge=0)


class DesignerFormOptionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channels: list[str] = Field(default_factory=list)
    kvs: list[str] = Field(default_factory=list)
    modes: list[DesignerMode] = Field(default_factory=list)
    template_ids: list[str] = Field(default_factory=list)
    supports_box2: bool = True
    supports_persona_image: bool = True
    max_prompt_length: int = Field(default=MAX_PROMPT_LENGTH, ge=1)
    max_copy_length: int = Field(default=MAX_COPY_LENGTH, ge=1)
    max_items_per_job: int = Field(default=MAX_ITEMS_PER_JOB, ge=1)


class DesignerBannerJsonRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    template_id: str = Field(min_length=1)
    canal: str = Field(min_length=1)
    kv: str = Field(min_length=1)
    modo_geracao: DesignerMode
    prompt: str = Field(min_length=1)
    copy_text: str | None = Field(default=None, alias='copy')
    box2: str | None = None
    persona_image: str | None = None
    item_count: int = Field(default=1, ge=1, le=MAX_ITEMS_PER_JOB)

    @field_validator('template_id', 'canal', 'kv', 'modo_geracao')
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator('prompt', 'copy_text', 'box2', 'persona_image')
    @classmethod
    def _strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DesignerAdjustItemRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    adjustment_prompt: str = Field(min_length=1)
    copy_text: str | None = Field(default=None, alias='copy')
    box2: str | None = None

    @field_validator('adjustment_prompt', 'copy_text', 'box2')
    @classmethod
    def _strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DesignerRefreshUrlRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reason: str | None = None

    @field_validator('reason')
    @classmethod
    def _strip_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DesignerJobItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: str
    template_id: str
    title: str
    status: DesignerJobItemStatus
    copy_preview: str
    prompt_preview: str
    result_note: str
    adjusted_count: int = Field(default=0, ge=0)
    refresh_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime
    error: DesignerError | None = None


class DesignerJobDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    owner_user_id: str
    status: DesignerJobStatus
    created_at: datetime
    updated_at: datetime
    template_id: str
    canal: str
    kv: str
    modo_geracao: DesignerMode
    box2: str | None = None
    persona_image_present: bool = False
    prompt_preview: str
    copy_preview: str
    progress: float = Field(ge=0.0, le=100.0)
    items: list[DesignerJobItemDTO] = Field(default_factory=list)
    summary: str
    error: DesignerError | None = None


class DesignerCancelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: DesignerJobStatus
    cancelled_at: datetime
    items_cancelled: int = Field(ge=0)
    message: str
