from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.routes import ai_chat  # noqa: E402
from app.core.config.settings import Settings, get_settings  # noqa: E402
from app.domains.ai_chat import service as ai_chat_service_module  # noqa: E402
from app.domains.ai_chat.providers import (  # noqa: E402
    AiProviderConfigurationError,
    AiProviderMessage,
    AiProviderRequestError,
    OllamaLanProvider,
    OllamaProvider,
    build_ai_provider,
    get_ai_provider_health,
)
from app.shared.enums import Role  # noqa: E402

from tests.test_ai_chat_api import FakeAiChatSession  # noqa: E402


class OllamaProviderTest(unittest.IsolatedAsyncioTestCase):
    async def test_build_provider_supports_ollama_defaults(self) -> None:
        settings = Settings(ai_provider="ollama")

        provider = build_ai_provider(settings)

        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual("ollama", provider.provider)
        self.assertEqual("http://127.0.0.1:11434", provider.base_url)
        self.assertEqual("qwen3:1.7b-64k", provider.model)
        self.assertEqual(120, provider.timeout_seconds)

    async def test_ollama_provider_sends_api_chat_payload_and_returns_text(self) -> None:
        captured: dict[str, object] = {}

        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:
            captured.update({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
            return {
                "model": "qwen3:1.7b-64k",
                "message": {"role": "assistant", "content": "Resposta via Ollama"},
                "prompt_eval_count": 10,
                "eval_count": 5,
            }

        provider = OllamaProvider(
            base_url="http://127.0.0.1:11434",
            model="qwen3:1.7b-64k",
            timeout_seconds=120,
            http_post=fake_post,
        )

        response = await provider.generate(
            [
                AiProviderMessage(role="system", content="Sistema"),
                AiProviderMessage(role="user", content="Olá"),
            ],
            mode="general",
        )

        self.assertEqual("Resposta via Ollama", response.content)
        self.assertEqual("ollama", response.provider)
        self.assertEqual("qwen3:1.7b-64k", response.model)
        self.assertEqual(10, response.prompt_tokens)
        self.assertEqual(5, response.completion_tokens)
        self.assertEqual("http://127.0.0.1:11434/api/chat", captured["url"])
        self.assertEqual(120, captured["timeout"])
        self.assertEqual({"Content-Type": "application/json"}, captured["headers"])
        payload = captured["payload"]
        self.assertIsInstance(payload, dict)
        self.assertEqual("qwen3:1.7b-64k", payload["model"])
        self.assertFalse(payload["stream"])
        self.assertEqual(
            [{"role": "system", "content": "Sistema"}, {"role": "user", "content": "Olá"}],
            payload["messages"],
        )

    async def test_ollama_provider_timeout_is_controlled_error(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            raise TimeoutError("timed out")

        provider = OllamaProvider(http_post=fake_post)

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_timeout", str(ctx.exception))

    async def test_ollama_provider_connection_failure_is_controlled_error(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            raise OSError("connection refused")

        provider = OllamaProvider(http_post=fake_post)

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_request_failed", str(ctx.exception))

    async def test_ollama_provider_model_missing_is_controlled_error(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            raise AiProviderRequestError("provider_http_404")

        provider = OllamaProvider(http_post=fake_post)

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_model_unavailable", str(ctx.exception))

    async def test_ollama_provider_invalid_json_shape_is_controlled_error(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            return {"message": {"role": "assistant"}}

        provider = OllamaProvider(http_post=fake_post)

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_empty_response", str(ctx.exception))

    async def test_endpoint_preserves_contract_and_rejects_frontend_base_url_choice(self) -> None:
        env_patch = patch.dict(
            os.environ,
            {
                "AI_PROVIDER": "ollama",
                "AI_MODEL": "",
                "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
                "OLLAMA_MODEL": "qwen3:1.7b-64k",
                "OLLAMA_TIMEOUT_SECONDS": "120",
            },
            clear=False,
        )
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.addCleanup(get_settings.cache_clear)

        session = FakeAiChatSession()
        user = SimpleNamespace(id=__import__("uuid").uuid4(), name="Operador", email="op@example.test", role=Role.TECHNICIAN)
        original_enabled = ai_chat.settings.enable_ai_chat
        original_route_provider = ai_chat.settings.ai_provider
        original_route_model = ai_chat.settings.ai_model
        original_service_provider = ai_chat_service_module.settings.ai_provider
        original_service_model = ai_chat_service_module.settings.ai_model
        original_factory = ai_chat_service_module.build_ai_provider

        class FakeOllama:
            provider = "ollama"
            model = "qwen3:1.7b-64k"

            async def generate(self, messages, mode=None):  # noqa: ANN001, ARG002
                from app.domains.ai_chat.providers import AiProviderResponse

                return AiProviderResponse(content="OK via Ollama", provider="ollama", model=self.model)

        ai_chat.settings.enable_ai_chat = True
        ai_chat.settings.ai_provider = "ollama"
        ai_chat.settings.ai_model = ""
        ai_chat_service_module.settings.ai_provider = "ollama"
        ai_chat_service_module.settings.ai_model = ""
        ai_chat_service_module.build_ai_provider = lambda _settings: FakeOllama()
        try:
            created = await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(title="Ollama"), session, user)
            detail = await ai_chat.send_message(
                created.id,
                ai_chat.AiChatMessageCreate(content="Responda OK", ollama_base_url="http://evil.example"),
                session,
                user,
            )
        finally:
            ai_chat.settings.enable_ai_chat = original_enabled
            ai_chat.settings.ai_provider = original_route_provider
            ai_chat.settings.ai_model = original_route_model
            ai_chat_service_module.settings.ai_provider = original_service_provider
            ai_chat_service_module.settings.ai_model = original_service_model
            ai_chat_service_module.build_ai_provider = original_factory

        self.assertEqual("ollama", detail.provider)
        self.assertEqual("qwen3:1.7b-64k", detail.model)
        self.assertEqual(["user", "assistant"], [message.role for message in detail.messages])
        self.assertEqual("OK via Ollama", detail.messages[-1].content)
        self.assertNotIn("ollama_base_url", detail.messages[0].extra_metadata)

    def test_ollama_health_reports_localhost_without_secrets(self) -> None:
        settings = Settings(ai_provider="ollama", ollama_model="qwen3:1.7b-64k")

        health = get_ai_provider_health(settings)

        self.assertEqual("ollama", health["provider"])
        self.assertTrue(health["configured"])
        self.assertEqual("ok", health["status"])
        self.assertEqual("qwen3:1.7b-64k", health["model"])
        self.assertNotIn("base_url", health)
        self.assertNotIn("127.0.0.1", str(health))
        self.assertNotIn("token", str(health).lower())
        self.assertNotIn("api_key", str(health).lower())

    async def test_build_provider_supports_ollama_lan_openai_compatible_runtime(self) -> None:
        settings = Settings(
            ai_provider="ollama-lan",
            ollama_base_url="http://192.168.0.103:11434/v1",
            ollama_model="qwen3:1.7b-64k",
            ollama_allowed_hosts="localhost,127.0.0.1,::1,192.168.0.103",
        )

        provider = build_ai_provider(settings)

        self.assertIsInstance(provider, OllamaLanProvider)
        self.assertEqual("ollama-lan", provider.provider)
        self.assertEqual("http://192.168.0.103:11434/v1", provider.base_url)
        self.assertEqual("qwen3:1.7b-64k", provider.model)
        self.assertEqual(120, provider.timeout_seconds)

    async def test_build_provider_supports_ai_chat_provider_alias(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AI_CHAT_PROVIDER": "ollama-lan",
                "AI_PROVIDER": "mock",
                "OLLAMA_BASE_URL": "http://192.168.0.103:11434/v1",
                "OLLAMA_ALLOWED_HOSTS": "localhost,127.0.0.1,::1,192.168.0.103",
            },
            clear=False,
        ):
            settings = Settings()

        provider = build_ai_provider(settings)

        self.assertIsInstance(provider, OllamaLanProvider)
        self.assertEqual("ollama-lan", provider.provider)

    async def test_ollama_lan_provider_sends_v1_chat_completions_payload_and_returns_text(self) -> None:
        captured: dict[str, object] = {}

        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:
            captured.update({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
            return {
                "choices": [{"message": {"role": "assistant", "content": "OK via Ollama LAN."}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 5},
            }

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434/v1",
            model="qwen3:1.7b-64k",
            timeout_seconds=120,
            allowed_hosts=["localhost", "127.0.0.1", "::1", "192.168.0.103"],
            http_post=fake_post,
        )

        response = await provider.generate(
            [
                AiProviderMessage(role="system", content="Sistema"),
                AiProviderMessage(role="user", content="Olá"),
            ],
            mode="general",
        )

        self.assertEqual("OK via Ollama LAN.", response.content)
        self.assertEqual("ollama-lan", response.provider)
        self.assertEqual("qwen3:1.7b-64k", response.model)
        self.assertEqual(11, response.prompt_tokens)
        self.assertEqual(5, response.completion_tokens)
        self.assertEqual("http://192.168.0.103:11434/v1/chat/completions", captured["url"])
        self.assertNotIn("/api/chat", str(captured["url"]))
        self.assertEqual({"Content-Type": "application/json"}, captured["headers"])
        payload = captured["payload"]
        self.assertIsInstance(payload, dict)
        self.assertEqual("qwen3:1.7b-64k", payload["model"])
        self.assertFalse(payload["stream"])
        self.assertEqual(
            [{"role": "system", "content": "Sistema"}, {"role": "user", "content": "Olá"}],
            payload["messages"],
        )

    async def test_ollama_lan_base_url_without_v1_appends_v1_once(self) -> None:
        captured: dict[str, object] = {}

        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            captured["url"] = url
            return {"choices": [{"message": {"content": "OK"}}]}

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434",
            allowed_hosts=["192.168.0.103"],
            http_post=fake_post,
        )

        await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("http://192.168.0.103:11434/v1/chat/completions", captured["url"])

    async def test_ollama_lan_blocks_lan_host_without_explicit_allowlist(self) -> None:
        with self.assertRaises(AiProviderConfigurationError) as ctx:
            OllamaLanProvider(base_url="http://192.168.0.103:11434/v1")

        self.assertEqual("ollama_lan_host_not_allowed", str(ctx.exception))

    async def test_ollama_lan_blocks_public_ip_even_when_listed(self) -> None:
        with self.assertRaises(AiProviderConfigurationError) as ctx:
            OllamaLanProvider(base_url="http://8.8.8.8:11434/v1", allowed_hosts=["8.8.8.8"])

        self.assertEqual("ollama_lan_host_not_allowed", str(ctx.exception))

    async def test_ollama_lan_blocks_wildcard_allowlist(self) -> None:
        with self.assertRaises(AiProviderConfigurationError) as ctx:
            OllamaLanProvider(base_url="http://192.168.0.103:11434/v1", allowed_hosts=["*"])

        self.assertEqual("ollama_allowed_hosts_wildcard_not_allowed", str(ctx.exception))

    async def test_ollama_lan_invalid_choices_shape_is_controlled_error(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            return {"message": {"content": "legacy api shape"}}

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434/v1",
            allowed_hosts=["192.168.0.103"],
            http_post=fake_post,
        )

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_lan_empty_response", str(ctx.exception))

    async def test_ollama_lan_strips_think_blocks_before_returning_text(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "<think>Raciocinio interno</think>OK via Ollama LAN.",
                        },
                        "finish_reason": "stop",
                    }
                ]
            }

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434/v1",
            allowed_hosts=["192.168.0.103"],
            http_post=fake_post,
        )

        response = await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("OK via Ollama LAN.", response.content)

    async def test_ollama_lan_strips_unclosed_think_block_and_preserves_final_answer(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "<think>\nLinha 1\nLinha 2\n\nOK via Ollama LAN.",
                        },
                        "finish_reason": "stop",
                    }
                ]
            }

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434/v1",
            allowed_hosts=["192.168.0.103"],
            http_post=fake_post,
        )

        response = await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("OK via Ollama LAN.", response.content)

    async def test_ollama_lan_raises_when_think_sanitization_removes_everything(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "<think>Somente raciocinio interno</think>",
                        },
                        "finish_reason": "stop",
                    }
                ]
            }

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434/v1",
            allowed_hosts=["192.168.0.103"],
            http_post=fake_post,
        )

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_lan_empty_response", str(ctx.exception))

    async def test_ollama_lan_failure_does_not_fallback_to_mock(self) -> None:
        async def fake_post(url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict[str, object]:  # noqa: ARG001
            raise OSError("connection refused")

        provider = OllamaLanProvider(
            base_url="http://192.168.0.103:11434/v1",
            allowed_hosts=["192.168.0.103"],
            http_post=fake_post,
        )

        with self.assertRaises(AiProviderRequestError) as ctx:
            await provider.generate([AiProviderMessage(role="user", content="Olá")])

        self.assertEqual("ollama_lan_request_failed", str(ctx.exception))

    def test_ollama_lan_health_reports_provider_without_base_url(self) -> None:
        settings = Settings(
            ai_provider="ollama-lan",
            ollama_base_url="http://192.168.0.103:11434/v1",
            ollama_allowed_hosts="localhost,127.0.0.1,::1,192.168.0.103",
            ollama_model="qwen3:1.7b-64k",
        )

        health = get_ai_provider_health(settings)

        self.assertEqual("ollama-lan", health["provider"])
        self.assertTrue(health["configured"])
        self.assertEqual("ok", health["status"])
        self.assertEqual("qwen3:1.7b-64k", health["model"])
        self.assertNotIn("base_url", health)
        self.assertNotIn("192.168.0.103", str(health))
        self.assertNotIn("token", str(health).lower())
        self.assertNotIn("api_key", str(health).lower())


if __name__ == "__main__":
    unittest.main()
