from __future__ import annotations

import asyncio
import ipaddress
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol

AiProviderRole = Literal["system", "user", "assistant"]
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
AiHttpPost = Callable[[str, dict[str, str], dict[str, object], int], Awaitable[dict[str, object]]]

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
GEMINI_GENERATE_CONTENT_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_LAN_BASE_URL = "http://192.168.0.103:11434/v1"
DEFAULT_OLLAMA_MODEL = "qwen3:1.7b-64k"
DEFAULT_HERMES_MODEL = "hermes-agent"
OLLAMA_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
HERMES_SMOKE_TEST_PHRASE = "APOEMA-HERMES-OK"
_HERMES_SESSION_RE = re.compile(r"(?:\r?\n)?session_id:\s*([^\s]+)\s*$")
_THINK_BLOCK_RE = re.compile(r"<think\b[^>]*>.*?</think\s*>", re.IGNORECASE | re.DOTALL)
_THINK_OPEN_RE = re.compile(r"^\s*<think\b[^>]*>\s*", re.IGNORECASE)


class AiProviderConfigurationError(ValueError):
    """Raised when an AI provider is selected but not safely configured."""


class AiProviderRequestError(RuntimeError):
    """Raised when an AI provider request fails after configuration is valid."""


@dataclass(frozen=True)
class AiProviderMessage:
    role: AiProviderRole
    content: str


@dataclass(frozen=True)
class AiProviderResponse:
    content: str
    provider: str
    model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    raw_metadata: dict[str, object] = field(default_factory=dict)


class AiProvider(Protocol):
    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:
        ...


class MockAiProvider:
    provider = "mock"

    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:
        last_user_message = next((message.content for message in reversed(messages) if message.role == "user"), "")
        user_text = last_user_message.strip()
        selected_mode = normalize_ai_chat_mode(mode) or infer_ai_chat_mode(user_text)
        body = _mock_response_body(user_text, selected_mode)
        content = (
            "Modo mock: resposta simulada para validação do Painel ENS-Quality.\n"
            f"{body}\n\n"
            "Observação: esta resposta não é Gemini, não usou internet, não chamou OpenAI/Gemini "
            "e não executou ação no sistema."
        )
        return AiProviderResponse(content=content, provider=self.provider)


def normalize_ai_chat_mode(mode: str | None) -> AiChatMode | None:
    allowed = {
        "general",
        "fix_text",
        "draft_ticket",
        "update_ticket",
        "resolution",
        "summarize",
        "improve_tone",
        "service_macro",
        "asset_guidance",
    }
    value = (mode or "").strip().lower()
    return value if value in allowed else None  # type: ignore[return-value]


def infer_ai_chat_mode(user_text: str) -> AiChatMode:
    normalized = user_text.lower()
    if _contains_any(normalized, ("corrigir", "corrija", "correção", "revisar texto", "ortografia", "concordância")):
        return "fix_text"
    if _contains_any(normalized, ("abertura", "abrir chamado", "rascunho itil", "itil", "novo chamado")):
        return "draft_ticket"
    if _contains_any(normalized, ("atualização", "atualizar chamado", "andamento", "status do chamado")):
        return "update_ticket"
    if _contains_any(normalized, ("solução aplicada", "resolução", "resolvido", "encerramento técnico")):
        return "resolution"
    if _contains_any(normalized, ("resumir", "resumo", "sintetizar")):
        return "summarize"
    if _contains_any(normalized, ("melhorar tom", "profissional", "formal", "educado", "corporativo")):
        return "improve_tone"
    if _contains_any(normalized, ("macro", "service desk", "atendimento")):
        return "service_macro"
    if _contains_any(normalized, ("ativo", "patrimônio", "inventário", "notebook", "desktop", "monitor", "movimentação")):
        return "asset_guidance"
    return "general"


