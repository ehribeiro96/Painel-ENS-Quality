from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_MACROS = (ROOT / "frontend/itam-platform/src/apoema/pages/MacrosPage.tsx").read_text(encoding="utf-8")
MACRO_PREVIEW = (ROOT / "frontend/itam-platform/src/components/base44/Base44MacroPreview.tsx").read_text(encoding="utf-8")
LEGACY_MACROS = ROOT / "frontend/itam-platform/src/pages/MacrosPage.tsx"
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4f-macros/MACROS_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


class ApoemaMacrosParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Macros Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/macros", MATRIX)
        self.assertIn("/apoema/macros", MATRIX)
        self.assertIn("Paridade", MATRIX)

    def test_macros_route_points_to_apoema_macros_page_without_legacy_alias(self) -> None:
        self.assertIn('path="macros" element={<MacrosPage />}', APOEMA_APP)
        self.assertNotIn("legacyCompatibilityRoutes", APP)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/macros"', APP)
        self.assertNotIn('redirectTo: "/apoema/macros"', APP)

    def test_macros_page_contains_itil_preview_and_copy_contract(self) -> None:
        for term in ("Base44MacroPanel", "Base44MacroPreview", "Base44EmptyState", "Base44FilterPanel", "Base44PageHeader", "Base44StatusBadge", "LoadingBlock"):
            self.assertIn(term, APOEMA_MACROS)
        for term in ("useQuery", "macroTemplates", "macroAutocomplete", "macroGenerate", "macroMarkCopied"):
            self.assertIn(term, APOEMA_MACROS)
        self.assertIn("Apoema Macros ITIL", APOEMA_MACROS)
        self.assertIn("Macros ITIL", APOEMA_MACROS)
        self.assertIn("Copiar macro", MACRO_PREVIEW)
        self.assertIn("Acesso nao autorizado.", APOEMA_MACROS)
        self.assertIn("ADMIN", APOEMA_MACROS)
        self.assertIn("TECHNICIAN", APOEMA_MACROS)

    def test_no_direct_provider_calls_in_apoema_macros(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA_MACROS)

    def test_legacy_macros_page_was_removed_from_disk(self) -> None:
        self.assertFalse(LEGACY_MACROS.exists())


if __name__ == "__main__":
    unittest.main()
