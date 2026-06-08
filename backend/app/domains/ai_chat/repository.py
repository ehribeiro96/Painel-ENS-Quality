from __future__ import annotations

import uuid

from app.domains.ai_chat.models import AiChatConversation, AiChatMessage
from app.shared.models import utc_now
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class AiChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_conversations(self, user_id: uuid.UUID) -> list[AiChatConversation]:
        result = await self.session.execute(
            select(AiChatConversation)
            .where(AiChatConversation.user_id == user_id, AiChatConversation.deleted_at.is_(None))
            .order_by(AiChatConversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_conversation_for_user(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> AiChatConversation | None:
        return await self.session.scalar(
            select(AiChatConversation)
            .options(selectinload(AiChatConversation.messages))
            .where(
                AiChatConversation.id == conversation_id,
                AiChatConversation.user_id == user_id,
                AiChatConversation.deleted_at.is_(None),
            )
        )

    async def list_messages(self, conversation_id: uuid.UUID) -> list[AiChatMessage]:
        result = await self.session.execute(
            select(AiChatMessage)
            .where(AiChatMessage.conversation_id == conversation_id, AiChatMessage.deleted_at.is_(None))
            .order_by(AiChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_conversation(
        self,
        user_id: uuid.UUID,
        title: str | None,
        provider: str,
        model: str | None,
    ) -> AiChatConversation:
        conversation = AiChatConversation(
            user_id=user_id,
            title=title,
            provider=provider,
            model=model,
            created_by=user_id,
            updated_by=user_id,
            extra_metadata={},
        )
        if conversation.created_at is None:
            conversation.created_at = utc_now()
        if conversation.updated_at is None:
            conversation.updated_at = conversation.created_at
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def create_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        user_id: uuid.UUID,
        provider: str | None = None,
        model: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        extra_metadata: dict[str, object] | None = None,
    ) -> AiChatMessage:
        message = AiChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            created_by=user_id,
            updated_by=user_id,
            extra_metadata=extra_metadata or {},
        )
        if message.created_at is None:
            message.created_at = utc_now()
        if message.updated_at is None:
            message.updated_at = message.created_at
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def update_message_metadata(self, message: AiChatMessage, extra_metadata: dict[str, object]) -> AiChatMessage:
        message.extra_metadata = extra_metadata
        message.updated_at = utc_now()
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
