from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOEMA_CSS = (ROOT / "frontend/itam-platform/src/apoema/styles/apoema.css").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
DASHBOARD = (ROOT / "frontend/itam-platform/src/apoema/pages/DashboardPage.tsx").read_text(encoding="utf-8")
CHAT = (ROOT / "frontend/itam-platform/src/apoema/pages/ChatPage.tsx").read_text(encoding="utf-8")
SIDEBAR = (ROOT / "frontend/itam-platform/src/apoema/components/ChatConversationSidebar.tsx").read_text(encoding="utf-8")
COMPOSER = (ROOT / "frontend/itam-platform/src/apoema/components/ChatComposer.tsx").read_text(encoding="utf-8")
MESSAGE = (ROOT / "frontend/itam-platform/src/apoema/components/ChatMessage.tsx").read_text(encoding="utf-8")
THEME = (ROOT / "frontend/itam-platform/src/apoema/hooks/useThemeMode.ts").read_text(encoding="utf-8")


class ApoemaHermesRedesignContractTest(unittest.TestCase):
    def test_theme_defaults_to_dark_and_css_is_dark_first(self) -> None:
        self.assertIn('return "dark";', THEME)
        self.assertIn("color-scheme: dark;", APOEMA_CSS)
        self.assertIn(".apoema-root[data-theme=\"dark\"]", APOEMA_CSS)
        self.assertIn(".apoema-root[data-theme=\"light\"]", APOEMA_CSS)

    def test_chat_keeps_sidebar_feed_composer_structure(self) -> None:
        for snippet in (
            'grid min-w-0 gap-4 lg:grid-cols-[clamp(240px,22vw,300px)_minmax(0,1fr)]',
            'rounded-[28px] border border-white/10 bg-white/[0.04]',
            "ChatConversationSidebar",
            "ChatComposer",
            "ChatMessage",
        ):
            self.assertIn(snippet, CHAT)
        self.assertNotIn("ChatFirstShell", CHAT)
        self.assertNotIn("apoema-chat-first-shell", CHAT)
        self.assertIn("rounded-[28px]", SIDEBAR)
        self.assertIn("Anexar arquivos", COMPOSER)
        self.assertIn("data-role={message.role}", MESSAGE)

    def test_dashboard_copy_uses_compact_operational_labels(self) -> None:
        self.assertIn("Ações rápidas", DASHBOARD)
        self.assertIn("Linha do tempo", DASHBOARD)
        self.assertIn("Abrir chat", DASHBOARD)
        self.assertIn("Ver ativos", DASHBOARD)
        self.assertNotIn("Mocked action lane", DASHBOARD)
        self.assertNotIn("Telemetry feed", DASHBOARD)

    def test_chat_copy_uses_portuguese_navigation_and_safety_labels(self) -> None:
        self.assertIn("Conversas", CHAT)
        self.assertIn("Hermes real no centro da operação", CHAT)
        self.assertIn("exclusão confirmada e anexos locais honestos", CHAT)
        self.assertIn("Pronto para operar", CHAT)
        self.assertNotIn("Workspace", CHAT)
        self.assertNotIn("Guard rails", CHAT)


if __name__ == "__main__":
    unittest.main()
