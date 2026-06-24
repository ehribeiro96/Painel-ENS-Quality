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
        self.assertIn("const legacyApoemaAliasRoutes", APP)
        self.assertIn("Legacy routes are retained temporarily while Apoema becomes the primary surface.", APP)
        self.assertIn("function LegacyShellRoute()", APP)
        self.assertIn("function LegacyRoutes()", APP)

    def test_legacy_routes_document_migration_targets(self) -> None:
        match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(match)
        legacy_block = match.group(1)
        alias_match = re.search(r"const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(alias_match)
        alias_block = alias_match.group(1)

        expected_routes = {
            "/users": "apoema:users",
            "/users/:id": "apoema:users",
            "/assignments": "apoema:movements",
            "/settings": "apoema:settings",
        }

        self.assertNotIn('path: "/assets"', legacy_block)
        self.assertNotIn('path: "/assets/:id"', legacy_block)
        self.assertNotIn('path: "/audit-logs"', legacy_block)
        self.assertNotIn('path: "/imports"', legacy_block)
        self.assertNotIn('path: "/macros"', legacy_block)
        self.assertNotIn('path: "/signatures"', legacy_block)
        self.assertNotIn('path: "/stock"', legacy_block)

        for path, target in expected_routes.items():
            self.assertIn(f'path: "{path}"', legacy_block)
            self.assertIn(f'migrationTarget: "{target}"', legacy_block)
            self.assertIn("temporaryCompatibility: true", legacy_block)

        self.assertIn('path: "/ai-chat"', alias_block)
        self.assertIn('path: "/audit-logs"', alias_block)
        self.assertIn('path: "/assets"', alias_block)
        self.assertIn('path: "/assets/:id"', alias_block)
        self.assertIn('path: "/imports"', alias_block)
        self.assertIn('path: "/macros"', alias_block)
        self.assertIn('path: "/signatures"', alias_block)
        self.assertIn('path: "/stock"', alias_block)
        self.assertIn('migrationTarget: "apoema:chat"', alias_block)
        self.assertIn('migrationTarget: "apoema:audit-logs"', alias_block)
        self.assertIn('migrationTarget: "apoema:assets"', alias_block)
        self.assertIn('migrationTarget: "apoema:imports"', alias_block)
        self.assertIn('migrationTarget: "apoema:macros"', alias_block)
        self.assertIn('migrationTarget: "apoema:signatures"', alias_block)
        self.assertIn('migrationTarget: "apoema:stock"', alias_block)
        self.assertIn("temporaryCompatibility: true", alias_block)
        self.assertIn('redirectTo: "/apoema/audit-logs"', APP)
        self.assertIn('redirectTo: "/apoema/assets"', APP)
        self.assertIn('redirectTo: "/apoema/assets/:id"', APP)
        self.assertIn('redirectTo: "/apoema/imports"', APP)
        self.assertIn('redirectTo: "/apoema/macros"', APP)
        self.assertIn('redirectTo: "/apoema/signatures"', APP)
        self.assertIn('redirectTo: "/apoema/stock"', APP)

    def test_apoema_surface_remains_outside_legacy_shell(self) -> None:
        apoema_routes_block = APP.split("function ApoemaRoutes()")[1].split("type LegacyCompatibilityRouteDefinition")[0]
        legacy_shell_block = APP.split("function LegacyShellRoute()")[1].split("function LegacyRoutes()")[0]

        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn("<LegacyApoemaAliasRoutes />", APP)
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
