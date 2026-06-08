from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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


class AiChatConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=180)
    message: str | None = Field(default=None, min_length=1)
    mode: AiChatMode | None = None


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
