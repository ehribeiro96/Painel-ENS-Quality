from __future__ import annotations

import os
import sys
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.dependencies.auth import require_role  # noqa: E402
from app.api.v1.routes import ai_chat  # noqa: E402
from app.core.config.settings import Settings, get_settings  # noqa: E402
from app.domains.ai_chat import providers as ai_chat_providers_module  # noqa: E402
from app.domains.ai_chat import service as ai_chat_service_module  # noqa: E402
from app.domains.ai_chat.providers import AiProviderRequestError  # noqa: E402
from app.domains.ai_chat.rate_limit import reset_ai_chat_rate_limit_memory  # noqa: E402
from app.shared.enums import Role  # noqa: E402
from fastapi import HTTPException  # noqa: E402

from tests.test_ai_chat_api import FakeAiChatSession  # noqa: E402


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


class AiChatHardeningTest(unittest.IsolatedAsyncioTestCase):
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
        self.user = SimpleNamespace(id=uuid.uuid4(), name="Operador", email="op@example.test", role=Role.TECHNICIAN)
        reset_ai_chat_rate_limit_memory()

    def tearDown(self) -> None:
        reset_ai_chat_rate_limit_memory()

    def test_settings_default_ai_chat_feature_flag_is_disabled_and_limits_exist(self) -> None:
        fields = Settings.model_fields
        self.assertFalse(fields["enable_ai_chat"].default)
        self.assertEqual("mock", fields["ai_provider"].default)
        self.assertEqual(12000, fields["ai_max_input_chars"].default)
        self.assertEqual(1000, fields["ai_max_output_tokens"].default)
        self.assertEqual(30, fields["ai_timeout_seconds"].default)
        self.assertEqual(20, fields["ai_chat_rate_limit_per_minute"].default)

    def test_all_ai_chat_endpoints_are_protected_by_rbac_dependency(self) -> None:
        protected_paths = {
            "/ai-chat/health",
            "/ai-chat/providers",
            "/ai-chat/message",
            "/ai-chat/conversations",
            "/ai-chat/conversations/{conversation_id}",
            "/ai-chat/conversations/{conversation_id}/messages",
        }
        for route in ai_chat.router.routes:
            if getattr(route, "path", None) in protected_paths:
                dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
                self.assertTrue(
                    any(getattr(call, "__closure__", None) for call in dependency_calls) or require_role in dependency_calls,
                    route.path,
                )

    async def test_feature_flag_blocks_conversation_when_disabled(self) -> None:
        original_enabled = ai_chat.settings.enable_ai_chat
        ai_chat.settings.enable_ai_chat = False
        try:
            with self.assertRaises(HTTPException) as ctx:
                await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="Bloqueado"), self.session, self.user)
        finally:
            ai_chat.settings.enable_ai_chat = original_enabled

        self.assertEqual(404, ctx.exception.status_code)
        self.assertEqual("ai_chat_disabled", ctx.exception.detail)

    async def test_safe_metadata_is_recorded_without_api_key_or_full_prompt_in_metadata(self) -> None:
        original_enabled = ai_chat.settings.enable_ai_chat
        ai_chat.settings.enable_ai_chat = True
        try:
            detail = await ai_chat.create_conversation(
                ai_chat.AiChatConversationCreate(title="Seguro", message="Texto sensível de teste"),
                self.session,
                self.user,
            )
        finally:
            ai_chat.settings.enable_ai_chat = original_enabled

        self.assertEqual(["user", "assistant"], [message.role for message in detail.messages])
        user_metadata = detail.messages[0].extra_metadata
        assistant_metadata = detail.messages[1].extra_metadata
        self.assertEqual("mock", user_metadata["provider"])
        self.assertIsNone(user_metadata["model"])
        self.assertEqual(len("Texto sensível de teste"), user_metadata["input_chars"])
        self.assertEqual("ok", user_metadata["status"])
        self.assertEqual("mock", assistant_metadata["provider"])
        self.assertEqual(len(detail.messages[1].content), assistant_metadata["output_chars"])
        self.assertEqual("ok", assistant_metadata["status"])
        combined_metadata = f"{user_metadata} {assistant_metadata}"
        self.assertNotIn("openai_api_key", combined_metadata.lower())
        self.assertNotIn("Texto sensível de teste", combined_metadata)

    async def test_provider_error_records_error_type_as_safe_metadata(self) -> None:
        original_enabled = ai_chat.settings.enable_ai_chat
        original_provider_factory = ai_chat_service_module.build_ai_provider

        class BrokenProvider:
            provider = "mock"
            model = None

            async def generate(self, messages):  # noqa: ANN001
                raise AiProviderRequestError("mock_failure")

        ai_chat.settings.enable_ai_chat = True
        ai_chat_service_module.build_ai_provider = lambda _settings: BrokenProvider()
        try:
            created = await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="Erro"), self.session, self.user)
            with self.assertRaises(HTTPException) as ctx:
                await ai_chat.send_message(created.id, ai_chat.AiChatMessageCreate(content="Falha controlada"), self.session, self.user)
        finally:
            ai_chat.settings.enable_ai_chat = original_enabled
            ai_chat_service_module.build_ai_provider = original_provider_factory

        self.assertEqual(502, ctx.exception.status_code)
        messages = self.session.messages[created.id]
        user_message = messages[-1]["entity"]
        self.assertEqual("error", user_message.extra_metadata["status"])
        self.assertEqual("mock_failure", user_message.extra_metadata["error_type"])
        self.assertNotIn("Falha controlada", str(user_message.extra_metadata))

    async def test_openai_without_key_returns_configuration_error_without_secret_leak(self) -> None:
        original_provider = ai_chat.settings.ai_provider
        original_openai_key = ai_chat.settings.ai_openai_api_key
        ai_chat.settings.ai_provider = "openai"
        ai_chat.settings.ai_openai_api_key = ""
        try:
            health = ai_chat_providers_module.get_ai_provider_health(ai_chat.settings)
        finally:
            ai_chat.settings.ai_provider = original_provider
            ai_chat.settings.ai_openai_api_key = original_openai_key

        self.assertEqual("configuration_error", health["status"])
        self.assertEqual("openai_api_key_missing", health["detail"])
        self.assertNotIn("sk-", str(health).lower())

    async def test_simple_per_user_rate_limit_returns_429(self) -> None:
        original_enabled = ai_chat.settings.enable_ai_chat
        original_limit = ai_chat.settings.ai_chat_rate_limit_per_minute
        ai_chat.settings.enable_ai_chat = True
        ai_chat.settings.ai_chat_rate_limit_per_minute = 1
        try:
            created = await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="Rate"), self.session, self.user)
            await ai_chat.send_message(created.id, ai_chat.AiChatMessageCreate(content="primeira"), self.session, self.user)
            with self.assertRaises(HTTPException) as ctx:
                await ai_chat.send_message(created.id, ai_chat.AiChatMessageCreate(content="segunda"), self.session, self.user)
        finally:
            ai_chat.settings.enable_ai_chat = original_enabled
            ai_chat.settings.ai_chat_rate_limit_per_minute = original_limit

        self.assertEqual(429, ctx.exception.status_code)
        self.assertEqual("ai_chat_rate_limit_exceeded", ctx.exception.detail)


