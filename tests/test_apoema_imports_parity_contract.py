from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
IMPORTS_PAGE = (ROOT / "frontend/itam-platform/src/apoema/pages/ImportsPage.tsx").read_text(encoding="utf-8")


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaImportsParityContractTest(unittest.TestCase):
    def test_imports_matrix_and_routes_map_to_apoema(self) -> None:
        matrix = ROOT / "docs/audit/apoema-only-phase-4e-imports/IMPORTS_PARITY_MATRIX_20260623.md"
        self.assertTrue(matrix.exists())
        matrix_text = matrix.read_text(encoding="utf-8")
        self.assertIn("/imports legacy", matrix_text)
        self.assertIn("/apoema/imports", matrix_text)

        normalized_app = APP.replace("\n", " ")
        self.assertIn('path: "/imports"', normalized_app)
        self.assertIn('migrationTarget: "apoema:imports"', normalized_app)
        self.assertIn('redirectTo: "/apoema/imports"', normalized_app)
        self.assertIn('path="imports" element={<ImportsPage />}', APOEMA_APP.replace("\n", " "))
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized_app)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized_app)

    def test_imports_no_longer_live_in_legacy_shell(self) -> None:
        legacy_match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(legacy_match)
        legacy_block = legacy_match.group(1)
        self.assertNotIn('path: "/imports"', legacy_block)

    def test_imports_page_is_apoema_native_and_api_backed(self) -> None:
        self.assertIn("Base44ImportPanel", IMPORTS_PAGE)
        self.assertIn("Base44EmptyState", IMPORTS_PAGE)
        self.assertIn("Base44InfoGrid", IMPORTS_PAGE)
        self.assertIn("Base44PageHeader", IMPORTS_PAGE)
        self.assertIn("Base44StatusBadge", IMPORTS_PAGE)
        self.assertIn("LoadingBlock", IMPORTS_PAGE)
        self.assertIn(".imports(token)", IMPORTS_PAGE)
        self.assertIn("importUpload", IMPORTS_PAGE)
        self.assertIn("importPreview", IMPORTS_PAGE)
        self.assertIn("importStaging", IMPORTS_PAGE)
        self.assertIn("importConflicts", IMPORTS_PAGE)
        self.assertIn("importValidationErrors", IMPORTS_PAGE)
        self.assertNotIn("localhost:11434", APOEMA)
        self.assertNotIn("OLLAMA_BASE_URL", APOEMA)
        self.assertNotIn("HERMES_BASE_URL", APOEMA)
        self.assertNotIn("COMPOSIO", APOEMA)
        self.assertNotIn("/api/chat", APOEMA)


if __name__ == "__main__":
    unittest.main()
