from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ApoemaFrontendErrorContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = (ROOT / "frontend/itam-platform/src/apoema/lib/apoemaChatApi.ts").read_text(encoding="utf-8")
        cls.page = (ROOT / "frontend/itam-platform/src/apoema/pages/ChatPage.tsx").read_text(encoding="utf-8")
        cls.message = (ROOT / "frontend/itam-platform/src/apoema/components/ChatMessage.tsx").read_text(encoding="utf-8")
        cls.css = (ROOT / "frontend/itam-platform/src/apoema/styles/apoema.css").read_text(encoding="utf-8")
        cls.types = (ROOT / "frontend/itam-platform/src/apoema/types.ts").read_text(encoding="utf-8")

    def test_adapter_defines_typed_api_error_and_status_classifier(self) -> None:
        for snippet in (
            "export type ApoemaApiErrorKind",
            "export class ApoemaApiError extends Error",
            'return "auth_required"',
            'return "forbidden"',
            'return "rate_limited"',
            'return "validation_error"',
            'return "backend_error"',
            'kind === "network_unavailable"',
        ):
            self.assertIn(snippet, self.api + self.types)

    def test_http_errors_are_classified_separately_from_network_fallback(self) -> None:
        self.assertIn('if (error instanceof ApoemaApiError && error.kind === "network_unavailable")', self.api)
        self.assertGreaterEqual(self.api.count("mockApoemaResponse"), 1)
        self.assertGreaterEqual(self.api.count('error.kind === "network_unavailable"'), 1)
        self.assertIn('throw error;', self.api)
        self.assertIn("Backend indisponível. Exibindo catálogo local de fallback.", self.api)
        self.assertIn("Backend indisponível. Exibindo resposta local de fallback.", self.api)

    def test_http_statuses_are_explicitly_handled_in_the_adapter(self) -> None:
        for status in ("401", "403", "422", "429"):
            self.assertIn(f"status === {status}", self.api)
        self.assertIn("status >= 500 && status < 600", self.api)

    def test_chat_page_renders_distinct_error_and_fallback_states(self) -> None:
        for snippet in (
            "Sua sessão expirou ou não foi autenticada. Faça login novamente para usar o chat.",
            "Você não tem permissão para usar este recurso.",
            "Limite temporário atingido. Aguarde alguns instantes e tente novamente.",
            "O backend do chat retornou erro. Tente novamente em instantes.",
            "Chat IA",
            "Hermes real no centro da operação",
            "Hermes está analisando a solicitação...",
        ):
            self.assertIn(snippet, self.page + self.message)

    def test_fallback_messages_are_visually_marked(self) -> None:
        self.assertIn("data-role={message.role}", self.message)
        self.assertIn("Copiar resposta", self.message)
        self.assertIn("bg-white/[0.04]", self.message)


if __name__ == "__main__":
    unittest.main()