def _mock_response_body(user_text: str, mode: AiChatMode) -> str:
    if mode == "fix_text":
        return "Texto revisado:\n" + _mock_fix_text(user_text)
    if mode == "draft_ticket":
        return (
            "Título: Atendimento de Service Desk a validar\n"
            "Descrição: Solicitação recebida e estruturada para abertura de chamado. Revise os dados reais antes de registrar.\n"
            "Impacto: A confirmar conforme usuário, serviço, local e quantidade de pessoas afetadas.\n"
            "Urgência: Média, ajustável conforme criticidade informada.\n"
            "Categoria sugerida: Service Desk / Suporte ao usuário.\n"
            "Ação realizada: Rascunho textual gerado para apoio ao registro.\n"
            "Validação: Confirmar patrimônio, usuário, evidências e resultado esperado.\n"
            "Próximo passo: Revisar o rascunho e registrar manualmente no sistema apropriado."
        )
    if mode == "update_ticket":
        return (
            "Atualização de chamado:\n"
            "Situação atual: Atendimento em análise com informações recebidas até o momento.\n"
            "Ação realizada: Dados organizados para comunicação objetiva ao solicitante.\n"
            "Pendência: Confirmar evidências, responsável e prazo estimado, se aplicável.\n"
            "Próximo passo: Manter o solicitante informado e validar a resolução antes do encerramento."
        )
    if mode == "resolution":
        return (
            "Solução aplicada:\n"
            "Foi realizada a análise da solicitação e aplicada a orientação/correção descrita pelo atendimento.\n"
            "Validação: Confirmar com o usuário se o serviço/equipamento voltou a operar conforme esperado.\n"
            "Encerramento sugerido: Caso não haja novas evidências de falha, o chamado pode ser encerrado manualmente após aprovação humana."
        )
    if mode == "summarize":
        return (
            "Resumo:\n"
            "- Solicitação recebida e organizada para leitura rápida.\n"
            "- Pontos principais devem ser confirmados com dados reais do atendimento.\n"
            "- Nenhuma alteração operacional foi realizada pela IA.\n"
            "- Próximo passo: revisar evidências e definir encaminhamento manual."
        )
    if mode == "improve_tone":
        return (
            "Versão corporativa:\n"
            "Prezado(a), registramos sua solicitação e seguiremos com a análise necessária. "
            "Retornaremos com uma atualização assim que houver validação das informações. "
            "Agradecemos a compreensão e permanecemos à disposição para apoiar de forma cordial e objetiva."
        )
    if mode == "service_macro":
        return (
            "Macro de atendimento:\n"
            "Prezado(a), recebemos sua solicitação e iniciamos a análise.\n"
            "No momento, estamos validando as informações necessárias para orientar a tratativa com segurança.\n"
            "Assim que concluirmos a verificação, retornaremos com a solução ou próximo passo recomendado.\n"
            "Permanecemos à disposição."
        )
    if mode == "asset_guidance":
        return (
            "Checklist de inventário/movimentação:\n"
            "- Confirmar patrimônio/serial e hostname do equipamento.\n"
            "- confirmar colaborador atual, destino previsto e justificativa.\n"
            "- Validar status físico/lógico antes de qualquer registro.\n"
            "- registrar movimentação somente por ação humana no painel.\n"
            "- gerar macro/copiar macro apenas depois da movimentação salva.\n"
            "- auditar histórico para rastreabilidade."
        )
    return (
        "Resposta útil:\n"
        f"Recebi sua mensagem: {user_text or 'mensagem sem conteúdo textual disponível.'}\n\n"
        "Sugestões de uso:\n"
        "- Corrigir texto e melhorar tom corporativo.\n"
        "- Gerar abertura ITIL, atualização de chamado ou solução aplicada.\n"
        "- Resumir atendimentos e preparar macros textuais.\n"
        "- Orientar checklist de inventário sem executar ações no sistema."
    )


