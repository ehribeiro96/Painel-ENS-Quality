from __future__ import annotations

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
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)

    def test_legacy_routes_document_migration_targets(self) -> None:
        self.assertIn("const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        for alias in (
            'path: "/ai-chat"',
            'path: "/audit-logs"',
            'path: "/assets"',
            'path: "/assets/:id"',
            'path: "/assignments"',
            'path: "/users"',
            'path: "/users/:id"',
            'path: "/settings"',
            'path: "/imports"',
            'path: "/macros"',
            'path: "/signatures"',
            'path: "/stock"',
            'migrationTarget: "apoema:chat"',
            'migrationTarget: "apoema:audit-logs"',
            'migrationTarget: "apoema:assets"',
            'migrationTarget: "apoema:movements"',
            'migrationTarget: "apoema:users"',
            'migrationTarget: "apoema:settings"',
            'migrationTarget: "apoema:imports"',
            'migrationTarget: "apoema:macros"',
            'migrationTarget: "apoema:signatures"',
            'migrationTarget: "apoema:stock"',
            'redirectTo: "/apoema/audit-logs"',
            'redirectTo: "/apoema/assets"',
            'redirectTo: "/apoema/assets/:id"',
            'redirectTo: "/apoema/assignments"',
            'redirectTo: "/apoema/users"',
            'redirectTo: "/apoema/users/:id"',
            'redirectTo: "/apoema/settings"',
            'redirectTo: "/apoema/imports"',
            'redirectTo: "/apoema/macros"',
            'redirectTo: "/apoema/signatures"',
            'redirectTo: "/apoema/stock"',
        ):
            self.assertNotIn(alias, APP)

    def test_apoema_surface_remains_outside_legacy_shell(self) -> None:
        apoema_routes_block = APP.split("function ApoemaRoutes()")[1].split("type LegacyCompatibilityRouteDefinition")[0]
        legacy_shell_block = APP.split("function LegacyShellRoute()")[1].split("function LegacyRoutes()")[0]

        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn("<AppShell>", legacy_shell_block)
        self.assertIn("<Outlet />", legacy_shell_block)
        self.assertNotIn("AppShell", apoema_routes_block)
        self.assertNotIn("legacyApoemaAliasRoutes", apoema_routes_block)

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
