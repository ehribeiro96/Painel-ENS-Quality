from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")


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
    def test_app_exposes_explicit_apoema_first_and_legacy_blocks(self) -> None:
        self.assertIn("function ApoemaRoutes()", APP)
        self.assertIn("const legacyCompatibilityRoutes", APP)
        self.assertIn("function LegacyShellRoute()", APP)
        self.assertIn("function LegacyRoutes()", APP)
        self.assertIn("// Legacy routes are retained temporarily while Apoema becomes the primary surface.", APP)
        self.assertIn("<ApoemaRoutes />", APP)
        self.assertIn("<LegacyRoutes />", APP)

    def test_root_and_apoema_routes_stay_apoema_first(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/login" element={<LoginPage />} ', normalized)

    def test_legacy_shell_isolated_from_apoema_route(self) -> None:
        legacy_shell_section = APP.split("function LegacyShellRoute()")[1].split("function LegacyRoutes()")[0]
        apoema_section = APP.split("function ApoemaRoutes()")[1].split("// Legacy routes are retained temporarily while Apoema becomes the primary surface.")[0]

        self.assertIn("<AppShell>", legacy_shell_section)
        self.assertIn("<Outlet />", legacy_shell_section)
        self.assertNotIn("ApoemaApp", legacy_shell_section)
        self.assertNotIn("AppShell", apoema_section)

    def test_legacy_routes_remain_preserved(self) -> None:
        match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(match)
        legacy_block = match.group(1)
        for path in ("/assets", "/assets/:id", "/users", "/users/:id", "/assignments", "/stock", "/imports", "/macros", "/ai-chat", "/signatures", "/audit-logs", "/settings"):
            self.assertIn(f'path: "{path}"', legacy_block)
        for target in ("apoema:assets", "apoema:users", "apoema:movements", "apoema:stock", "apoema:imports", "apoema:macros", "apoema:chat", "apoema:signatures", "apoema:audit-logs", "apoema:settings"):
            self.assertIn(f'migrationTarget: "{target}"', APP)
        self.assertIn("temporaryCompatibility: true", APP)

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