class AiChatFrontendHardeningTest(unittest.TestCase):
    def test_frontend_reads_enable_ai_chat_flag_and_hides_menu_by_default(self) -> None:
        app_shell = ROOT / "frontend/itam-platform/src/components/AppShell.tsx"
        features = (ROOT / "frontend/itam-platform/src/lib/features.ts").read_text(encoding="utf-8")
        vite_config = (ROOT / "frontend/itam-platform/vite.config.ts").read_text(encoding="utf-8")

        self.assertFalse(app_shell.exists())
        self.assertIn("ENABLE_AI_CHAT", features)
        self.assertNotIn('href: "/ai-chat"', (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8"))
        self.assertIn("envPrefix", vite_config)
        self.assertIn("ENABLE_", vite_config)

    def test_ai_chat_page_contains_required_safety_notice(self) -> None:
        legacy_page = ROOT / "frontend/itam-platform/src/pages/AiChatPage.tsx"
        apoema_page = (ROOT / "frontend/itam-platform/src/apoema/pages/ChatPage.tsx").read_text(encoding="utf-8")

        self.assertFalse(legacy_page.exists())
        self.assertIn("Proteções", apoema_page)
        self.assertIn("Sem segredos", apoema_page)
        self.assertIn("Backend indisponível. Exibindo resposta local de fallback.", apoema_page)


if __name__ == "__main__":
    unittest.main()