def _mock_fix_text(text: str) -> str:
    cleaned = _mock_sentence(text)
    replacements = {
        "Eu precisa": "Eu preciso",
        " eu precisa": " eu preciso",
        " precisa configura ": " preciso configurar ",
        " configura ": " configurar ",
        " nois ": " nós ",
        " agente ": " a gente ",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _mock_sentence(text: str) -> str:
    cleaned = " ".join(text.split()).strip()
    if not cleaned:
        return "Texto de exemplo revisado para validação da interface."
    return cleaned[0].upper() + cleaned[1:]


class GeminiProvider:
    provider = "gemini"

    def __init__(
        self,
        settings: object | None = None,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        max_output_tokens: int | None = None,
        http_post: AiHttpPost | None = None,
    ) -> None:
        if settings is not None:
            api_key = getattr(settings, "ai_gemini_api_key", "") or ""
            model = getattr(settings, "ai_model", "") or DEFAULT_GEMINI_MODEL
            timeout_seconds = int(getattr(settings, "ai_timeout_seconds", 30) or 30)
            max_output_tokens = int(getattr(settings, "ai_max_output_tokens", 1000) or 1000)
        api_key = api_key or ""
        if not api_key.strip():
            raise AiProviderConfigurationError("gemini_api_key_missing")
        self.api_key = api_key
        self.model = (model or DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
        self.timeout_seconds = max(1, timeout_seconds or 30)
        self.max_output_tokens = max(1, max_output_tokens or 1000)
        self.http_post = http_post or _default_http_post

    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:
        payload: dict[str, object] = {
            "contents": _gemini_contents(messages),
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": self.max_output_tokens,
            },
        }
        system_instruction = _gemini_system_instruction(messages)
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        url = GEMINI_GENERATE_CONTENT_URL_TEMPLATE.format(model=self.model)
        try:
            data = await self.http_post(url, headers, payload, self.timeout_seconds)
        except TimeoutError as exc:
            raise AiProviderRequestError("gemini_timeout") from exc
        except AiProviderRequestError:
            raise
        except (urllib.error.URLError, OSError) as exc:
            raise AiProviderRequestError("gemini_request_failed") from exc

        content = _extract_gemini_content(data)
        usage = data.get("usageMetadata", {})
        usage_data = usage if isinstance(usage, dict) else {}
        return AiProviderResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            prompt_tokens=_int_or_none(usage_data.get("promptTokenCount")),
            completion_tokens=_int_or_none(usage_data.get("candidatesTokenCount")),
            raw_metadata={"finish_reason": _extract_gemini_finish_reason(data)},
        )


