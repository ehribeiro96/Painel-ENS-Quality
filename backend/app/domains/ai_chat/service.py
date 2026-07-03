from __future__ import annotations

import uuid

from app.core.config.settings import settings
from app.domains.ai_chat.models import AiChatConversation
from app.domains.ai_chat.providers import (
    AiProviderConfigurationError,
    AiProviderMessage,
    AiProviderRequestError,
    build_ai_provider,
    infer_ai_chat_mode,
    normalize_ai_chat_mode,
)
from app.domains.ai_chat.repository import AiChatRepository
from app.domains.ai_chat.schemas import (
    AiChatConversationCreate,
    AiChatConversationDetail,
    AiChatConversationUpdate,
    AiChatMessageCreate,
    AiChatMessageRead,
    AiChatMode,
)
from sqlalchemy.ext.asyncio import AsyncSession

SYSTEM_PROMPT = """Você é o copiloto textual do Painel ENS-Quality para apoio ao Service Desk.

Responda sempre em português brasileiro, com objetividade, clareza operacional e tom corporativo. Você ajuda a corrigir textos, gerar rascunhos ITIL, atualizações de chamado, soluções aplicadas, resumos de atendimento, macros textuais e orientações de inventário/ativo.

Regras de segurança operacional:
- Nunca afirme que executou ação no sistema.
- Nunca altere dados, ativos, movimentações, usuários, imports, macros, assinaturas ou permissões.
- Nunca invente patrimônio, serial, hostname, usuário, status, evidência, chamado ou movimentação.
- Quando faltar dado, peça a informação ou indique o campo a confirmar.
- Se o usuário pedir ação operacional, entregue apenas rascunho, checklist ou orientação textual e informe que a execução exige ação humana aprovada no painel.

Para ITIL, quando aplicável, organize em:
Título
Descrição
Impacto
Urgência
Categoria sugerida
Ação realizada
Validação
Próximo passo

Para solução aplicada, gere texto pronto, claro e verificável. Para macro de atendimento, gere texto cordial e direto. Para inventário/ativo, oriente verificação, movimentação e auditoria sem executar nada.
"""

MODE_INSTRUCTIONS: dict[str, str] = {
    "general": "Modo atual: geral. Responda com ajuda textual útil e sugira modos mais específicos quando fizer sentido.",
    "fix_text": "Modo atual: correção de texto. Preserve o sentido, corrija gramática/concordância e devolva seção 'Texto revisado'.",
    "draft_ticket": "Modo atual: abertura ITIL. Gere rascunho estruturado com Título, Descrição, Impacto, Urgência, Categoria sugerida, Ação realizada, Validação e Próximo passo.",
    "update_ticket": "Modo atual: atualização de chamado. Gere atualização objetiva com situação atual, ação realizada, pendências e próximo passo.",
    "resolution": "Modo atual: solução aplicada. Gere texto claro de solução, validação e condição de encerramento manual.",
    "summarize": "Modo atual: resumo. Resuma em bullets objetivos, sem inventar informações ausentes.",
    "improve_tone": "Modo atual: melhorar tom. Reescreva em tom corporativo, cordial e objetivo.",
    "service_macro": "Modo atual: macro de atendimento. Gere macro cordial, direta e pronta para copiar.",
    "asset_guidance": "Modo atual: orientação de ativo. Gere checklist de inventário/movimentação/auditoria, sem executar ação no sistema.",
}


def resolve_ai_chat_mode(mode: AiChatMode | str | None, content: str) -> AiChatMode:
    return normalize_ai_chat_mode(mode) or infer_ai_chat_mode(content)


def build_system_prompt(mode: AiChatMode) -> str:
    instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["general"])
    return f"{SYSTEM_PROMPT}\n{instruction}"


class AiChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AiChatRepository(session)

    async def list_conversations(self, user_id: uuid.UUID) -> list[AiChatConversation]:
        return await self.repository.list_conversations(user_id)

    async def create_conversation(self, payload: AiChatConversationCreate, user_id: uuid.UUID) -> AiChatConversation:
        provider = build_ai_provider(settings)
        provider_name = getattr(provider, "provider", settings.ai_provider)
        model = settings.ai_model or getattr(provider, "model", None)
        conversation = await self.repository.create_conversation(user_id, payload.title, provider_name, model)
        if payload.message:
            await self.send_message(conversation, AiChatMessageCreate(content=payload.message, mode=payload.mode), user_id)
        return conversation

    async def rename_conversation(self, conversation: AiChatConversation, payload: AiChatConversationUpdate, user_id: uuid.UUID) -> AiChatConversation:
        return await self.repository.update_conversation_title(conversation, payload.title.strip(), user_id)

    async def delete_conversation(self, conversation: AiChatConversation, user_id: uuid.UUID) -> AiChatConversation:
        return await self.repository.delete_conversation(conversation, user_id)

    async def get_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> AiChatConversation | None:
        return await self.repository.get_conversation_for_user(conversation_id, user_id)

    async def send_message(self, conversation: AiChatConversation, payload: AiChatMessageCreate, user_id: uuid.UUID) -> AiChatConversationDetail:
        input_chars = len(payload.content)
        if input_chars > settings.ai_max_input_chars:
            raise ValueError("ai_chat_input_too_large")

        provider = build_ai_provider(settings)
        provider_name = getattr(provider, "provider", settings.ai_provider)
        model = settings.ai_model or getattr(provider, "model", None)
        mode = resolve_ai_chat_mode(payload.mode, payload.content)
        user_metadata: dict[str, object] = {
            "provider": provider_name,
            "model": model,
            "mode": mode,
            "input_chars": input_chars,
            "output_chars": 0,
            "status": "pending",
        }
        user_message = await self.repository.create_message(
            conversation.id,
            "user",
            payload.content,
            user_id,
            provider=provider_name,
            model=model,
            extra_metadata=user_metadata,
        )
        history = await self.repository.list_messages(conversation.id)
        provider_messages = [AiProviderMessage(role="system", content=build_system_prompt(mode))]
        provider_messages.extend(AiProviderMessage(role=message.role, content=message.content) for message in history[-20:])
        try:
            try:
                response = await provider.generate(provider_messages, mode=mode)
            except TypeError as exc:
                if "unexpected keyword argument 'mode'" not in str(exc):
                    raise
                response = await provider.generate(provider_messages)
        except (AiProviderConfigurationError, AiProviderRequestError) as exc:
            error_metadata = {
                **user_metadata,
                "status": "error",
                "error_type": str(exc),
            }
            await self.repository.update_message_metadata(user_message, error_metadata)
            raise

        user_metadata = {**user_metadata, "status": "ok"}
        await self.repository.update_message_metadata(user_message, user_metadata)
        await self.repository.create_message(
            conversation.id,
            "assistant",
            response.content,
            user_id,
            provider=response.provider,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            extra_metadata={
                "provider": response.provider,
                "model": response.model,
                "mode": mode,
                "input_chars": input_chars,
                "output_chars": len(response.content),
                "status": "ok",
            },
        )
        refreshed_messages = await self.repository.list_messages(conversation.id)
        return self.to_detail(conversation, refreshed_messages)

    @staticmethod
    def to_detail(conversation: AiChatConversation, messages: list[object]) -> AiChatConversationDetail:
        return AiChatConversationDetail.model_validate(
            {
                "id": conversation.id,
                "user_id": conversation.user_id,
                "title": conversation.title,
                "provider": conversation.provider,
                "model": conversation.model,
                "system_prompt_version": conversation.system_prompt_version,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "extra_metadata": conversation.extra_metadata,
                "messages": [AiChatMessageRead.model_validate(message) for message in messages],
            }
        )
