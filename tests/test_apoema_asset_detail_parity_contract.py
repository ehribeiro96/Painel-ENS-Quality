from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_DETAIL = (ROOT / "frontend/itam-platform/src/apoema/pages/AssetDetailPage.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4c-asset-detail/ASSET_DETAIL_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


class ApoemaAssetDetailParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_dynamic_redirect_policy(self) -> None:
        self.assertIn("Asset Detail legacy -> Apoema Detalhe de Ativo", MATRIX)
        self.assertIn("POLICY_A_SAFE_DYNAMIC_REDIRECT", MATRIX)
        self.assertIn("/assets/:id", MATRIX)
        self.assertIn("/apoema/assets/:id", MATRIX)
        self.assertIn("parity_minimum_met", MATRIX)

    def test_asset_detail_route_points_to_apoema_detail_page_without_legacy_alias(self) -> None:
        self.assertIn('path="assets/:id" element={<AssetDetailPage />}', APOEMA_APP)
        self.assertNotIn("legacyCompatibilityRoutes", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/assets/:id"', APP)
        self.assertNotIn('redirectTo: "/apoema/assets/:id"', APP)

    def test_detail_page_contains_operational_actions_and_states(self) -> None:
        for term in ("MoveAssetDialog", "Base44AssetTimeline", "Base44EmptyState", "LoadingBlock", "Base44PageHeader", "queryClient.invalidateQueries"):
            self.assertIn(term, APOEMA_DETAIL)
        self.assertIn('to=".."', APOEMA_DETAIL)
        self.assertIn('to="../.."', APOEMA_DETAIL)
        self.assertIn("Movimentar", APOEMA_DETAIL)
        self.assertIn("Copiar resumo", APOEMA_DETAIL)

    def test_no_direct_provider_calls_in_apoema_detail(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA_DETAIL)


if __name__ == "__main__":
    unittest.main()
