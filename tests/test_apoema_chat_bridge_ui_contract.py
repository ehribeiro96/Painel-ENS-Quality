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
        cls.central_api = read(ROOT / "frontend/itam-platform/src/lib/api.ts")
        cls.chat_message = read(APOEMA / "components" / "ChatMessage.tsx")
        cls.chat_message_content = read(ROOT / "frontend/itam-platform/src/components/ChatMessageContent.tsx")
        cls.chat_composer = read(APOEMA / "components" / "ChatComposer.tsx")
        cls.chat_sidebar = read(APOEMA / "components" / "ChatConversationSidebar.tsx")
        cls.chat_empty_state = read(APOEMA / "components" / "ChatEmptyState.tsx")
        cls.shell = read(APOEMA / "components" / "DonorAppShell.tsx")
        cls.app = read(APOEMA / "ApoemaApp.tsx")
        cls.types = read(ROOT / "frontend/itam-platform/src/lib/types.ts")

    def test_central_client_uses_ai_chat_backend_contract(self) -> None:
        for snippet in (
            'aiChatHealth: (token: string) => request<AiChatProviderHealth>("/ai-chat/health", { token })',
            'aiChatConversations: (token: string) => request<AiChatConversation[]>("/ai-chat/conversations", { token })',
            'aiChatConversation: (token: string, id: string) => request<AiChatConversationDetail>(`/ai-chat/conversations/${id}`, { token })',
            'aiChatCreateConversation: (token: string, payload: AiChatConversationCreate) =>',
            'aiChatSendMessage: (token: string, id: string, contentOrPayload: string | AiChatMessageCreate, mode?: AiChatMessageCreate["mode"]) =>',
        ):
            self.assertIn(snippet, self.central_api)

    def test_chat_page_uses_chat_shell_components_and_central_api(self) -> None:
        for snippet in (
            'import { useAuth } from "@/lib/auth";',
            "ChatConversationSidebar",
            "ChatComposer",
            "ChatMessage",
            "Chat IA",
            "Hermes real no centro da operação",
            "exclusão confirmada e anexos locais honestos",
            "Pronto para operar",
        ):
            self.assertIn(snippet, self.chat_page)
        for snippet in (
            "Chat / Histórico",
            "?new=1",
            "Novo chat",
            "Operação",
            "Automação",
            "Governança",
        ):
            self.assertIn(snippet, self.shell)
        self.assertNotIn("apoemaChatBridgeApi", self.chat_page)
        self.assertNotIn("providerLoadState === \"fallback\"", self.chat_page)
        self.assertNotIn("Fallback local ativo", self.chat_page)
        self.assertNotIn("Mock adapter", self.chat_page)

    def test_new_chat_opens_clean_workspace_without_auto_persisting_empty_conversation(self) -> None:
        self.assertIn('setSearchParams({ new: "1" }', self.chat_page)
        self.assertIn("autoSelect: false", self.chat_page)
        self.assertIn("ApoemaChatBridgeAdapter.createSessionAndSendMessage", self.chat_page)
        self.assertNotIn('ApoemaChatBridgeAdapter.createSession(token, "Nova conversa")', self.chat_page)

    def test_chat_ui_keeps_auth_errors_honest_without_fallback_masking(self) -> None:
        for snippet in (
            "Sua sessão expirou ou não foi autenticada. Faça login novamente para usar o chat.",
            "Você não tem permissão para usar este recurso.",
            "Limite temporário atingido. Aguarde alguns instantes e tente novamente.",
            "O backend do chat retornou erro. Tente novamente em instantes.",
            "Não foi possível concluir a operação. Tente novamente em instantes.",
        ):
            self.assertIn(snippet, self.chat_page)

    def test_chat_ui_uses_safe_lite_rendering_without_dangerous_html(self) -> None:
        for content in (self.chat_page, self.chat_message):
            self.assertNotIn("dangerouslySetInnerHTML", content)
        self.assertNotIn("dangerouslySetInnerHTML", self.chat_message_content)
        self.assertIn("ChatCodeBlock", self.chat_message_content)
        self.assertIn("ChatMessageContent", self.chat_message)
        self.assertIn("Copiar resposta", self.chat_message)

    def test_chat_ui_does_not_call_providers_directly_or_expose_provider_secrets(self) -> None:
        forbidden_patterns = [
            re.compile(r"from\s+['\"](?:openai|@google|googleapis|@google-cloud|ollama|composio)"),
            re.compile(r"https?://[^'\"]*(?:openai|gemini|googleapis|vertex|imagen|ollama|composio)", re.IGNORECASE),
            re.compile(r"\b(?:apiKey|api_key|providerKey|VITE_[A-Z0-9_]*KEY|process\.env)\b"),
            re.compile(r"sk-[A-Za-z0-9_-]+|ghp_[A-Za-z0-9_-]+|xoxb-[A-Za-z0-9_-]+|AKIA[A-Z0-9]{16}|BEGIN .*PRIVATE KEY", re.IGNORECASE),
        ]
        for content in (self.chat_page, self.chat_message, self.chat_composer, self.chat_sidebar, self.chat_empty_state, self.types):
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
