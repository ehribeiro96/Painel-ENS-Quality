from __future__ import annotations

import time
from uuid import UUID

from app.api.v1.dependencies.auth import require_ai_capability
from app.core.config.settings import settings
from app.core.database.session import get_session
from app.core.permissions.ai import ensure_ai_enabled
from app.domains.ai_chat.apoema import build_apoema_provider_catalog, generate_apoema_message
from app.domains.ai_chat.providers import AiProviderConfigurationError, AiProviderRequestError, get_ai_provider_health
from app.domains.ai_chat.rate_limit import get_ai_chat_rate_limiter
from app.domains.ai_chat.schemas import (
    AiChatConversationCreate,
    AiChatConversationDetail,
    AiChatConversationRead,
    AiChatConversationUpdate,
    AiChatMessageCreate,
    ApoemaChatMessageCreate,
    ApoemaChatMessageResponse,
    ApoemaChatProvidersResponse,
)
from app.domains.ai_chat.service import AiChatService
from app.domains.audit.ai import record_ai_operation_audits
from app.domains.users.models import User
from app.shared.enums import AiCapability
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

ai_chat_user = Depends(require_ai_capability(AiCapability.AI_CHAT_ACCESS))
_AI_CHAT_RATE_LIMIT = get_ai_chat_rate_limiter()._memory_store._buckets  # compatibility for existing tests


def _ensure_ai_chat_enabled() -> None:
    ensure_ai_enabled(settings)


async def _apply_rate_limit(user_id: UUID) -> None:
    # Rate limit is enforced by the shared store abstraction to keep multi-worker and multi-container behavior aligned.
    limiter = get_ai_chat_rate_limiter()
    await limiter.check(user_id)


def _provider_error_detail(prefix: str, exc: Exception) -> str:
    # Provider exceptions contain sanitized error codes only. Never include prompt bodies or API keys here.
    return f"{prefix}: {exc}"


@router.get("/health")
async def health(current_user: User = ai_chat_user) -> dict[str, object]:  # noqa: ARG001
    _ensure_ai_chat_enabled()
    provider_health = get_ai_provider_health(settings)
    return {"enabled": settings.enable_ai_chat, **provider_health}


@router.get("/providers", response_model=ApoemaChatProvidersResponse)
async def list_apoema_providers(current_user: User = ai_chat_user) -> ApoemaChatProvidersResponse:  # noqa: ARG001
    _ensure_ai_chat_enabled()
    return build_apoema_provider_catalog(settings)


@router.post("/message", response_model=ApoemaChatMessageResponse)
async def send_apoema_message(
    payload: ApoemaChatMessageCreate,
    current_user: User = ai_chat_user,
    session: AsyncSession = Depends(get_session),
) -> ApoemaChatMessageResponse:
    _ensure_ai_chat_enabled()
    if len(payload.message) > settings.ai_max_input_chars:
        raise HTTPException(status_code=422, detail="ai_chat_input_too_large")
    await _apply_rate_limit(current_user.id)
    started = time.perf_counter()

    async def operation() -> ApoemaChatMessageResponse:
        response = await generate_apoema_message(settings, payload)
        await record_ai_operation_audits(
            session,
            event="CHAT_MESSAGE",
            user=current_user,
            provider=response.provider,
            model=response.model,
            resource_type="ChatConversation",
            resource_id=response.conversation_id,
            status="SUCCESS" if response.status == "ok" else "FAILED",
            duration_ms=round((time.perf_counter() - started) * 1000),
            error=response.error,
        )
        return response

    return await commit_or_rollback(session, operation)


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
        await _apply_rate_limit(current_user.id)
    service = AiChatService(session)
    started = time.perf_counter()

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
        if payload.message:
            await record_ai_operation_audits(
                session,
                event="CHAT_MESSAGE",
                user=current_user,
                provider=conversation.provider,
                model=conversation.model,
                resource_type="ChatConversation",
                resource_id=conversation.id,
                status="SUCCESS",
                duration_ms=round((time.perf_counter() - started) * 1000),
            )
        messages = await service.repository.list_messages(conversation.id)
        return service.to_detail(conversation, messages)

    try:
        return await commit_or_rollback(session, operation)
    except HTTPException as exc:
        if payload.message:
            await record_ai_operation_audits(
                session,
                event="CHAT_MESSAGE",
                user=current_user,
                provider=settings.ai_provider,
                model=settings.ai_model,
                resource_type="ChatConversation",
                resource_id=None,
                status="FAILED",
                duration_ms=round((time.perf_counter() - started) * 1000),
                error=str(exc.detail),
            )
            await session.commit()
        raise


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


@router.patch("/conversations/{conversation_id}", response_model=AiChatConversationRead)
async def rename_conversation(
    conversation_id: UUID,
    payload: AiChatConversationUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    service = AiChatService(session)
    conversation = await service.get_conversation(conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ai_chat_conversation_not_found")

    async def operation():
        return await service.rename_conversation(conversation, payload, current_user.id)

    return await commit_or_rollback(session, operation)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    service = AiChatService(session)
    conversation = await service.get_conversation(conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ai_chat_conversation_not_found")

    async def operation():
        await service.delete_conversation(conversation, current_user.id)
        return None

    return await commit_or_rollback(session, operation)


@router.post("/conversations/{conversation_id}/messages", response_model=AiChatConversationDetail)
async def send_message(
    conversation_id: UUID,
    payload: AiChatMessageCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = ai_chat_user,
):
    _ensure_ai_chat_enabled()
    await _apply_rate_limit(current_user.id)
    service = AiChatService(session)
    conversation = await service.get_conversation(conversation_id, current_user.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ai_chat_conversation_not_found")
    started = time.perf_counter()

    async def operation():
        try:
            detail = await service.send_message(conversation, payload, current_user.id)
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
        await record_ai_operation_audits(
            session,
            event="CHAT_MESSAGE",
            user=current_user,
            provider=conversation.provider,
            model=conversation.model,
            resource_type="ChatConversation",
            resource_id=conversation.id,
            status="SUCCESS",
            duration_ms=round((time.perf_counter() - started) * 1000),
        )
        return detail

    try:
        return await commit_or_rollback(session, operation)
    except HTTPException as exc:
        await record_ai_operation_audits(
            session,
            event="CHAT_MESSAGE",
            user=current_user,
            provider=conversation.provider,
            model=conversation.model,
            resource_type="ChatConversation",
            resource_id=conversation.id,
            status="FAILED",
            duration_ms=round((time.perf_counter() - started) * 1000),
            error=str(exc.detail),
        )
        await session.commit()
        raise
