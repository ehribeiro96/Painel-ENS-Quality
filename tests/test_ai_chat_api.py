from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.dependencies.auth import get_current_user, require_role  # noqa: E402
from app.api.v1.routes import ai_chat  # noqa: E402
from app.core.config.settings import get_settings  # noqa: E402
from app.core.database import base as _database_base  # noqa: E402, F401
from app.domains.ai_chat import service as ai_chat_service_module  # noqa: E402
from app.domains.ai_chat import providers as ai_chat_providers_module  # noqa: E402
from app.domains.ai_chat.providers import AiProviderConfigurationError  # noqa: E402
from app.shared.enums import Role  # noqa: E402
from fastapi import HTTPException  # noqa: E402


def force_ai_chat_mock_settings() -> patch:
    env_patch = patch.dict(
        os.environ,
        {
            "AI_PROVIDER": "mock",
            "AI_MODEL": "",
            "AI_GEMINI_API_KEY": "",
            "AI_OPENAI_API_KEY": "",
        },
        clear=False,
    )
    env_patch.start()
    get_settings.cache_clear()
    for settings_obj in (ai_chat.settings, ai_chat_service_module.settings):
        settings_obj.ai_provider = "mock"
        settings_obj.ai_model = ""
        settings_obj.ai_gemini_api_key = ""
        settings_obj.ai_openai_api_key = ""
    return env_patch


class FakeAiChatSession:
    def __init__(self) -> None:
        self.conversations: dict[uuid.UUID, dict[str, object]] = {}
        self.messages: dict[uuid.UUID, list[dict[str, object]]] = {}

    def add(self, entity: object) -> None:
        name = entity.__class__.__name__
        if name == "AiChatConversation":
            if getattr(entity, "id", None) is None:
                entity.id = uuid.uuid4()
            now = datetime.now(UTC)
            entity.created_at = getattr(entity, "created_at", None) or now
            entity.updated_at = getattr(entity, "updated_at", None) or now
            entity.system_prompt_version = getattr(entity, "system_prompt_version", None) or "mvp-1"
            entity.extra_metadata = getattr(entity, "extra_metadata", None) or {}
            self.conversations[entity.id] = {"entity": entity, "user_id": entity.user_id, "deleted_at": entity.deleted_at}
            self.messages.setdefault(entity.id, [])
        elif name == "AiChatMessage":
            if getattr(entity, "id", None) is None:
                entity.id = uuid.uuid4()
            now = datetime.now(UTC)
            entity.created_at = getattr(entity, "created_at", None) or now
            entity.updated_at = getattr(entity, "updated_at", None) or now
            entity.extra_metadata = getattr(entity, "extra_metadata", None) or {}
            bucket = self.messages.setdefault(entity.conversation_id, [])
            if not any(row["entity"].id == entity.id for row in bucket):
                bucket.append({"entity": entity})

    async def flush(self) -> None:
        return None

    async def refresh(self, entity: object) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None

    async def scalar(self, statement):  # noqa: ANN001 - fake SQLAlchemy boundary
        params = statement.compile().params
        row = self.conversations.get(params.get("id_1"))
        if not row:
            return None
        if row["user_id"] != params.get("user_id_1") or row["deleted_at"] is not None:
            return None
        return row["entity"]

    async def execute(self, statement):  # noqa: ANN001 - fake SQLAlchemy boundary
        text = str(statement.compile(compile_kwargs={"literal_binds": False}))
        params = statement.compile().params
        if "FROM ai_chat_conversations" in text:
            user_id = params.get("user_id_1")
            items = [row["entity"] for row in self.conversations.values() if row["user_id"] == user_id and row["deleted_at"] is None]
        elif "FROM ai_chat_messages" in text:
            items = [row["entity"] for row in self.messages.get(params.get("conversation_id_1"), [])]
        else:
            items = []
        return FakeResult(items)


