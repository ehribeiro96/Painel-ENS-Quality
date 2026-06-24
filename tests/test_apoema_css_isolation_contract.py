from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
MAIN = (ROOT / "frontend/itam-platform/src/main.tsx").read_text(encoding="utf-8")
GLOBAL_CSS = (ROOT / "frontend/itam-platform/src/styles.css").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_CSS = (ROOT / "frontend/itam-platform/src/apoema/styles/apoema.css").read_text(encoding="utf-8")
LOGIN_PAGE = ROOT / "frontend/itam-platform/src/pages/LoginPage.tsx"
NOT_FOUND_PAGE = ROOT / "frontend/itam-platform/src/pages/NotFoundPage.tsx"


class ApoemaCssIsolationContractTest(unittest.TestCase):
    def assert_selector_absent(self, selector: str) -> None:
        pattern = re.compile(rf"(?<![\w-]){re.escape(selector)}(?![\w-])")
        self.assertIsNone(pattern.search(GLOBAL_CSS), msg=f"selector still present: {selector}")

    def test_global_css_and_apoema_css_are_still_imported(self) -> None:
        self.assertIn('import "./styles.css";', MAIN)
        self.assertIn('import "./styles/apoema.css";', APOEMA_APP)
        self.assertTrue(LOGIN_PAGE.exists())
        self.assertTrue(NOT_FOUND_PAGE.exists())

    def test_removed_legacy_shell_selectors_are_not_in_global_css(self) -> None:
        removed_selectors = (
            ".shell",
            ".sidebar",
            ".main",
            ".topbar",
            ".toolbar",
            ".content",
            ".search-results",
            ".search-result",
            ".dashboard-metrics",
            ".dashboard-panels",
            ".import-export-grid",
            ".assets-page",
            ".page-actions",
            ".form-panel-actions",
            ".users-toolbar",
            ".users-form-card",
            ".audit-summary-grid",
            ".audit-toolbar",
            ".assignments-summary-grid",
        )
        for selector in removed_selectors:
            self.assert_selector_absent(selector)

    def test_preserved_operational_selectors_still_exist(self) -> None:
        preserved_global_selectors = (
            ".details",
            ".metric-card",
            ".filter-chip",
            ".assignment-cell",
            ".assignment-warning",
            ".assignment-status-badge",
            ".email-cell",
            ".users-row-actions",
            ".wide-field",
            ".screen-center",
            ".base44-login-shell",
            ".base44-notfound-shell",
        )
        for selector in preserved_global_selectors:
            self.assertIn(selector, GLOBAL_CSS)

        preserved_apoema_selectors = (".apoema-root", ".apoema-shell", ".apoema-topbar")
        for selector in preserved_apoema_selectors:
            self.assertIn(selector, APOEMA_CSS)

    def test_apoema_and_route_contracts_remain_intact(self) -> None:
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertNotIn("AppShell", APP)
        self.assertNotIn("LegacyShellRoute", APP)
        self.assertNotIn("LegacyRoutes", APP)
        self.assertNotIn("legacyCompatibilityRoutes", APP)
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA_CSS)


if __name__ == "__main__":
    unittest.main()
