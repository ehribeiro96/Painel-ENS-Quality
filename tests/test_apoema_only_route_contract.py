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


class ApoemaOnlyRouteContractTest(unittest.TestCase):
    def test_root_redirects_to_apoema_and_apoema_routes_exist(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)

    def test_protected_route_wraps_apoema_and_lazy_loading_remains(self) -> None:
        self.assertIn("function ProtectedRoute(", APP)
        self.assertIn("function ApoemaRoute()", APP)
        self.assertIn("<ProtectedRoute>", APP)
        self.assertIn("lazy(() => import(\"./apoema\")", APP)
        self.assertIn("Suspense fallback={<RouteLoading />}", APP)

    def test_legacy_routes_remain_in_place_for_compatibility(self) -> None:
        match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(match)
        legacy_block = match.group(1)
        for path in ("/imports", "/macros", "/settings", "/audit-logs", "/users", "/signatures", "/stock"):
            self.assertIn(f'path: "{path}"', legacy_block)
        alias_match = re.search(r"const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(alias_match)
        alias_block = alias_match.group(1)
        self.assertIn('path: "/ai-chat"', alias_block)
        self.assertIn('path: "/assets"', alias_block)
        self.assertIn('path: "/assets/:id"', alias_block)
        self.assertIn('migrationTarget: "apoema:chat"', alias_block)
        self.assertIn('migrationTarget: "apoema:assets"', alias_block)
        self.assertIn('redirectTo: "/apoema/assets"', alias_block)
        self.assertIn('redirectTo: "/apoema/assets/:id"', alias_block)
        self.assertNotIn('element={<DashboardPage />}', APP)

    def test_apoema_does_not_call_providers_directly(self) -> None:
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
