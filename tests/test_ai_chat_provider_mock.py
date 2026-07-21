from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config.settings import get_settings  # noqa: E402
from app.domains.ai_chat import providers as ai_chat_providers_module  # noqa: E402
from app.domains.ai_chat.providers import AiProviderMessage, MockAiProvider, build_ai_provider  # noqa: E402


def force_ai_chat_mock_environment() -> patch:
    env_patch = patch.dict(
        os.environ,
        {
            "AI_PROVIDER": "mock",
            "AI_MOCK_ENABLED": "true",
            "AI_MODEL": "",
            "AI_GEMINI_API_KEY": "",
            "AI_OPENAI_API_KEY": "",
        },
        clear=False,
    )
    env_patch.start()
    get_settings.cache_clear()
    return env_patch


class AiChatMockProviderTest(unittest.IsolatedAsyncioTestCase):
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

    async def test_mock_provider_generates_generic_response_without_external_key_or_network(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="Olá IA")], mode="general")

        self.assertEqual("mock", response.provider)
        self.assertIsNone(response.model)
        self.assertTrue(response.content.startswith("Modo mock: resposta simulada para validação do Painel ENS-Quality."))
        self.assertIn("Sugestões de uso", response.content)
        self.assertIn("Olá IA", response.content)
        self.assertIn("não é Gemini", response.content)
        self.assertIn("não usou internet", response.content)

    async def test_mock_provider_generates_text_correction_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="eu precisa configura o notebook")], mode="fix_text")

        self.assertIn("Texto revisado", response.content)
        self.assertIn("Eu preciso configurar o notebook", response.content)
        self.assertIn("mock", response.content.lower())

    async def test_mock_provider_generates_itil_draft_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="Gerar rascunho para abertura de chamado ITIL")], mode="draft_ticket")

        self.assertIn("Título", response.content)
        self.assertIn("Descrição", response.content)
        self.assertIn("Impacto", response.content)
        self.assertIn("Urgência", response.content)
        self.assertIn("Categoria sugerida", response.content)
        self.assertIn("Ação realizada", response.content)
        self.assertIn("Validação", response.content)
        self.assertIn("Próximo passo", response.content)

    async def test_mock_provider_generates_ticket_update_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="Cliente aguardando validação")], mode="update_ticket")

        self.assertIn("Atualização de chamado", response.content)
        self.assertIn("Situação atual", response.content)
        self.assertIn("Próximo passo", response.content)

    async def test_mock_provider_generates_resolution_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="Foi reinstalado o driver")], mode="resolution")

        self.assertIn("Solução aplicada", response.content)
        self.assertIn("Validação", response.content)

    async def test_mock_provider_generates_summary_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="Resumir a conversa")], mode="summarize")

        self.assertIn("Resumo", response.content)
        self.assertIn("-", response.content)

    async def test_mock_provider_generates_improve_tone_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="manda o notebook logo")], mode="improve_tone")

        self.assertIn("Versão corporativa", response.content)
        self.assertIn("cordial", response.content.lower())

    async def test_mock_provider_generates_service_macro_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="atendimento concluído")], mode="service_macro")

        self.assertIn("Macro de atendimento", response.content)
        self.assertIn("Prezado", response.content)

    async def test_mock_provider_generates_inventory_response(self) -> None:
        provider = MockAiProvider()

        response = await provider.generate([AiProviderMessage(role="user", content="Orientar movimentação de notebook do inventário")], mode="asset_guidance")

        self.assertIn("Checklist de inventário/movimentação", response.content)
        self.assertIn("patrimônio/serial", response.content)
        self.assertIn("confirmar colaborador atual", response.content)
        self.assertIn("registrar movimentação", response.content)
        self.assertIn("gerar macro", response.content)
        self.assertIn("auditar histórico", response.content)

    def test_build_ai_provider_defaults_to_mock(self) -> None:
        class MinimalSettings:
            ai_provider = "mock"
            ai_model = ""
            mock_provider_allowed = True

        provider = build_ai_provider(MinimalSettings())

        self.assertIsInstance(provider, MockAiProvider)


if __name__ == "__main__":
    unittest.main()
