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
        self.assertIn("function LegacyApoemaAliasRoutes()", APP)
        self.assertIn("const legacyCompatibilityRoutes", APP)
        self.assertIn("const legacyApoemaAliasRoutes", APP)
        self.assertIn("function LegacyShellRoute()", APP)
        self.assertIn("function LegacyRoutes()", APP)
        self.assertIn("// Legacy routes are retained temporarily while Apoema becomes the primary surface.", APP)
        self.assertIn("<ApoemaRoutes />", APP)
        self.assertIn("<LegacyApoemaAliasRoutes />", APP)
        self.assertIn("<LegacyRoutes />", APP)

    def test_root_and_apoema_routes_stay_apoema_first(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn("<LegacyApoemaAliasRoutes />", APP)
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
        self.assertIn('path: "/settings"', legacy_block)
        self.assertNotIn('path: "/users"', legacy_block)
        self.assertNotIn('path: "/users/:id"', legacy_block)

        alias_match = re.search(r"const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(alias_match)
        alias_block = alias_match.group(1)
        self.assertIn('path: "/ai-chat"', alias_block)
        self.assertIn('path: "/audit-logs"', alias_block)
        self.assertIn('path: "/assets"', alias_block)
        self.assertIn('path: "/assets/:id"', alias_block)
        self.assertIn('path: "/assignments"', alias_block)
        self.assertIn('path: "/users"', alias_block)
        self.assertIn('path: "/users/:id"', alias_block)
        self.assertIn('path: "/imports"', alias_block)
        self.assertIn('path: "/macros"', alias_block)
        self.assertIn('path: "/signatures"', alias_block)
        self.assertIn('path: "/stock"', alias_block)
        self.assertIn('migrationTarget: "apoema:chat"', alias_block)
        self.assertIn('migrationTarget: "apoema:audit-logs"', alias_block)
        self.assertIn('migrationTarget: "apoema:assets"', alias_block)
        self.assertIn('migrationTarget: "apoema:movements"', alias_block)
        self.assertIn('migrationTarget: "apoema:users"', alias_block)
        self.assertIn('migrationTarget: "apoema:imports"', alias_block)
        self.assertIn('migrationTarget: "apoema:macros"', alias_block)
        self.assertIn('migrationTarget: "apoema:signatures"', alias_block)
        self.assertIn('migrationTarget: "apoema:stock"', alias_block)
        self.assertIn('redirectTo: "/apoema/audit-logs"', alias_block)
        self.assertIn('redirectTo: "/apoema/assets"', alias_block)
        self.assertIn('redirectTo: "/apoema/assets/:id"', alias_block)
        self.assertIn('redirectTo: "/apoema/assignments"', alias_block)
        self.assertIn('redirectTo: "/apoema/users"', alias_block)
        self.assertIn('redirectTo: "/apoema/users/:id"', alias_block)
        self.assertIn('redirectTo: "/apoema/imports"', alias_block)
        self.assertIn('redirectTo: "/apoema/macros"', alias_block)
        self.assertIn('redirectTo: "/apoema/signatures"', alias_block)
        self.assertIn('redirectTo: "/apoema/stock"', alias_block)
        for target in ("apoema:assets", "apoema:users", "apoema:movements", "apoema:stock", "apoema:imports", "apoema:macros", "apoema:signatures", "apoema:audit-logs", "apoema:settings"):
            self.assertIn(f'migrationTarget: "{target}"', APP)
        self.assertIn("temporaryCompatibility: true", APP)
        self.assertIn("temporaryCompatibility: true", alias_block)

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
