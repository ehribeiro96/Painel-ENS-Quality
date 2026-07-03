from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.dependencies.auth import get_current_user  # noqa: E402
from app.api.v1.routes import ai_chat  # noqa: E402
from app.core.config.settings import Settings  # noqa: E402
from app.domains.ai_chat.apoema import build_apoema_provider_catalog, generate_apoema_message  # noqa: E402
from app.domains.ai_chat.providers import AiProviderRequestError, AiProviderResponse  # noqa: E402
from app.domains.ai_chat.schemas import ApoemaChatMessageCreate  # noqa: E402
from fastapi import HTTPException  # noqa: E402


class ApoemaAiChatBackendTest(unittest.IsolatedAsyncioTestCase):
    def test_provider_catalog_exposes_expected_providers(self) -> None:
        settings = Settings(ai_chat_default_provider="mock")

        with patch("app.domains.ai_chat.apoema.get_ai_provider_health") as health_probe:
            health_probe.return_value = {
                "provider": "hermes",
                "configured": True,
                "status": "ok",
                "model": "hermes-agent",
            }
            catalog = build_apoema_provider_catalog(settings)

        self.assertEqual(["mock", "ollama", "hermes"], [provider.id for provider in catalog.providers])
        self.assertEqual("fallback-local", catalog.providers[0].default_model)
        self.assertEqual("qwen3:4b-64k", catalog.providers[1].default_model)
        self.assertEqual(["qwen3:4b-64k", "qwen2.5-coder:7b"], catalog.providers[1].models)
        self.assertEqual("hermes-agent", catalog.providers[2].default_model)
        self.assertEqual("online", catalog.providers[2].status)

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

    async def test_hermes_terminal_provider_returns_real_response_without_fallback(self) -> None:
        settings = Settings(ai_chat_default_provider="hermes", hermes_base_url="")
        payload = ApoemaChatMessageCreate(
            conversation_id=None,
            provider="hermes",
            model="hermes-agent",
            message="Resumo de atendimento",
            mode="assistente_n2",
        )

        with patch("app.domains.ai_chat.apoema.HermesTerminalProvider.generate") as hermes_generate:
            hermes_generate.return_value = AiProviderResponse(
                content="APOEMA-HERMES-OK",
                provider="hermes",
                model="hermes-agent",
            )
            response = await generate_apoema_message(settings, payload)

        self.assertEqual("hermes", response.provider)
        self.assertEqual("ok", response.status)
        self.assertEqual("hermes-agent", response.model)
        self.assertEqual("APOEMA-HERMES-OK", response.content)
        self.assertIsNone(response.error)

    def test_apoema_routes_require_auth_dependency(self) -> None:
        provider_route = next(route for route in ai_chat.router.routes if getattr(route, "path", None) == "/ai-chat/providers")
        message_route = next(route for route in ai_chat.router.routes if getattr(route, "path", None) == "/ai-chat/message")

        self.assertTrue(provider_route.dependant.dependencies)
        self.assertTrue(message_route.dependant.dependencies)
        dependency_calls = {dependency.call for dependency in provider_route.dependant.dependencies + message_route.dependant.dependencies}
        self.assertTrue(any(getattr(call, "__closure__", None) for call in dependency_calls))

    async def test_get_current_user_without_token_returns_401(self) -> None:
        request = SimpleNamespace(state=SimpleNamespace())

        with self.assertRaises(HTTPException) as ctx:
            await get_current_user(request=request, credentials=None, session=SimpleNamespace())

        self.assertEqual(401, ctx.exception.status_code)
        self.assertEqual("missing_token", ctx.exception.detail)


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
