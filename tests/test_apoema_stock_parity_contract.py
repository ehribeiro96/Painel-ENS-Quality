from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_STOCK = (ROOT / "frontend/itam-platform/src/apoema/pages/StockPage.tsx").read_text(encoding="utf-8")
LEGACY_STOCK = (ROOT / "frontend/itam-platform/src/pages/StockPage.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4g-stock/STOCK_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaStockParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Stock Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/stock", MATRIX)
        self.assertIn("/apoema/stock", MATRIX)
        self.assertIn("Paridade", MATRIX)

    def test_stock_route_points_to_apoema_stock_page_without_legacy_alias(self) -> None:
        self.assertIn('path="stock" element={<StockPage />}', APOEMA_APP)
        self.assertIn("const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/stock"', APP)
        self.assertNotIn('redirectTo: "/apoema/stock"', APP)

    def test_stock_page_contains_operational_parity_surface(self) -> None:
        for term in ("Base44PageHeader", "Base44OperationalGrid", "Base44MetricCard", "Base44Surface", "Base44StatusBadge", "Base44EmptyState", "LoadingBlock"):
            self.assertIn(term, APOEMA_STOCK)
        self.assertIn("assetsByStatus(", APOEMA_STOCK)
        self.assertIn("Apoema Estoque", APOEMA_STOCK)
        self.assertIn("Estoque", APOEMA_STOCK)
        self.assertIn("Sem mock", APOEMA_STOCK)
        self.assertIn("total", APOEMA_STOCK)

    def test_legacy_stock_page_remains_available_for_compatibility(self) -> None:
        for term in ("assetsByStatus(", "Base44MetricCard", "Base44OperationalGrid", "Base44Surface"):
            self.assertIn(term, LEGACY_STOCK)

    def test_apoema_stays_free_of_direct_provider_calls(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA)

    def test_lazy_loading_and_preview_boundary_remain_preserved(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('lazy(() => import("./apoema")', normalized)
        self.assertIn('Suspense fallback={<RouteLoading />}', APP)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />}', normalized)


if __name__ == "__main__":
    unittest.main()