class FakeResult:
    def __init__(self, items: list[object]) -> None:
        self.items = items

    def scalars(self):
        return self

    def all(self) -> list[object]:
        return self.items


class AiChatApiTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.env_patch = force_ai_chat_mock_settings()
        self.addCleanup(self.env_patch.stop)
        self.addCleanup(get_settings.cache_clear)
        self.urlopen_patch = patch.object(
            ai_chat_providers_module.urllib.request,
            "urlopen",
            side_effect=AssertionError("unit tests must not call urllib.request.urlopen"),
        )
        self.urlopen_patch.start()
        self.addCleanup(self.urlopen_patch.stop)
        self.session = FakeAiChatSession()
        self.user_a = self._user(uuid.uuid4(), "a@example.test")
        self.user_b = self._user(uuid.uuid4(), "b@example.test")
        self.original_enable_ai_chat = ai_chat.settings.enable_ai_chat
        ai_chat.settings.enable_ai_chat = True
        ai_chat._AI_CHAT_RATE_LIMIT.clear()

    def tearDown(self) -> None:
        ai_chat.settings.enable_ai_chat = self.original_enable_ai_chat
        ai_chat._AI_CHAT_RATE_LIMIT.clear()

    @staticmethod
    def _user(user_id: uuid.UUID, email: str):
        return SimpleNamespace(id=user_id, name=email, email=email, role=Role.TECHNICIAN)

    def test_routes_depend_on_existing_current_user_authentication(self) -> None:
        protected_paths = {
            "/ai-chat/conversations",
            "/ai-chat/conversations/{conversation_id}",
            "/ai-chat/conversations/{conversation_id}/messages",
        }
        for route in ai_chat.router.routes:
            if getattr(route, "path", None) in protected_paths:
                dependencies = {dependency.call for dependency in route.dependant.dependencies}
                self.assertTrue(
                    get_current_user in dependencies
                    or any(getattr(call, "__closure__", None) for call in dependencies)
                    or require_role in dependencies,
                    route.path,
                )

    async def test_api_uses_mock_provider_even_when_external_environment_selects_gemini(self) -> None:
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "AI_GEMINI_API_KEY": "fake"}, clear=False):
            get_settings.cache_clear()
            ai_chat.settings.ai_provider = "mock"
            ai_chat.settings.ai_model = ""
            ai_chat.settings.ai_gemini_api_key = ""
            ai_chat_service_module.settings.ai_provider = "mock"
            ai_chat_service_module.settings.ai_model = ""
            ai_chat_service_module.settings.ai_gemini_api_key = ""

            created = await ai_chat.create_conversation(
                ai_chat.AiChatConversationCreate(title="Ambiente externo Gemini"),
                self.session,
                self.user_a,
            )

        self.assertEqual("mock", created.provider)

    async def test_create_conversation_uses_authenticated_user_id_and_sends_message(self) -> None:
        created = await ai_chat.create_conversation(
            ai_chat.AiChatConversationCreate(title="Minha conversa"),
            self.session,
            self.user_a,
        )
        self.assertEqual(self.user_a.id, created.user_id)
        self.assertEqual("mock", created.provider)

        detail = await ai_chat.send_message(
            created.id,
            ai_chat.AiChatMessageCreate(content="Olá IA"),
            self.session,
            self.user_a,
        )
        self.assertEqual(["user", "assistant"], [message.role for message in detail.messages])
        self.assertIn("Olá IA", detail.messages[1].content)
        self.assertTrue(detail.messages[1].content.startswith("Modo mock: resposta simulada para validação do Painel ENS-Quality."))
        self.assertEqual("mock", detail.messages[1].provider)

        persisted_messages = self.session.messages[created.id]
        self.assertEqual(["user", "assistant"], [row["entity"].role for row in persisted_messages])
        self.assertIn("Olá IA", persisted_messages[1]["entity"].content)

    async def test_api_accepts_message_with_mode_and_persists_assistant_message(self) -> None:
        created = await ai_chat.create_conversation(
            ai_chat.AiChatConversationCreate(title="Modo"),
            self.session,
            self.user_a,
        )

        detail = await ai_chat.send_message(
            created.id,
            ai_chat.AiChatMessageCreate(content="eu precisa configura o notebook", mode="fix_text"),
            self.session,
            self.user_a,
        )

        self.assertEqual(["user", "assistant"], [message.role for message in detail.messages])
        self.assertIn("Texto revisado", detail.messages[1].content)
        self.assertEqual("fix_text", detail.messages[0].extra_metadata["mode"])
        self.assertEqual("fix_text", detail.messages[1].extra_metadata["mode"])

    async def test_create_conversation_with_initial_message_returns_and_persists_assistant_message(self) -> None:
        created = await ai_chat.create_conversation(
            ai_chat.AiChatConversationCreate(title="Inicial", message="Resumir atendimento", mode="summarize"),
            self.session,
            self.user_a,
        )

        self.assertEqual("mock", created.provider)
        self.assertEqual(["user", "assistant"], [message.role for message in created.messages])
        self.assertIn("Resumo", created.messages[1].content)
        self.assertEqual("mock", created.messages[1].provider)

        persisted_messages = self.session.messages[created.id]
        self.assertEqual(["user", "assistant"], [row["entity"].role for row in persisted_messages])
        self.assertIn("Resumo", persisted_messages[1]["entity"].content)

    async def test_user_cannot_open_or_send_message_to_other_users_conversation(self) -> None:
        created = await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="B"), self.session, self.user_b)

        with self.assertRaises(HTTPException) as opened:
            await ai_chat.get_conversation(created.id, self.session, self.user_a)
        with self.assertRaises(HTTPException) as sent:
            await ai_chat.send_message(created.id, ai_chat.AiChatMessageCreate(content="invadir"), self.session, self.user_a)

        self.assertEqual(404, opened.exception.status_code)
        self.assertEqual(404, sent.exception.status_code)

    async def test_message_above_limit_returns_422(self) -> None:
        created = await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="Limite"), self.session, self.user_a)

        with self.assertRaises(HTTPException) as ctx:
            await ai_chat.send_message(created.id, ai_chat.AiChatMessageCreate.model_construct(content="x" * 12001), self.session, self.user_a)

        self.assertEqual(422, ctx.exception.status_code)

    async def test_health_endpoint_returns_provider_configuration_status(self) -> None:
        original = ai_chat.get_ai_provider_health
        ai_chat.get_ai_provider_health = lambda _settings: {
            "provider": "openai",
            "configured": False,
            "status": "configuration_error",
            "detail": "openai_api_key_missing",
        }
        try:
            health = await ai_chat.health()
        finally:
            ai_chat.get_ai_provider_health = original

        self.assertEqual("openai", health["provider"])
        self.assertFalse(health["configured"])
        self.assertEqual("configuration_error", health["status"])
        self.assertEqual("openai_api_key_missing", health["detail"])
        self.assertNotIn("api_key", health)

    async def test_provider_configuration_error_returns_clear_503(self) -> None:
        created = await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="Provider"), self.session, self.user_a)
        original_service = ai_chat.AiChatService

        class BrokenService(original_service):
            async def send_message(self, conversation, payload, user_id):  # noqa: ANN001
                raise AiProviderConfigurationError("openai_api_key_missing")

        ai_chat.AiChatService = BrokenService
        try:
            with self.assertRaises(HTTPException) as ctx:
                await ai_chat.send_message(created.id, ai_chat.AiChatMessageCreate(content="Olá"), self.session, self.user_a)
        finally:
            ai_chat.AiChatService = original_service

        self.assertEqual(503, ctx.exception.status_code)
        self.assertEqual("ai_provider_configuration_error: openai_api_key_missing", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
