from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.core.config.settings import get_settings
from app.domains.ai_chat import providers as ai_chat_providers_module
from app.domains.ai_chat.models import AiChatConversation, AiChatMessage
from app.domains.ai_chat.providers import (
    AiProviderConfigurationError,
    AiProviderMessage,
    GeminiProvider,
    MockAiProvider,
    OpenAIProvider,
    build_ai_provider,
    get_ai_provider_health,
)
from app.domains.ai_chat.schemas import AiChatConversationCreate, AiChatMessageCreate


def force_ai_chat_mock_environment() -> patch:
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
    return env_patch


class AiChatMvpContractTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.env_patch = force_ai_chat_mock_environment()
        self.addCleanup(self.env_patch.stop)
        self.addCleanup(get_settings.cache_clear)
        self.urlopen_patch = patch.object(
            ai_chat_providers_module.urllib.request,
            "urlopen",
            side_effect=AssertionError("unit tests must not call urllib.request.urlopen"),
        )
        self.urlopen_patch.start()
        self.addCleanup(self.urlopen_patch.stop)

    def test_settings_contract_uses_only_approved_ai_env_names(self) -> None:
        from app.core.config.settings import Settings

        fields = Settings.model_fields
        self.assertEqual("mock", fields["ai_provider"].default)
        self.assertEqual("", fields["ai_model"].default)
        self.assertEqual("", fields["ai_gemini_api_key"].default)
        self.assertEqual("", fields["ai_openai_api_key"].default)
        self.assertEqual(30, fields["ai_timeout_seconds"].default)
        self.assertEqual(12000, fields["ai_max_input_chars"].default)
        self.assertEqual(1000, fields["ai_max_output_tokens"].default)
        self.assertNotIn("ai_api_key", fields)
        self.assertNotIn("gemini_api_key", fields)
        self.assertNotIn("openai_api_key", fields)

    def test_settings_prefers_panel_ai_openai_api_key(self) -> None:
        from app.core.config.settings import Settings

        with patch.dict(
            "os.environ",
            {"AI_OPENAI_API_KEY": "panel-key", "OPENAI_API_KEY": "external-key"},
            clear=False,
        ):
            settings = Settings()

        self.assertEqual("panel-key", settings.ai_openai_api_key)
        self.assertEqual("panel-key", settings.openai_api_key)

    def test_settings_bridges_external_openai_key_in_memory_only(self) -> None:
        from app.core.config.settings import Settings

        with patch.dict("os.environ", {"OPENAI_API_KEY": "external-key"}, clear=False):
            with patch.dict("os.environ", {"AI_OPENAI_API_KEY": ""}, clear=False):
                settings = Settings()

        self.assertEqual("external-key", settings.ai_openai_api_key)
        self.assertEqual("external-key", settings.openai_api_key)

    def test_models_use_extra_metadata_python_attribute_for_metadata_column(self) -> None:
        self.assertIn("extra_metadata", AiChatConversation.__mapper__.attrs.keys())
        self.assertIn("extra_metadata", AiChatMessage.__mapper__.attrs.keys())
        self.assertEqual("metadata", AiChatConversation.__table__.c.metadata.name)
        self.assertEqual("metadata", AiChatMessage.__table__.c.metadata.name)

    def test_payload_limits_are_mvp_limits(self) -> None:
        valid = AiChatMessageCreate(content="x" * 12000)
        self.assertEqual(12000, len(valid.content))
        oversized = AiChatMessageCreate(content="x" * 12001)
        self.assertEqual(12001, len(oversized.content))
        conversation = AiChatConversationCreate(title="Teste", message="Olá", mode="general")
        self.assertEqual("Teste", conversation.title)
        self.assertEqual("general", conversation.mode)

    def test_ai_chat_message_accepts_optional_mode_without_requiring_it(self) -> None:
        without_mode = AiChatMessageCreate(content="Olá")
        with_mode = AiChatMessageCreate(content="Olá", mode="draft_ticket")

        self.assertIsNone(without_mode.mode)
        self.assertEqual("draft_ticket", with_mode.mode)

    def test_build_provider_supports_mock_default_gemini_and_openai(self) -> None:
        class DefaultSettings:
            ai_provider = ""
            ai_model = ""
            ai_gemini_api_key = ""
            openai_api_key = ""
            ai_timeout_seconds = 30
            ai_max_output_tokens = 1000

        class GeminiSettings:
            ai_provider = "gemini"
            ai_model = "gemini-test"
            ai_gemini_api_key = "test-gemini-key"
            openai_api_key = ""
            ai_timeout_seconds = 6
            ai_max_output_tokens = 222

        class OpenAISettings:
            ai_provider = "openai"
            ai_model = "gpt-4o-mini"
            ai_gemini_api_key = ""
            openai_api_key = "sk-test"
            ai_timeout_seconds = 7
            ai_max_output_tokens = 321

        class UnsupportedSettings:
            ai_provider = "anthropic"
            ai_model = ""
            ai_gemini_api_key = ""
            openai_api_key = ""
            ai_timeout_seconds = 30
            ai_max_output_tokens = 1000

        self.assertIsInstance(build_ai_provider(DefaultSettings()), MockAiProvider)
        self.assertIsInstance(build_ai_provider(GeminiSettings()), GeminiProvider)
        self.assertIsInstance(build_ai_provider(OpenAISettings()), OpenAIProvider)
        with self.assertRaises(ValueError):
            build_ai_provider(UnsupportedSettings())

    def test_gemini_provider_requires_ai_gemini_api_key(self) -> None:
        class GeminiWithoutKeySettings:
            ai_provider = "gemini"
            ai_model = "gemini-2.0-flash"
            ai_gemini_api_key = ""
            ai_timeout_seconds = 30
            ai_max_output_tokens = 1000

        with self.assertRaises(AiProviderConfigurationError) as ctx:
            build_ai_provider(GeminiWithoutKeySettings())
        self.assertEqual("gemini_api_key_missing", str(ctx.exception))

    async def test_gemini_provider_generates_text_with_mocked_http(self) -> None:
        captured: dict[str, object] = {}

        async def fake_http_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:
            captured.update({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
            return {
                "candidates": [
                    {
                        "content": {"parts": [{"text": "Resposta Gemini mockada"}]},
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 8},
            }

        provider = GeminiProvider(
            api_key="test-gemini-key",
            model="gemini-test",
            timeout_seconds=8,
            max_output_tokens=333,
            http_post=fake_http_post,
        )

        response = await provider.generate(
            [
                AiProviderMessage(role="system", content="Instrução segura"),
                AiProviderMessage(role="user", content="Olá Gemini"),
            ]
        )

        self.assertEqual("Resposta Gemini mockada", response.content)
        self.assertEqual("gemini", response.provider)
        self.assertEqual("gemini-test", response.model)
        self.assertEqual(12, response.prompt_tokens)
        self.assertEqual(8, response.completion_tokens)
        self.assertEqual(8, captured["timeout"])
        self.assertEqual("https://generativelanguage.googleapis.com/v1beta/models/gemini-test:generateContent", captured["url"])
        self.assertNotIn("test-gemini-key", captured["url"])
        headers = captured["headers"]
        self.assertIsInstance(headers, dict)
        self.assertEqual("test-gemini-key", headers["x-goog-api-key"])
        payload = captured["payload"]
        self.assertIsInstance(payload, dict)
        self.assertEqual({"temperature": 0.2, "maxOutputTokens": 333}, payload["generationConfig"])
        self.assertEqual({"parts": [{"text": "Instrução segura"}]}, payload["systemInstruction"])
        self.assertEqual([{"role": "user", "parts": [{"text": "Olá Gemini"}]}], payload["contents"])

    def test_openai_provider_requires_openai_api_key(self) -> None:
        class OpenAIWithoutKeySettings:
            ai_provider = "openai"
            ai_model = "gpt-4o-mini"
            openai_api_key = ""
            ai_timeout_seconds = 30
            ai_max_output_tokens = 1000

        with self.assertRaises(AiProviderConfigurationError) as ctx:
            build_ai_provider(OpenAIWithoutKeySettings())
        self.assertEqual("openai_api_key_missing", str(ctx.exception))

    async def test_openai_provider_generates_text_with_mocked_http(self) -> None:
        captured: dict[str, object] = {}

        async def fake_http_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:
            captured.update({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
            return {
                "choices": [{"message": {"content": "Resposta OpenAI mockada"}}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            }

        provider = OpenAIProvider(
            api_key="sk-secret-test",
            model="gpt-test",
            timeout_seconds=9,
            max_output_tokens=456,
            http_post=fake_http_post,
        )

        response = await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("Resposta OpenAI mockada", response.content)
        self.assertEqual("openai", response.provider)
        self.assertEqual("gpt-test", response.model)
        self.assertEqual(11, response.prompt_tokens)
        self.assertEqual(7, response.completion_tokens)
        self.assertEqual(9, captured["timeout"])
        headers = captured["headers"]
        self.assertIsInstance(headers, dict)
        self.assertEqual("Bearer sk-secret-test", headers["Authorization"])
        payload = captured["payload"]
        self.assertIsInstance(payload, dict)
        self.assertEqual("gpt-test", payload["model"])
        self.assertEqual(456, payload["max_tokens"])

    def test_ai_provider_health_reports_configuration_without_secrets(self) -> None:
        class OpenAIWithoutKeySettings:
            ai_provider = "openai"
            ai_model = "gpt-4o-mini"
            ai_gemini_api_key = ""
            openai_api_key = ""
            ai_timeout_seconds = 30
            ai_max_output_tokens = 1000

        health = get_ai_provider_health(OpenAIWithoutKeySettings())

        self.assertEqual("openai", health["provider"])
        self.assertFalse(health["configured"])
        self.assertEqual("configuration_error", health["status"])
        self.assertEqual("openai_api_key_missing", health["detail"])
        self.assertNotIn("api_key", health)

    def test_gemini_provider_health_reports_configuration_without_secrets(self) -> None:
        class GeminiWithoutKeySettings:
            ai_provider = "gemini"
            ai_model = "gemini-2.0-flash"
            ai_gemini_api_key = ""
            ai_timeout_seconds = 30
            ai_max_output_tokens = 1000

        health = get_ai_provider_health(GeminiWithoutKeySettings())

        self.assertEqual("gemini", health["provider"])
        self.assertFalse(health["configured"])
        self.assertEqual("configuration_error", health["status"])
        self.assertEqual("gemini_api_key_missing", health["detail"])
        self.assertNotIn("api_key", health)

    def test_migration_down_revision_is_macros_module(self) -> None:
        import importlib

        migration = importlib.import_module("backend.alembic.versions.0006_ai_chat")
        self.assertEqual("0005_macros_module", migration.down_revision)


if __name__ == "__main__":
    unittest.main()