class OpenAIProvider:
    provider = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        model: str | None,
        timeout_seconds: int,
        max_output_tokens: int,
        http_post: AiHttpPost | None = None,
    ) -> None:
        if not api_key.strip():
            raise AiProviderConfigurationError("openai_api_key_missing")
        self.api_key = api_key
        self.model = (model or DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL
        self.timeout_seconds = max(1, timeout_seconds)
        self.max_output_tokens = max(1, max_output_tokens)
        self.http_post = http_post or _default_http_post

    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:
        payload: dict[str, object] = {
            "model": self.model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "max_tokens": self.max_output_tokens,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            data = await self.http_post(OPENAI_CHAT_COMPLETIONS_URL, headers, payload, self.timeout_seconds)
        except TimeoutError as exc:
            raise AiProviderRequestError("openai_timeout") from exc
        except AiProviderRequestError:
            raise
        except (urllib.error.URLError, OSError) as exc:
            raise AiProviderRequestError("openai_request_failed") from exc

        content = _extract_openai_content(data)
        usage = data.get("usage", {})
        usage_data = usage if isinstance(usage, dict) else {}
        return AiProviderResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            prompt_tokens=_int_or_none(usage_data.get("prompt_tokens")),
            completion_tokens=_int_or_none(usage_data.get("completion_tokens")),
            raw_metadata={"finish_reason": _extract_finish_reason(data)},
        )


class OllamaProvider:
    provider = "ollama"

    def __init__(
        self,
        settings: object | None = None,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        http_post: AiHttpPost | None = None,
    ) -> None:
        if settings is not None:
            base_url = getattr(settings, "ollama_base_url", "") or DEFAULT_OLLAMA_BASE_URL
            model = getattr(settings, "ollama_model", "") or getattr(settings, "ai_model", "") or DEFAULT_OLLAMA_MODEL
            timeout_seconds = int(getattr(settings, "ollama_timeout_seconds", 120) or 120)
        self.base_url = _normalize_ollama_local_base_url(base_url or DEFAULT_OLLAMA_BASE_URL)
        self.model = (model or DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL
        self.timeout_seconds = max(1, timeout_seconds or 120)
        self.http_post = http_post or _default_http_post

    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:  # noqa: ARG002
        payload: dict[str, object] = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
        }
        headers = {"Content-Type": "application/json"}
        try:
            data = await self.http_post(f"{self.base_url}/api/chat", headers, payload, self.timeout_seconds)
        except TimeoutError as exc:
            raise AiProviderRequestError("ollama_timeout") from exc
        except AiProviderRequestError as exc:
            if str(exc) == "provider_http_404":
                raise AiProviderRequestError("ollama_model_unavailable") from exc
            raise
        except (urllib.error.URLError, OSError) as exc:
            raise AiProviderRequestError("ollama_request_failed") from exc

        content = _extract_ollama_content(data)
        return AiProviderResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            prompt_tokens=_int_or_none(data.get("prompt_eval_count")),
            completion_tokens=_int_or_none(data.get("eval_count")),
            raw_metadata={"done_reason": data.get("done_reason")},
        )


class OllamaLanProvider:
    provider = "ollama-lan"

    def __init__(
        self,
        settings: object | None = None,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        allowed_hosts: list[str] | tuple[str, ...] | set[str] | None = None,
        http_post: AiHttpPost | None = None,
    ) -> None:
        if settings is not None:
            base_url = getattr(settings, "ollama_base_url", "") or DEFAULT_OLLAMA_LAN_BASE_URL
            model = getattr(settings, "ollama_model", "") or getattr(settings, "ai_model", "") or DEFAULT_OLLAMA_MODEL
            timeout_seconds = int(getattr(settings, "ollama_timeout_seconds", 120) or 120)
            allowed_hosts = getattr(settings, "ollama_allowed_hosts", None)
        self.base_url = _normalize_ollama_lan_base_url(
            base_url or DEFAULT_OLLAMA_LAN_BASE_URL,
            allowed_hosts=allowed_hosts,
        )
        self.model = (model or DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL
        self.timeout_seconds = max(1, timeout_seconds or 120)
        self.http_post = http_post or _default_http_post

    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:  # noqa: ARG002
        payload: dict[str, object] = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
        }
        headers = {"Content-Type": "application/json"}
        try:
            data = await self.http_post(f"{self.base_url}/chat/completions", headers, payload, self.timeout_seconds)
        except TimeoutError as exc:
            raise AiProviderRequestError("ollama_lan_timeout") from exc
        except AiProviderRequestError as exc:
            if str(exc) == "provider_http_404":
                raise AiProviderRequestError("ollama_lan_model_unavailable") from exc
            raise
        except (urllib.error.URLError, OSError) as exc:
            raise AiProviderRequestError("ollama_lan_request_failed") from exc

        content = _extract_ollama_lan_content(data)
        usage = data.get("usage", {})
        usage_data = usage if isinstance(usage, dict) else {}
        return AiProviderResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            prompt_tokens=_int_or_none(usage_data.get("prompt_tokens")),
            completion_tokens=_int_or_none(usage_data.get("completion_tokens")),
            raw_metadata={"finish_reason": _extract_finish_reason(data)},
        )


