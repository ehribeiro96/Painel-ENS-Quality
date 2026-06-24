from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_SIGNATURES = (ROOT / "frontend/itam-platform/src/apoema/pages/SignaturesPage.tsx").read_text(encoding="utf-8")
LEGACY_SIGNATURES = (ROOT / "frontend/itam-platform/src/pages/SignaturesPage.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4h-signatures/SIGNATURES_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaSignaturesParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Signatures Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/signatures", MATRIX)
        self.assertIn("/apoema/signatures", MATRIX)
        self.assertIn("Paridade", MATRIX)

    def test_signatures_route_points_to_apoema_signatures_page(self) -> None:
        self.assertIn('path="signatures" element={<SignaturesPage />}', APOEMA_APP)
        alias_match = re.search(r"const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(alias_match)
        alias_block = alias_match.group(1)
        self.assertIn('path: "/signatures"', alias_block)
        self.assertIn('migrationTarget: "apoema:signatures"', alias_block)
        self.assertIn('redirectTo: "/apoema/signatures"', alias_block)
        legacy_match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(legacy_match)
        legacy_block = legacy_match.group(1)
        self.assertNotIn('path: "/signatures"', legacy_block)

    def test_signatures_page_contains_operational_parity_surface(self) -> None:
        for term in ("Base44CopyBlock", "Base44EmptyState", "Base44OperationalGrid", "Base44PageHeader", "Base44StatusBadge", "Base44Surface", "Base44UserCard", "LoadingBlock"):
            self.assertIn(term, APOEMA_SIGNATURES)
        for term in ("signatureGenerate", "signatureDownloadHtml", "Apoema Assinaturas", "Assinaturas Corporativas", "Abrir legado", "HTML da assinatura copiado"):
            self.assertIn(term, APOEMA_SIGNATURES)

    def test_legacy_signatures_page_remains_available_for_compatibility(self) -> None:
        for term in ("signatureGenerate", "signatureDownloadHtml", "Base44CopyBlock", "Base44UserCard"):
            self.assertIn(term, LEGACY_SIGNATURES)

    def test_apoema_stays_free_of_direct_provider_calls(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA)

    def test_related_apoema_aliases_and_lazy_loading_remain_preserved(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('lazy(() => import("./apoema")', normalized)
        self.assertIn('Suspense fallback={<RouteLoading />}', APP)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)

        for target in (
            'redirectTo: "/apoema/signatures"',
            'redirectTo: "/apoema/stock"',
            'redirectTo: "/apoema/macros"',
            'redirectTo: "/apoema/imports"',
            'redirectTo: "/apoema/audit-logs"',
            'redirectTo: "/apoema/assets"',
            'redirectTo: "/apoema/assets/:id"',
            'redirectTo: "/apoema/chat"',
        ):
            self.assertIn(target, APP)

        self.assertIn('path: "/ai-chat"', APP)
        self.assertIn('migrationTarget: "apoema:chat"', APP)
        self.assertIn('path="chat" element={<ChatPage />}', APOEMA_APP)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)


if __name__ == "__main__":
    unittest.main()
