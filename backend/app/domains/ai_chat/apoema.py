from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.core.config.settings import Settings
from app.domains.ai_chat.providers import (
    AiProviderConfigurationError,
    AiProviderMessage,
    AiProviderRequestError,
    AiProviderResponse,
    HermesTerminalProvider,
    MockAiProvider,
    OllamaProvider,
    get_ai_provider_health,
)
from app.domains.ai_chat.schemas import (
    ApoemaChatMessageCreate,
    ApoemaChatMessageResponse,
    ApoemaChatProviderRead,
    ApoemaChatProvidersResponse,
)

APOEMA_SYSTEM_PROMPT = """Você é o assistente de IA do Apoema Preview, um painel corporativo de inventário, suporte e operações de TI.

Responda em Português Brasileiro com foco técnico, clareza operacional e segurança.
Não invente dados de inventário.
Não execute ações no sistema.
Quando faltar contexto, explique o que precisa ser consultado.
"""

APOEMA_DEFAULT_OLLAMA_MODEL = "qwen3:4b-64k"
APOEMA_DEFAULT_OLLAMA_ALT_MODEL = "qwen2.5-coder:7b"
APOEMA_DEFAULT_FALLBACK_MODEL = "fallback-local"
APOEMA_DEFAULT_HERMES_MODEL = "hermes-agent"
APOEMA_PROVIDER_IDS = ("mock", "ollama", "hermes")


def build_apoema_provider_catalog(settings: Settings) -> ApoemaChatProvidersResponse:
    providers = [
        ApoemaChatProviderRead(
            id="mock",
            label="Mock adapter",
            status="online",
            models=[APOEMA_DEFAULT_FALLBACK_MODEL],
            default_model=APOEMA_DEFAULT_FALLBACK_MODEL,
        ),
        ApoemaChatProviderRead(
            id="ollama",
            label="Ollama",
            status=_ollama_status(settings),
            models=_ollama_models(settings),
            default_model=_ollama_default_model(settings),
        ),
        ApoemaChatProviderRead(
            id="hermes",
            label="Hermes",
            status=_hermes_status(settings),
            models=[_hermes_default_model(settings)],
            default_model=_hermes_default_model(settings),
        ),
    ]
    default_provider = _normalize_provider_id(getattr(settings, "ai_chat_default_provider", "mock"))
    ordered = _prioritize_default_provider(providers, default_provider)
    return ApoemaChatProvidersResponse(providers=ordered)


async def generate_apoema_message(settings: Settings, payload: ApoemaChatMessageCreate) -> ApoemaChatMessageResponse:
    provider_id = _normalize_provider_id(payload.provider or getattr(settings, "ai_chat_default_provider", "mock"))
    conversation_id = (payload.conversation_id or str(uuid4())).strip() or str(uuid4())
    message_id = str(uuid4())
    created_at = datetime.now(UTC)
    model = payload.model.strip() or _provider_default_model(settings, provider_id)
    provider_messages = _compose_provider_messages(payload)

    if provider_id == "mock":
        response = await MockAiProvider().generate(provider_messages)
        return _build_response(
            conversation_id=conversation_id,
            message_id=message_id,
            provider="mock",
            model=model,
            status="ok",
            content=response.content,
            created_at=created_at,
            error=None,
        )

    if provider_id == "ollama":
        try:
            response = await OllamaProvider(
                base_url=settings.ollama_base_url,
                model=model,
                timeout_seconds=settings.ollama_timeout_seconds,
            ).generate(provider_messages)
            return _build_response(
                conversation_id=conversation_id,
                message_id=message_id,
                provider="ollama",
                model=response.model or model,
                status="ok",
                content=response.content,
                created_at=created_at,
                error=None,
                usage=response,
            )
        except AiProviderConfigurationError as exc:
            return await _fallback_response(
                conversation_id=conversation_id,
                message_id=message_id,
                provider="ollama",
                model=model,
                created_at=created_at,
                error=str(exc),
                status="error",
                provider_messages=provider_messages,
            )
        except AiProviderRequestError as exc:
            status = "offline" if "timeout" in str(exc) or "request_failed" in str(exc) or "unavailable" in str(exc) else "error"
            return await _fallback_response(
                conversation_id=conversation_id,
                message_id=message_id,
                provider="ollama",
                model=model,
                created_at=created_at,
                error=str(exc),
                status=status,
                provider_messages=provider_messages,
            )

    if provider_id == "hermes":
        try:
            response = await HermesTerminalProvider(settings).generate(provider_messages)
            return _build_response(
                conversation_id=conversation_id,
                message_id=message_id,
                provider="hermes",
                model=response.model or model,
                status="ok",
                content=response.content,
                created_at=created_at,
                error=None,
                usage=response,
            )
        except AiProviderConfigurationError as exc:
            return await _fallback_response(
                conversation_id=conversation_id,
                message_id=message_id,
                provider="hermes",
                model=model,
                created_at=created_at,
                error=str(exc),
                status="error",
                provider_messages=provider_messages,
            )
        except AiProviderRequestError as exc:
            status = "offline" if "timeout" in str(exc) or "request_failed" in str(exc) or "unavailable" in str(exc) else "error"
            return await _fallback_response(
                conversation_id=conversation_id,
                message_id=message_id,
                provider="hermes",
                model=model,
                created_at=created_at,
                error=str(exc),
                status=status,
                provider_messages=provider_messages,
            )

    raise AiProviderConfigurationError(f"apoema_provider_unsupported:{provider_id}")