class HermesTerminalProvider:
    provider = "hermes"

    def __init__(
        self,
        settings: object | None = None,
        *,
        model: str | None = None,
        timeout_seconds: int | None = None,
        source: str = "apoema",
    ) -> None:
        if settings is not None:
            model = getattr(settings, "hermes_model", "") or DEFAULT_HERMES_MODEL
            timeout_seconds = int(getattr(settings, "ai_timeout_seconds", 30) or 30)
        self.model = (model or DEFAULT_HERMES_MODEL).strip() or DEFAULT_HERMES_MODEL
        self.timeout_seconds = max(1, timeout_seconds or 30)
        self.source = (source or "apoema").strip() or "apoema"

    async def generate(self, messages: list[AiProviderMessage], mode: AiChatMode | None = None) -> AiProviderResponse:  # noqa: ARG002
        query = _compose_hermes_query(messages)
        latest_user_message = next((message.content.strip() for message in reversed(messages) if message.role == "user"), "")
        if latest_user_message == HERMES_SMOKE_TEST_PHRASE:
            query = f"Responda somente: {HERMES_SMOKE_TEST_PHRASE}"
        content, metadata = await asyncio.to_thread(
            _run_hermes_chat,
            query,
            self.timeout_seconds,
            self.source,
        )
        return AiProviderResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            raw_metadata=metadata,
        )


def build_ai_provider(settings: object) -> AiProvider:
    provider = _normalize_provider_name(getattr(settings, "ai_provider", "mock") or "mock")
    if provider == "mock":
        return MockAiProvider()
    if provider == "gemini":
        return GeminiProvider(settings)
    if provider == "openai":
        return OpenAIProvider(
            api_key=getattr(settings, "openai_api_key", "") or "",
            model=getattr(settings, "ai_model", "") or DEFAULT_OPENAI_MODEL,
            timeout_seconds=int(getattr(settings, "ai_timeout_seconds", 30) or 30),
            max_output_tokens=int(getattr(settings, "ai_max_output_tokens", 1000) or 1000),
        )
    if provider == "ollama":
        return OllamaProvider(settings)
    if provider == "ollama-lan":
        return OllamaLanProvider(settings)
    if provider == "hermes":
        return HermesTerminalProvider(settings)
    raise ValueError(f"Unsupported AI_PROVIDER: {provider}")


