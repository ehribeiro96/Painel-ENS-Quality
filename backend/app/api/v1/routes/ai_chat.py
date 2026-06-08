from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic
from uuid import UUID

from app.api.v1.dependencies.auth import require_role
from app.core.config.settings import settings
from app.core.database.session import get_session
from app.domains.ai_chat.providers import AiProviderConfigurationError, AiProviderRequestError, get_ai_provider_health
from app.domains.ai_chat.schemas import (
    AiChatConversationCreate,
    AiChatConversationDetail,
    AiChatConversationRead,
    AiChatMessageCreate,
)
from app.domains.ai_chat.service import AiChatService
from app.domains.users.models import User
from app.shared.enums import Role
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

ai_chat_user = Depends(require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER, Role.VIEWER))
_AI_CHAT_RATE_LIMIT: dict[str, deque[float]] = defaultdict(deque)


def _ensure_ai_chat_enabled() -> None:
    if not settings.enable_ai_chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ai_chat_disabled")


def _apply_rate_limit(user_id: UUID) -> None:
    limit = int(settings.ai_chat_rate_limit_per_minute or 0)
    if limit <= 0:
        return
    now = monotonic()
    window_start = now - 60
    bucket = _AI_CHAT_RATE_LIMIT[str(user_id)]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="ai_chat_rate_limit_exceeded")
    bucket.append(now)


def _provider_error_detail(prefix: str, exc: Exception) -> str:
    # Provider exceptions contain sanitized error codes only. Never include prompt bodies or API keys here.
    return f"{prefix}: {exc}"


@router.get("/health")
async def health(current_user: User = ai_chat_user) -> dict[str, object]:  # noqa: ARG001
    provider_health = get_ai_provider_health(settings)
    return {"enabled": settings.enable_ai_chat, **provider_health}


@router.get("/conversations", response_model=list[AiChatConversationRead])
async def list_conversations(
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    return await AiChatService(session).list_conversations(current_user.id)


@router.post("/conversations", response_model=AiChatConversationDetail, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: AiChatConversationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    if payload.message and len(payload.message) > settings.ai_max_input_chars:
        raise HTTPException(status_code=422, detail="ai_chat_input_too_large")
    if payload.message:
        _apply_rate_limit(current_user.id)
    service = AiChatService(session)

    async def operation():
        try:
            conversation = await service.create_conversation(payload, current_user.id)
        except AiProviderConfigurationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_provider_error_detail("ai_provider_configuration_error", exc),
            ) from exc
        except AiProviderRequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=_provider_error_detail("ai_provider_request_error", exc),
            ) from exc
        messages = await service.repository.list_messages(conversation.id)
        return service.to_detail(conversation, messages)

    return await commit_or_rollback(session, operation)


@router.get("/conversations/{conversation_id}", response_model=AiChatConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    service = AiChatService(session)
    conversation = await service.get_conversation(conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ai_chat_conversation_not_found")
    messages = await service.repository.list_messages(conversation.id)
    return service.to_detail(conversation, messages)


@router.post("/conversations/{conversation_id}/messages", response_model=AiChatConversationDetail)
async def send_message(
    conversation_id: UUID,
    payload: AiChatMessageCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    _apply_rate_limit(current_user.id)
    service = AiChatService(session)
    conversation = await service.get_conversation(conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ai_chat_conversation_not_found")

    async def operation():
        try:
            return await service.send_message(conversation, payload, current_user.id)
        except AiProviderConfigurationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_provider_error_detail("ai_provider_configuration_error", exc),
            ) from exc
        except AiProviderRequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=_provider_error_detail("ai_provider_request_error", exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return await commit_or_rollback(session, operation)