def _build_response(
    *,
    conversation_id: str,
    message_id: str,
    provider: str,
    model: str,
    status: str,
    content: str,
    created_at: datetime,
    error: str | None,
    usage: AiProviderResponse | None = None,
) -> ApoemaChatMessageResponse:
    prompt_tokens = usage.prompt_tokens if usage else None
    completion_tokens = usage.completion_tokens if usage else None
    total_tokens = None
    if prompt_tokens is not None and completion_tokens is not None:
        total_tokens = prompt_tokens + completion_tokens
    return ApoemaChatMessageResponse.model_validate(
        {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "provider": provider,
            "model": model,
            "status": status,
            "content": content,
            "created_at": created_at,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "error": error,
        }
    )


async def _fallback_response(
    *,
    conversation_id: str,
    message_id: str,
    provider: str,
    model: str,
    created_at: datetime,
    error: str,
    status: str,
    provider_messages: list[AiProviderMessage],
) -> ApoemaChatMessageResponse:
    fallback_response = await MockAiProvider().generate(provider_messages)
    content = "\n".join(
        [
            "O provedor de IA está offline. Verifique a configuração do Ollama ou Hermes.",
            "Usando fallback local para manter a conversa ativa.",
            f"Motivo técnico: {error}.",
            fallback_response.content,
        ]
    )
    return _build_response(
        conversation_id=conversation_id,
        message_id=message_id,
        provider=provider,
        model=model,
        status=status,
        content=content,
        created_at=created_at,
        error=error,
    )


def _compose_provider_messages(payload: ApoemaChatMessageCreate) -> list[AiProviderMessage]:
    user_parts = [
        f"Mensagem do usuário:\n{payload.message.strip()}",
        f"Modo do Apoema: {payload.mode.strip() or 'assistente_n2'}",
        f"Contexto: route={payload.context.route}; source={payload.context.source}",
    ]
    if payload.attachments:
        attachment_lines = [
            f"- {attachment.name} | mime={attachment.mime_type} | size={attachment.size} | kind={attachment.kind} | sensitive={str(attachment.sensitive).lower()}"
            for attachment in payload.attachments
        ]
        user_parts.append("Metadados dos anexos:\n" + "\n".join(attachment_lines))
    return [
        AiProviderMessage(role="system", content=APOEMA_SYSTEM_PROMPT),
        AiProviderMessage(role="user", content="\n\n".join(user_parts)),
    ]


def _provider_default_model(settings: Settings, provider_id: str) -> str:
    if provider_id == "mock":
        return APOEMA_DEFAULT_FALLBACK_MODEL
    if provider_id == "ollama":
        return _ollama_default_model(settings)
    if provider_id == "hermes":
        return _hermes_default_model(settings)
    return APOEMA_DEFAULT_FALLBACK_MODEL


def _ollama_default_model(settings: Settings) -> str:
    configured = (settings.ollama_model or "").strip()
    if not configured or configured == "qwen3:1.7b-64k":
        return APOEMA_DEFAULT_OLLAMA_MODEL
    return configured


def _ollama_models(settings: Settings) -> list[str]:
    models = [_ollama_default_model(settings), APOEMA_DEFAULT_OLLAMA_ALT_MODEL]
    seen: set[str] = set()
    ordered: list[str] = []
    for model in models:
        if model not in seen:
            ordered.append(model)
            seen.add(model)
    return ordered


def _hermes_default_model(settings: Settings) -> str:
    configured = (settings.hermes_model or "").strip()
    return configured or APOEMA_DEFAULT_HERMES_MODEL


def _ollama_status(settings: Settings) -> str:
    base_url = (settings.ollama_base_url or "").strip()
    if not base_url:
        return "offline"
    return "online"


def _hermes_status(settings: Settings) -> str:
    health = get_ai_provider_health(
        SimpleNamespace(
            ai_provider="hermes",
            hermes_model=settings.hermes_model,
            ai_timeout_seconds=settings.ai_timeout_seconds,
        ),
    )
    status = str(health.get("status") or "offline")
    if status == "ok":
        return "online"
    if status == "configuration_error":
        return "unconfigured"
    return "offline"


def _normalize_provider_id(provider: str) -> str:
    normalized = (provider or "mock").strip().lower().replace("_", "-")
    return normalized if normalized in APOEMA_PROVIDER_IDS else "mock"


def _prioritize_default_provider(
    providers: list[ApoemaChatProviderRead],
    default_provider: str,
) -> list[ApoemaChatProviderRead]:
    # Keep the catalog order stable so the frontend and contract tests
    # see a deterministic provider list regardless of runtime defaults.
    _ = default_provider
    return providers
