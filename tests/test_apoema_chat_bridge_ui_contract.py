from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOEMA = ROOT / "frontend" / "itam-platform" / "src" / "apoema"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ApoemaChatBridgeUiContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chat_page = read(APOEMA / "pages" / "ChatPage.tsx")
        cls.bridge_api = read(APOEMA / "lib" / "apoemaChatBridgeApi.ts")
        cls.chat_message = read(APOEMA / "components" / "ChatMessage.tsx")
        cls.chat_composer = read(APOEMA / "components" / "ChatComposer.tsx")
        cls.chat_sidebar = read(APOEMA / "components" / "ChatConversationSidebar.tsx")
        cls.app = read(APOEMA / "ApoemaApp.tsx")
        cls.types = read(APOEMA / "types.ts")

    def test_bridge_client_uses_ai_chat_backend_contract(self) -> None:
        for snippet in (
            'const API_BASE = "/api/v1"',
            '"/ai-chat/health"',
            '"/ai-chat/providers"',
            '"/ai-chat/conversations"',
            '/ai-chat/conversations/${encodeURIComponent(conversationId)}',
            '/ai-chat/conversations/${encodeURIComponent(conversationId)}/messages',
            '"/ai-chat/message"',
            'network_unavailable',
            'Backend indisponível. Exibindo resposta local de fallback.',
        ):
            self.assertIn(snippet, self.bridge_api)

    def test_chat_page_uses_backend_conversations_as_primary_source(self) -> None:
        self.assertIn("listAiChatConversations", self.chat_page)
        self.assertIn("getAiChatConversation", self.chat_page)
        self.assertIn("createAiChatConversation", self.chat_page)
        self.assertIn("sendAiChatConversationMessage", self.chat_page)
        self.assertNotIn("apoemaConversations", self.chat_page)
        self.assertNotIn("apoemaInitialMessages", self.chat_page)
        self.assertNotIn("sendAiMessage", self.chat_page)
        self.assertNotIn("FileDropzone", self.chat_page)
        self.assertNotIn("attachmentWarning", self.chat_page)

    def test_chat_ui_keeps_auth_errors_honest_without_fallback_masking(self) -> None:
        for snippet in (
            "Sua sessão expirou ou não foi autenticada. Faça login novamente para usar o Chat de IA.",
            "Você não tem permissão para usar este recurso.",
            "Limite de uso atingido. Aguarde alguns instantes e tente novamente.",
            "O backend de IA retornou um erro. Tente novamente em instantes.",
            'providerLoadState === "error"',
            'providerLoadState === "fallback"',
            "Fallback local ativo",
            'kind === "network_unavailable"',
        ):
            self.assertIn(snippet, self.chat_page + self.bridge_api)

    def test_chat_ui_does_not_invent_streaming_cancel_or_attachments(self) -> None:
        for snippet in ("EventSource", "getReader", "AbortController", "stream", "attachment", "artifact"):
            self.assertNotIn(snippet, self.chat_page.lower())
            self.assertNotIn(snippet, self.bridge_api.lower())

    def test_chat_ui_does_not_call_providers_directly_or_expose_provider_secrets(self) -> None:
        forbidden_patterns = [
            re.compile(r"from\s+['\"](?:openai|@google|googleapis|@google-cloud|ollama|composio)"),
            re.compile(r"https?://[^'\"]*(?:openai|gemini|googleapis|vertex|imagen|ollama|composio)", re.IGNORECASE),
            re.compile(r"\b(?:apiKey|api_key|providerKey|VITE_[A-Z0-9_]*KEY|process\.env)\b"),
            re.compile(r"sk-[A-Za-z0-9_-]+|ghp_[A-Za-z0-9_-]+|xoxb-[A-Za-z0-9_-]+|AKIA[A-Z0-9]{16}|BEGIN .*PRIVATE KEY", re.IGNORECASE),
        ]
        for content in (self.chat_page, self.bridge_api, self.chat_message, self.chat_composer, self.chat_sidebar, self.types):
            for pattern in forbidden_patterns:
                self.assertIsNone(pattern.search(content), f"direct provider or secret-like material found: {pattern.pattern}")

    def test_chat_route_remains_canonical_and_no_legacy_alias_reappears(self) -> None:
        self.assertIn('path="chat" element={<ChatPage />}', self.app)
        self.assertIn('path="artifacts" element={<ArtifactsPage />}', self.app)
        self.assertNotIn('path: "/artifacts"', self.app)
        self.assertNotIn('legacyCompatibilityRoutes', self.app)
        self.assertNotIn('legacyApoemaAliasRoutes', self.app)
        self.assertNotIn('restore AppShell', self.chat_page)


if __name__ == "__main__":
    unittest.main()
