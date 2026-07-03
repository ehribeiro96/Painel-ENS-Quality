from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend" / "itam-platform" / "src" / "App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend" / "itam-platform" / "src" / "apoema" / "ApoemaApp.tsx").read_text(encoding="utf-8")


class ApoemaNavigationTargetsContractTest(unittest.TestCase):
    def test_sidebar_navigation_uses_current_apoema_prefix(self) -> None:
        normalized = APP.replace("\n", " ")

        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('to="/apoema/chat"', normalized)
        self.assertNotIn("ChatFirstShell", normalized)

    def test_apoema_and_preview_routes_remain_canonical(self) -> None:
        normalized = APOEMA_APP.replace("\n", " ")

        self.assertIn("DonorAppShell", normalized)
        self.assertIn('path="chat" element={<ChatPage />}', normalized)
        self.assertIn('path="dashboard" element={<DashboardPage />}', normalized)
        self.assertIn('path="assets" element={<AssetsPage />}', normalized)
        self.assertIn('path="settings" element={<SettingsPage />}', normalized)
        self.assertIn('path="integrations" element={<IntegrationsPage />}', normalized)
        self.assertIn('path="designer/jobs/:jobId" element={<DesignerJobPage />}', normalized)


if __name__ == "__main__":
    unittest.main()
