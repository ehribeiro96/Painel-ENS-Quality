from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "frontend/itam-platform/src/apoema").rglob("*"))
    if path.suffix in {".ts", ".tsx", ".css"}
)


class ApoemaLegacySurfaceContractTest(unittest.TestCase):
    def test_legacy_compatibility_boundary_is_explicit(self) -> None:
        self.assertIn("const legacyCompatibilityRoutes", APP)
        self.assertIn("Legacy routes are retained temporarily while Apoema becomes the primary surface.", APP)
        self.assertIn("function LegacyShellRoute()", APP)
        self.assertIn("function LegacyRoutes()", APP)

    def test_legacy_routes_document_migration_targets(self) -> None:
        match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(match)
        legacy_block = match.group(1)

        expected_routes = {
            "/assets": "apoema:assets",
            "/assets/:id": "apoema:assets",
            "/users": "apoema:users",
            "/users/:id": "apoema:users",
            "/assignments": "apoema:movements",
            "/stock": "apoema:stock",
            "/imports": "apoema:imports",
            "/macros": "apoema:macros",
            "/ai-chat": "apoema:chat",
            "/signatures": "apoema:signatures",
            "/audit-logs": "apoema:audit-logs",
            "/settings": "apoema:settings",
        }

        for path, target in expected_routes.items():
            self.assertIn(f'path: "{path}"', legacy_block)
            self.assertIn(f'migrationTarget: "{target}"', legacy_block)
            self.assertIn("temporaryCompatibility: true", legacy_block)

    def test_apoema_surface_remains_outside_legacy_shell(self) -> None:
        apoema_routes_block = APP.split("function ApoemaRoutes()")[1].split("type LegacyCompatibilityRouteDefinition")[0]
        legacy_shell_block = APP.split("function LegacyShellRoute()")[1].split("function LegacyRoutes()")[0]

        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn("<AppShell>", legacy_shell_block)
        self.assertIn("<Outlet />", legacy_shell_block)
        self.assertNotIn("AppShell", apoema_routes_block)

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
