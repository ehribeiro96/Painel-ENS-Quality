from __future__ import annotations

import asyncio
import json
import urllib.error
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


def build_ai_provider(settings: object) -> AiProvider:
    provider = (getattr(settings, "ai_provider", "mock") or "mock").strip().lower()
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
    raise ValueError(f"Unsupported AI_PROVIDER: {provider}")


def get_ai_provider_health(settings: object) -> dict[str, object]:
    provider = (getattr(settings, "ai_provider", "mock") or "mock").strip().lower()
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
    return {"provider": provider, "configured": False, "status": "unsupported_provider"}


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
    if not isinstance(content, str) or not content.strip():
        raise AiProviderRequestError("openai_empty_response")
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
    text = "".join(texts).strip()
    if not text:
        raise AiProviderRequestError("gemini_empty_response")
    return text


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
