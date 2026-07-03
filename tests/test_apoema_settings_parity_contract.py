from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_SETTINGS_PAGE = (ROOT / "frontend/itam-platform/src/apoema/pages/SettingsPage.tsx").read_text(encoding="utf-8")
LEGACY_SETTINGS_PAGE = ROOT / "frontend/itam-platform/src/pages/SettingsPage.tsx"
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4k-settings/SETTINGS_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaSettingsParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Settings Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/settings", MATRIX)
        self.assertIn("/apoema/settings", MATRIX)
        self.assertIn("Tema/aparência", MATRIX)
        self.assertIn("Segurança visual", MATRIX)
        self.assertIn("Somente leitura", MATRIX)

    def test_settings_routes_move_to_apoema_without_legacy_alias(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)

        self.assertNotIn("legacyCompatibilityRoutes", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/settings"', APP)
        self.assertNotIn('redirectTo: "/apoema/settings"', APP)

    def test_apoema_app_exposes_settings_surface(self) -> None:
        self.assertIn('path="settings" element={<SettingsPage />}', APOEMA_APP)
        self.assertIn('SettingsPage', APOEMA_APP)
        self.assertIn("DonorAppShell", APOEMA_APP)

    def test_settings_page_preserves_theme_preferences_and_security_copy(self) -> None:
        for term in (
            "Configurações",
            "Tema, segurança e densidade",
            "apoemaPreferences",
            "Proteção de contexto",
            "Assistência centrada em IA",
            "Nenhum token, senha, cookie ou header é renderizado nesta interface.",
            "Donor-first",
        ):
            self.assertIn(term, APOEMA_SETTINGS_PAGE)

    def test_legacy_settings_page_was_removed_from_disk(self) -> None:
        self.assertFalse(LEGACY_SETTINGS_PAGE.exists())

    def test_apoema_stays_free_of_direct_provider_calls_and_secrets(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat", "PASSWORD=", "TOKEN=", "SECRET="):
            self.assertNotIn(term, APOEMA)

    def test_lazy_loading_and_shell_boundary_remain_preserved(self) -> None:
        self.assertIn('lazy(() => import("./apoema")', APP)
        self.assertIn('Suspense fallback={<RouteLoading />}', APP)
        self.assertNotIn("AppShell", APP)
        self.assertNotIn("LegacyShellRoute", APP)
        self.assertNotIn("LegacyRoutes", APP)


if __name__ == "__main__":
    unittest.main()
