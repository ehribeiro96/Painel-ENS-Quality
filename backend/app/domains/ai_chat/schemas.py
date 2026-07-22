from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

AiChatRole = Literal["system", "user", "assistant"]
AiChatMode = Literal[
    "general",
    "fix_text",
    "draft_ticket",
    "update_ticket",
    "resolution",
    "summarize",
    "improve_tone",
    "service_macro",
    "asset_guidance",
]
AiChatProviderId = Literal["mock", "ollama", "hermes"]
AiChatProviderStatus = Literal["online", "offline", "error", "unconfigured"]
AiChatResponseStatus = Literal["ok", "offline", "error", "unconfigured"]
AiChatAttachmentKind = Literal["text", "spreadsheet", "pdf", "image", "script", "log", "unknown"]


class AiChatConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=180)
    message: str | None = Field(default=None, min_length=1)
    mode: AiChatMode | None = None


class AiChatConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=180)


class AiChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)
    mode: AiChatMode | None = None


class AiChatConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str | None
    provider: str
    model: str | None
    system_prompt_version: str
    extra_metadata: dict[str, object] = Field(default_factory=dict, validation_alias="extra_metadata", serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime


class AiChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: AiChatRole
    content: str
    provider: str | None
    model: str | None
    extra_metadata: dict[str, object] = Field(default_factory=dict, validation_alias="extra_metadata", serialization_alias="metadata")
    created_at: datetime


class AiChatConversationDetail(AiChatConversationRead):
    messages: list[AiChatMessageRead] = Field(default_factory=list)


class ApoemaChatAttachment(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    size: int = Field(ge=0)
    kind: AiChatAttachmentKind = "unknown"
    sensitive: bool = False


class ApoemaChatContext(BaseModel):
    route: str = "apoema-chat"
    source: str = "apoema-preview"


class ApoemaChatMessageCreate(BaseModel):
    conversation_id: UUID | None = None
    provider: AiChatProviderId = "mock"
    model: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/+\-]*$")
    message: str = Field(min_length=1)
    mode: str = "assistente_n2"
    attachments: list[ApoemaChatAttachment] = Field(default_factory=list)
    context: ApoemaChatContext = Field(default_factory=ApoemaChatContext)

    @field_validator("model")
    @classmethod
    def reject_ambiguous_model_whitespace(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("ai_model_not_allowed")
        return value


class ApoemaChatUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class ApoemaChatMessageResponse(BaseModel):
    conversation_id: str
    message_id: str
    provider: AiChatProviderId
    model: str
    status: AiChatResponseStatus
    content: str
    created_at: datetime
    usage: ApoemaChatUsage = Field(default_factory=ApoemaChatUsage)
    error: str | None = None


class ApoemaChatProviderRead(BaseModel):
    id: AiChatProviderId
    label: str
    status: AiChatProviderStatus
    models: list[str] = Field(default_factory=list)
    default_model: str


class ApoemaChatProvidersResponse(BaseModel):
    providers: list[ApoemaChatProviderRead] = Field(default_factory=list)
