from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOEMA_CSS = (ROOT / "frontend/itam-platform/src/apoema/styles/apoema.css").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
DASHBOARD = (ROOT / "frontend/itam-platform/src/apoema/pages/DashboardPage.tsx").read_text(encoding="utf-8")
CHAT = (ROOT / "frontend/itam-platform/src/apoema/pages/ChatPage.tsx").read_text(encoding="utf-8")
THEME = (ROOT / "frontend/itam-platform/src/apoema/hooks/useThemeMode.ts").read_text(encoding="utf-8")


class ApoemaHermesRedesignContractTest(unittest.TestCase):
    def test_theme_defaults_to_dark_and_css_is_dark_first(self) -> None:
        self.assertIn('return "dark";', THEME)
        self.assertIn("color-scheme: dark;", APOEMA_CSS)
        self.assertIn(".apoema-root[data-theme=\"dark\"]", APOEMA_CSS)
        self.assertIn(".apoema-root[data-theme=\"light\"]", APOEMA_CSS)

    def test_shell_keeps_sidebar_topbar_and_rail_structure(self) -> None:
        self.assertIn('className="apoema-shell"', APOEMA_APP)
        self.assertIn('className="apoema-sidebar"', APOEMA_APP)
        self.assertIn('className="apoema-topbar"', APOEMA_APP)
        self.assertIn('className="apoema-rail"', APOEMA_APP)

    def test_dashboard_copy_uses_compact_operational_labels(self) -> None:
        self.assertIn("Ações rápidas", DASHBOARD)
        self.assertIn("Linha do tempo", DASHBOARD)
        self.assertNotIn("Mocked action lane", DASHBOARD)
        self.assertNotIn("Telemetry feed", DASHBOARD)

    def test_chat_copy_uses_portuguese_navigation_and_safety_labels(self) -> None:
        self.assertIn("Conversas", CHAT)
        self.assertIn("Proteções", CHAT)
        self.assertNotIn("Workspace", CHAT)
        self.assertNotIn("Guard rails", CHAT)


if __name__ == "__main__":
    unittest.main()
