from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APPSHELL = ROOT / "frontend/itam-platform/src/components/AppShell.tsx"


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaShellBoundaryContractTest(unittest.TestCase):
    def test_appshell_was_removed_and_app_tsx_no_longer_imports_it(self) -> None:
        self.assertFalse(APPSHELL.exists())
        self.assertNotIn("AppShell", APP)
        self.assertNotIn("LegacyShellRoute", APP)
        self.assertNotIn("LegacyRoutes", APP)
        self.assertNotIn("legacyCompatibilityRoutes", APP)
        self.assertNotIn("Outlet", APP)

    def test_app_keeps_apoema_first_routes_and_login_fallback(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/login" element={<LoginPage />} ', normalized)
        self.assertNotIn('path: "/ai-chat"', APP)
        self.assertNotIn('path: "/assets"', APP)
        self.assertNotIn('path: "/audit-logs"', APP)
        self.assertNotIn('path: "/imports"', APP)
        self.assertNotIn('path: "/macros"', APP)
        self.assertNotIn('path: "/stock"', APP)
        self.assertNotIn('path: "/signatures"', APP)
        self.assertNotIn('path: "/assignments"', APP)
        self.assertNotIn('path: "/users"', APP)
        self.assertNotIn('path: "/settings"', APP)

    def test_apoema_stays_free_of_direct_provider_calls(self) -> None:
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
