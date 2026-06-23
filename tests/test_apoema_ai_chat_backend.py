from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.routes import ai_chat  # noqa: E402
from app.core.config.settings import Settings  # noqa: E402
from app.domains.ai_chat.apoema import build_apoema_provider_catalog, generate_apoema_message  # noqa: E402
from app.domains.ai_chat.providers import AiProviderRequestError  # noqa: E402
from app.domains.ai_chat.schemas import ApoemaChatMessageCreate  # noqa: E402


class ApoemaAiChatBackendTest(unittest.IsolatedAsyncioTestCase):
    def test_provider_catalog_exposes_expected_providers(self) -> None:
        settings = Settings(ai_chat_default_provider="mock")

        catalog = build_apoema_provider_catalog(settings)

        self.assertEqual(["mock", "ollama", "hermes"], [provider.id for provider in catalog.providers])
        self.assertEqual("fallback-local", catalog.providers[0].default_model)
        self.assertEqual("qwen3:4b-64k", catalog.providers[1].default_model)
        self.assertEqual(["qwen3:4b-64k", "qwen2.5-coder:7b"], catalog.providers[1].models)
        self.assertEqual("hermes-agent", catalog.providers[2].default_model)
        self.assertEqual("unconfigured", catalog.providers[2].status)

    async def test_mock_provider_message_returns_ok(self) -> None:
        settings = Settings(ai_chat_default_provider="mock")
        payload = ApoemaChatMessageCreate(
            conversation_id="apoema-test",
            provider="mock",
            model="fallback-local",
            message="Olá Apoema",
            mode="assistente_n2",
        )

        response = await generate_apoema_message(settings, payload)

        self.assertEqual("apoema-test", response.conversation_id)
        self.assertEqual("mock", response.provider)
        self.assertEqual("ok", response.status)
        self.assertTrue(response.content.startswith("Modo mock: resposta simulada para validação do Painel ENS-Quality."))

    async def test_ollama_request_failure_falls_back_without_exposing_secret_or_prompt(self) -> None:
        settings = Settings(ai_chat_default_provider="ollama")
        payload = ApoemaChatMessageCreate(
            conversation_id="apoema-ollama",
            provider="ollama",
            model="qwen3:4b-64k",
            message="Teste com prompt sensível",
            mode="assistente_n2",
        )

        with patch("app.domains.ai_chat.apoema.OllamaProvider.generate", side_effect=AiProviderRequestError("ollama_timeout")):
            response = await generate_apoema_message(settings, payload)

        self.assertEqual("ollama", response.provider)
        self.assertEqual("offline", response.status)
        self.assertIn("Usando fallback local", response.content)
        self.assertNotIn("Teste com prompt sensível", response.error or "")

    async def test_hermes_placeholder_returns_safe_unconfigured_response(self) -> None:
        settings = Settings(ai_chat_default_provider="hermes", hermes_base_url="")
        payload = ApoemaChatMessageCreate(
            conversation_id=None,
            provider="hermes",
            model="hermes-agent",
            message="Resumo de atendimento",
            mode="assistente_n2",
        )

        response = await generate_apoema_message(settings, payload)

        self.assertEqual("hermes", response.provider)
        self.assertEqual("unconfigured", response.status)
        self.assertEqual("hermes-agent", response.model)
        self.assertIn("Usando fallback local", response.content)

    def test_public_routes_exist_without_auth_dependency(self) -> None:
        provider_route = next(route for route in ai_chat.router.routes if getattr(route, "path", None) == "/ai-chat/providers")
        message_route = next(route for route in ai_chat.router.routes if getattr(route, "path", None) == "/ai-chat/message")

        self.assertEqual([], provider_route.dependant.dependencies)
        self.assertEqual([], message_route.dependant.dependencies)


class ApoemaFrontendStaticSafetyTest(unittest.TestCase):
    def test_apoema_frontend_does_not_reference_ollama_or_direct_chat_urls(self) -> None:
        chat_page = (ROOT / "frontend/itam-platform/src/apoema/pages/ChatPage.tsx").read_text(encoding="utf-8")
        api_file = (ROOT / "frontend/itam-platform/src/apoema/lib/apoemaChatApi.ts").read_text(encoding="utf-8")

        forbidden_terms = [
            "localhost:11434",
            "127.0.0.1:11434",
            "/api/chat",
            "OLLAMA_BASE_URL",
            "HERMES_BASE_URL",
        ]
        for term in forbidden_terms:
            self.assertNotIn(term, chat_page)
            self.assertNotIn(term, api_file)


if __name__ == "__main__":
    unittest.main()
