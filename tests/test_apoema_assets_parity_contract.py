from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_ASSET_DETAIL = (ROOT / "frontend/itam-platform/src/apoema/pages/AssetDetailPage.tsx").read_text(encoding="utf-8")
APOEMA_ASSETS = (ROOT / "frontend/itam-platform/src/apoema/pages/AssetsPage.tsx").read_text(encoding="utf-8")
LEGACY_ASSETS = (ROOT / "frontend/itam-platform/src/pages/AssetsPage.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4b-assets/ASSETS_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


class ApoemaAssetsParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Assets legacy -> Apoema Ativos", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/assets", MATRIX)
        self.assertIn("/apoema/assets", MATRIX)
        self.assertIn("parity_minimum_met", MATRIX)

    def test_assets_route_is_canonical_in_apoema_and_alias_is_removed(self) -> None:
        self.assertIn('path="assets" element={<AssetsPage />}', APOEMA_APP)
        self.assertIn('path="assets/:id" element={<AssetDetailPage />}', APOEMA_APP)
        self.assertIn("const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/assets"', APP)
        self.assertNotIn('path: "/assets/:id"', APP)
        self.assertNotIn('redirectTo: "/apoema/assets"', APP)
        self.assertNotIn('redirectTo: "/apoema/assets/:id"', APP)

    def test_apoema_assets_page_contains_the_operational_parity_surface(self) -> None:
        for term in ("Search", "DataTable", "StatusPill", "MetricCard", "selectedAsset", "apoemaMetrics"):
            self.assertIn(term, APOEMA_ASSETS)
        self.assertIn("Filtre, revise e priorize a base de ativos", APOEMA_ASSETS)

    def test_apoema_asset_detail_page_contains_operational_actions(self) -> None:
        for term in ("MoveAssetDialog", "Base44AssetTimeline", "LoadingBlock", "Base44EmptyState", "queryClient.invalidateQueries"):
            self.assertIn(term, APOEMA_ASSET_DETAIL)
        self.assertIn('to=".."', APOEMA_ASSET_DETAIL)
        self.assertIn("Movimentar", APOEMA_ASSET_DETAIL)

    def test_legacy_assets_page_remains_on_disk_for_compatibility(self) -> None:
        for term in ("useQuery", "saveAssetMutation", "deleteAssetMutation", "MoveAssetDialog", "DataTable"):
            self.assertIn(term, LEGACY_ASSETS)
        self.assertIn("Historico preservado.", LEGACY_ASSETS)


if __name__ == "__main__":
    unittest.main()