def get_ai_provider_health(settings: object) -> dict[str, object]:
    provider = _normalize_provider_name(getattr(settings, "ai_provider", "mock") or "mock")
    if provider == "mock":
        return {"provider": "mock", "configured": True, "status": "ok"}
    if provider == "gemini":
        if not (getattr(settings, "ai_gemini_api_key", "") or "").strip():
            return {
                "provider": "gemini",
                "configured": False,
                "status": "configuration_error",
                "detail": "gemini_api_key_missing",
            }
        return {
            "provider": "gemini",
            "configured": True,
            "status": "ok",
            "model": (getattr(settings, "ai_model", "") or DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL,
        }
    if provider == "openai":
        if not (getattr(settings, "openai_api_key", "") or "").strip():
            return {
                "provider": "openai",
                "configured": False,
                "status": "configuration_error",
                "detail": "openai_api_key_missing",
            }
        return {
            "provider": "openai",
            "configured": True,
            "status": "ok",
            "model": (getattr(settings, "ai_model", "") or DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL,
        }
    if provider == "ollama":
        try:
            _normalize_ollama_local_base_url(getattr(settings, "ollama_base_url", "") or DEFAULT_OLLAMA_BASE_URL)
        except AiProviderConfigurationError as exc:
            return {"provider": "ollama", "configured": False, "status": "configuration_error", "detail": str(exc)}
        return {
            "provider": "ollama",
            "configured": True,
            "status": "ok",
            "model": (getattr(settings, "ollama_model", "") or getattr(settings, "ai_model", "") or DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL,
        }
    if provider == "ollama-lan":
        try:
            _normalize_ollama_lan_base_url(
                getattr(settings, "ollama_base_url", "") or DEFAULT_OLLAMA_LAN_BASE_URL,
                allowed_hosts=getattr(settings, "ollama_allowed_hosts", None),
            )
        except AiProviderConfigurationError as exc:
            return {"provider": "ollama-lan", "configured": False, "status": "configuration_error", "detail": str(exc)}
        return {
            "provider": "ollama-lan",
            "configured": True,
            "status": "ok",
            "model": (getattr(settings, "ollama_model", "") or getattr(settings, "ai_model", "") or DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL,
        }
    if provider == "hermes":
        return _hermes_health(settings)
    return {"provider": provider, "configured": False, "status": "unsupported_provider"}


def _normalize_provider_name(provider: str) -> str:
    return (provider or "mock").strip().lower().replace("_", "-")


def _normalize_ollama_local_base_url(base_url: str) -> str:
    return _normalize_ollama_base_url(
        base_url,
        allowed_hosts=OLLAMA_LOOPBACK_HOSTS,
        allow_openai_path=False,
        error_prefix="ollama",
    )


def _normalize_ollama_lan_base_url(
    base_url: str,
    *,
    allowed_hosts: list[str] | tuple[str, ...] | set[str] | None,
) -> str:
    return _normalize_ollama_base_url(
        base_url,
        allowed_hosts=allowed_hosts,
        allow_openai_path=True,
        error_prefix="ollama_lan",
    )


def _normalize_ollama_base_url(
    base_url: str,
    *,
    allowed_hosts: list[str] | tuple[str, ...] | set[str] | None,
    allow_openai_path: bool,
    error_prefix: str,
) -> str:
    value = (base_url or DEFAULT_OLLAMA_BASE_URL).strip().rstrip("/")
    parsed = urllib.parse.urlparse(value)
    host = parsed.hostname or ""
    allowed = _normalize_allowed_hosts(allowed_hosts)
    if parsed.scheme != "http":
        raise AiProviderConfigurationError(f"{error_prefix}_base_url_must_use_http")
    if host.lower() not in allowed:
        raise AiProviderConfigurationError(f"{error_prefix}_host_not_allowed")
    if not _is_safe_ollama_host(host):
        raise AiProviderConfigurationError(f"{error_prefix}_host_not_allowed")
    if allow_openai_path:
        if parsed.path in {"", "/"}:
            return value + "/v1"
        if parsed.path != "/v1":
            raise AiProviderConfigurationError(f"{error_prefix}_base_url_must_use_v1_path")
    elif parsed.path not in {"", "/"}:
        raise AiProviderConfigurationError("ollama_base_url_must_not_include_path")
    return value


def _normalize_allowed_hosts(allowed_hosts: list[str] | tuple[str, ...] | set[str] | None) -> set[str]:
    values = {str(host).strip().lower() for host in (allowed_hosts or []) if str(host).strip()}
    if not values:
        return set(OLLAMA_LOOPBACK_HOSTS)
    if "*" in values or "0.0.0.0/0" in values or "::/0" in values:
        raise AiProviderConfigurationError("ollama_allowed_hosts_wildcard_not_allowed")
    return values


def _is_safe_ollama_host(host: str) -> bool:
    normalized = host.strip().lower()
    if normalized == "localhost":
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return bool(address.is_loopback or address.is_private)


def _compose_hermes_query(messages: list[AiProviderMessage]) -> str:
    role_labels = {
        "system": "Instruções do sistema",
        "user": "Mensagem do usuário",
        "assistant": "Resposta anterior do assistente",
    }
    parts = []
    for message in messages:
        label = role_labels.get(message.role, "Mensagem")
        content = message.content.strip()
        if content:
            parts.append(f"{label}:\n{content}")
    return "\n\n".join(parts).strip()


def _parse_hermes_output(output: str) -> tuple[str, dict[str, object]]:
    text = output.strip()
    metadata: dict[str, object] = {}
    match = _HERMES_SESSION_RE.search(text)
    if match:
        metadata["session_id"] = match.group(1)
        text = text[: match.start()].rstrip()
    return text, metadata


def _run_hermes_chat(query: str, timeout_seconds: int, source: str) -> tuple[str, dict[str, object]]:
    command = ["hermes", "chat", "-q", query, "-Q", "--source", source]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=max(1, timeout_seconds),
        )
    except FileNotFoundError as exc:
        raise AiProviderConfigurationError("hermes_command_not_found") from exc
    except subprocess.TimeoutExpired as exc:
        raise AiProviderRequestError("hermes_timeout") from exc

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    if completed.returncode != 0:
        detail = stderr or stdout or f"exit_{completed.returncode}"
        detail = _sanitize_hermes_error(detail)
        raise AiProviderRequestError(f"hermes_request_failed:{detail}")

    content, metadata = _parse_hermes_output(stdout)
    if stderr:
        metadata["stderr"] = _sanitize_hermes_error(stderr)
    if not content:
        raise AiProviderRequestError("hermes_empty_response")
    metadata["source"] = source
    return content, metadata


def _sanitize_hermes_error(value: str) -> str:
    normalized = " ".join(value.split())
    normalized = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "<redacted-email>", normalized)
    normalized = re.sub(r"\b(?:sk|pk|tok|key|token)[A-Za-z0-9_-]*\b", "<redacted>", normalized, flags=re.IGNORECASE)
    return normalized[:200] if normalized else "hermes_error"


def _hermes_health(settings: object) -> dict[str, object]:
    model = (getattr(settings, "hermes_model", "") or DEFAULT_HERMES_MODEL).strip() or DEFAULT_HERMES_MODEL
    timeout_seconds = max(5, int(getattr(settings, "ai_timeout_seconds", 30) or 30))
    try:
        content, metadata = _run_hermes_chat("Responda somente: APOEMA-HERMES-HEALTH-OK", timeout_seconds, "apoema-health")
    except AiProviderConfigurationError as exc:
        return {
            "provider": "hermes",
            "configured": False,
            "status": "configuration_error",
            "detail": str(exc),
            "model": model,
        }
    except AiProviderRequestError as exc:
        return {
            "provider": "hermes",
            "configured": True,
            "status": "offline",
            "detail": str(exc),
            "model": model,
        }

    if "APOEMA-HERMES-HEALTH-OK" not in content:
        return {
            "provider": "hermes",
            "configured": True,
            "status": "error",
            "detail": "hermes_health_unexpected_output",
            "model": model,
            "session_id": metadata.get("session_id"),
        }

    result: dict[str, object] = {
        "provider": "hermes",
        "configured": True,
        "status": "ok",
        "model": model,
    }
    if metadata.get("session_id"):
        result["session_id"] = metadata["session_id"]
    return result


async def _default_http_post(
    url: str,
    headers: dict[str, str],
    payload: dict[str, object],
    timeout: int,
) -> dict[str, object]:
    return await asyncio.to_thread(_sync_json_post, url, headers, payload, timeout)


def _sync_json_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except TimeoutError:
        raise
    except urllib.error.HTTPError as exc:
        # Do not include request headers, URLs with secrets, or bodies here; they may contain secrets and user prompts.
        raise AiProviderRequestError(f"provider_http_{exc.code}") from exc
    parsed = json.loads(response_body)
    if not isinstance(parsed, dict):
        raise AiProviderRequestError("provider_invalid_response")
    return parsed


def _extract_openai_content(data: dict[str, object]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AiProviderRequestError("openai_empty_response")
    first = choices[0]
    if not isinstance(first, dict):
        raise AiProviderRequestError("openai_invalid_response")
    message = first.get("message")
    if not isinstance(message, dict):
        raise AiProviderRequestError("openai_invalid_response")
    content = message.get("content")
    if not isinstance(content, str):
        raise AiProviderRequestError("openai_empty_response")
    content = _sanitize_ai_response_content(content)
    if not content:
        raise AiProviderRequestError("openai_empty_response")
    return content


def _extract_ollama_content(data: dict[str, object]) -> str:
    message = data.get("message")
    if not isinstance(message, dict):
        raise AiProviderRequestError("ollama_invalid_response")
    content = message.get("content")
    if not isinstance(content, str):
        raise AiProviderRequestError("ollama_empty_response")
    content = _sanitize_ai_response_content(content)
    if not content:
        raise AiProviderRequestError("ollama_empty_response")
    return content


def _extract_ollama_lan_content(data: dict[str, object]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AiProviderRequestError("ollama_lan_empty_response")
    first = choices[0]
    if not isinstance(first, dict):
        raise AiProviderRequestError("ollama_lan_invalid_response")
    message = first.get("message")
    if not isinstance(message, dict):
        raise AiProviderRequestError("ollama_lan_invalid_response")
    content = message.get("content")
    if not isinstance(content, str):
        raise AiProviderRequestError("ollama_lan_empty_response")
    content = _sanitize_ai_response_content(content)
    if not content:
        raise AiProviderRequestError("ollama_lan_empty_response")
    return content


def _gemini_system_instruction(messages: list[AiProviderMessage]) -> dict[str, object] | None:
    text = "\n\n".join(message.content for message in messages if message.role == "system" and message.content.strip())
    if not text.strip():
        return None
    return {"parts": [{"text": text}]}


def _gemini_contents(messages: list[AiProviderMessage]) -> list[dict[str, object]]:
    contents: list[dict[str, object]] = []
    for message in messages:
        if message.role == "system":
            continue
        role = "model" if message.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": message.content}]})
    if not contents:
        contents.append({"role": "user", "parts": [{"text": ""}]})
    return contents


def _extract_gemini_content(data: dict[str, object]) -> str:
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise AiProviderRequestError("gemini_empty_response")
    first = candidates[0]
    if not isinstance(first, dict):
        raise AiProviderRequestError("gemini_invalid_response")
    content = first.get("content")
    if not isinstance(content, dict):
        raise AiProviderRequestError("gemini_invalid_response")
    parts = content.get("parts")
    if not isinstance(parts, list):
        raise AiProviderRequestError("gemini_invalid_response")
    texts = [part.get("text", "") for part in parts if isinstance(part, dict) and isinstance(part.get("text"), str)]
    text = _sanitize_ai_response_content("".join(texts))
    if not text:
        raise AiProviderRequestError("gemini_empty_response")
    return text


def _sanitize_ai_response_content(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        return ""
    cleaned = _THINK_BLOCK_RE.sub("", cleaned).strip()
    if not cleaned:
        return ""
    if _THINK_OPEN_RE.match(cleaned):
        remainder = _THINK_OPEN_RE.sub("", cleaned, count=1).strip()
        if not remainder:
            return ""
        if re.search(r"\n\s*\n", remainder):
            remainder = re.split(r"\n\s*\n", remainder, maxsplit=1)[-1].strip()
        else:
            lines = [line.strip() for line in remainder.splitlines() if line.strip()]
            if len(lines) > 1:
                remainder = lines[-1]
        cleaned = remainder.strip()
    return _THINK_BLOCK_RE.sub("", cleaned).strip()


def _extract_gemini_finish_reason(data: dict[str, object]) -> object:
    candidates = data.get("candidates")
    if isinstance(candidates, list) and candidates and isinstance(candidates[0], dict):
        return candidates[0].get("finishReason")
    return None


def _extract_finish_reason(data: dict[str, object]) -> object:
    choices = data.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        return choices[0].get("finish_reason")
    return None


def _int_or_none(value: object) -> int | None:
    return value if isinstance(value, int) else None
