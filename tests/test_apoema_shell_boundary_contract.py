from __future__ import annotations

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
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)

    def test_root_and_apoema_routes_stay_apoema_first(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', normalized)
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

    def test_legacy_shell_isolated_from_apoema_route(self) -> None:
        legacy_shell_section = APP.split("function LegacyShellRoute()")[1].split("function LegacyRoutes()")[0]
        apoema_section = APP.split("function ApoemaRoutes()")[1].split("// Legacy routes are retained temporarily while Apoema becomes the primary surface.")[0]

        self.assertIn("<AppShell>", legacy_shell_section)
        self.assertIn("<Outlet />", legacy_shell_section)
        self.assertNotIn("ApoemaApp", legacy_shell_section)
        self.assertNotIn("AppShell", apoema_section)

    def test_legacy_routes_remain_preserved(self) -> None:
        self.assertIn("const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn("temporaryCompatibility: true", APP)
        for target in (
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
            self.assertNotIn(target, APP)

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
