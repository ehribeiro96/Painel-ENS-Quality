from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")


class ApoemaRemoveLegacyAliasesContractTest(unittest.TestCase):
    def test_legacy_alias_routes_are_removed_from_app_routing(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/login" element={<LoginPage />}', normalized)
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn("const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];", APP)

        for alias in (
            'path: "/ai-chat"',
            'path: "/assets"',
            'path: "/assets/:id"',
            'path: "/audit-logs"',
            'path: "/imports"',
            'path: "/macros"',
            'path: "/stock"',
            'path: "/signatures"',
            'path: "/assignments"',
            'path: "/users"',
            'path: "/users/:id"',
            'path: "/settings"',
            'redirectTo: "/apoema/chat"',
            'redirectTo: "/apoema/assets"',
            'redirectTo: "/apoema/assets/:id"',
            'redirectTo: "/apoema/audit-logs"',
            'redirectTo: "/apoema/imports"',
            'redirectTo: "/apoema/macros"',
            'redirectTo: "/apoema/stock"',
            'redirectTo: "/apoema/signatures"',
            'redirectTo: "/apoema/assignments"',
            'redirectTo: "/apoema/users"',
            'redirectTo: "/apoema/users/:id"',
            'redirectTo: "/apoema/settings"',
            "legacyApoemaAliasRoutes",
            "LegacyApoemaAliasRoutes",
        ):
            self.assertNotIn(alias, APP)

        self.assertIn("// Legacy routes are retained temporarily while Apoema becomes the primary surface.", APP)
        self.assertIn("function LegacyShellRoute()", APP)
        self.assertIn("function LegacyRoutes()", APP)
        self.assertNotIn("AppShell", APP.split("function ApoemaRoutes()")[1].split("type LegacyCompatibilityRouteDefinition")[0])


if __name__ == "__main__":
    unittest.main()
