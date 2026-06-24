from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_ASSIGNMENTS = (ROOT / "frontend/itam-platform/src/apoema/pages/AssignmentsPage.tsx").read_text(encoding="utf-8")
LEGACY_ASSIGNMENTS = ROOT / "frontend/itam-platform/src/pages/AssignmentsPage.tsx"
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4i-assignments/ASSIGNMENTS_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaAssignmentsParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Assignments Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/assignments", MATRIX)
        self.assertIn("/apoema/assignments", MATRIX)
        self.assertIn("Paridade", MATRIX)

    def test_assignments_route_points_to_apoema_movements_page_without_legacy_alias(self) -> None:
        self.assertIn('path="assignments" element={<AssignmentsPage />}', APOEMA_APP)
        self.assertIn("const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/assignments"', APP)
        self.assertNotIn('redirectTo: "/apoema/assignments"', APP)

    def test_assignments_page_contains_operational_and_timeline_surface(self) -> None:
        for term in (
            "Base44AssetTimeline",
            "Base44EmptyState",
            "Base44OperationalGrid",
            "Base44PageHeader",
            "Base44StatusBadge",
            "Base44Surface",
            "DataTable",
            "LoadingBlock",
            "Apoema Movimentações",
            "Movimentações",
            "Histórico recente",
            "Vínculos atuais",
            "api.recentMovements",
        ):
            self.assertIn(term, APOEMA_ASSIGNMENTS)

    def test_legacy_assignments_page_was_removed_from_disk(self) -> None:
        self.assertFalse(LEGACY_ASSIGNMENTS.exists())

    def test_apoema_stays_free_of_direct_provider_calls(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA)

    def test_related_apoema_aliases_and_lazy_loading_remain_preserved(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('lazy(() => import("./apoema")', normalized)
        self.assertIn('Suspense fallback={<RouteLoading />}', APP)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        for target in (
            'path: "/assignments"',
            'redirectTo: "/apoema/assignments"',
            'redirectTo: "/apoema/signatures"',
            'redirectTo: "/apoema/stock"',
            'redirectTo: "/apoema/macros"',
            'redirectTo: "/apoema/imports"',
            'redirectTo: "/apoema/audit-logs"',
            'redirectTo: "/apoema/assets"',
            'redirectTo: "/apoema/assets/:id"',
            'redirectTo: "/apoema/chat"',
        ):
            self.assertNotIn(target, APP)
        self.assertIn('path="assignments" element={<AssignmentsPage />}', APOEMA_APP)


if __name__ == "__main__":
    unittest.main()
