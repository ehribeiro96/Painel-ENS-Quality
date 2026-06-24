from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APPSHELL = ROOT / "frontend/itam-platform/src/components/AppShell.tsx"
APOEMA = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "frontend/itam-platform/src/apoema").rglob("*"))
    if path.suffix in {".ts", ".tsx", ".css"}
)


class ApoemaLegacySurfaceContractTest(unittest.TestCase):
    def test_legacy_shell_boundary_was_removed_from_app(self) -> None:
        self.assertFalse(APPSHELL.exists())
        self.assertNotIn("AppShell", APP)
        self.assertNotIn("LegacyShellRoute", APP)
        self.assertNotIn("LegacyRoutes", APP)
        self.assertNotIn("legacyCompatibilityRoutes", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)

    def test_apoema_surface_remains_apoema_first_without_legacy_shell_wrapper(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/login" element={<LoginPage />} ', normalized)
        self.assertNotIn('path: "/ai-chat"', APP)
        self.assertNotIn('path: "/audit-logs"', APP)
        self.assertNotIn('path: "/assets"', APP)
        self.assertNotIn('path: "/assets/:id"', APP)
        self.assertNotIn('path: "/assignments"', APP)
        self.assertNotIn('path: "/users"', APP)
        self.assertNotIn('path: "/users/:id"', APP)
        self.assertNotIn('path: "/settings"', APP)
        self.assertNotIn('path: "/imports"', APP)
        self.assertNotIn('path: "/macros"', APP)
        self.assertNotIn('path: "/signatures"', APP)
        self.assertNotIn('path: "/stock"', APP)
        self.assertNotIn("Outlet", APP)

    def test_apoema_sources_do_not_call_providers_directly(self) -> None:
        forbidden_terms = (
            "localhost:11434",
            "127.0.0.1:11434",
            "OLLAMA_BASE_URL",
            "HERMES_BASE_URL",
            "COMPOSIO",
            "/api/chat",
        )
        for term in forbidden_terms:
            self.assertNotIn(term, APOEMA)


if __name__ == "__main__":
    unittest.main()
