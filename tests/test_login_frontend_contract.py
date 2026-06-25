from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGIN = (ROOT / "frontend/itam-platform/src/pages/LoginPage.tsx").read_text(encoding="utf-8")
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
AUTH = (ROOT / "frontend/itam-platform/src/lib/auth.tsx").read_text(encoding="utf-8")
API = (ROOT / "frontend/itam-platform/src/lib/api.ts").read_text(encoding="utf-8")
STYLES = (ROOT / "frontend/itam-platform/src/styles.css").read_text(encoding="utf-8")


class LoginFrontendContractTest(unittest.TestCase):
    def test_login_page_exports_function_component_and_form(self) -> None:
        self.assertIn("export function LoginPage()", LOGIN)
        self.assertIn('Base44Surface className="base44-login-card" as="form"', LOGIN)
        self.assertIn('type="email"', LOGIN)
        self.assertIn('type="password"', LOGIN)
        self.assertIn("handleSubmit", LOGIN)

    def test_login_page_handles_loading_and_error_states(self) -> None:
        self.assertIn("if (loading)", LOGIN)
        self.assertIn("LoadingBlock label=\"Validando sessão...\"", LOGIN)
        self.assertIn("getLoginErrorMessage", LOGIN)
        self.assertIn("Credenciais inválidas. Verifique e-mail e senha.", LOGIN)
        self.assertIn("Backend indisponível. Tente novamente em instantes.", LOGIN)
        self.assertIn("bootError", LOGIN)

    def test_login_page_does_not_use_mock_login_shortcut(self) -> None:
        lowered = LOGIN.lower()
        self.assertNotIn("mock login", lowered)
        self.assertNotIn("login mock", lowered)

    def test_app_preserves_login_route_and_protected_routes(self) -> None:
        self.assertIn('path="/login" element={<LoginPage />} ', APP.replace("\n", " "))
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />} ', APP.replace("\n", " "))
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema-preview" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn("RouteLoading", APP)

    def test_auth_context_has_timeout_and_boot_error_handling(self) -> None:
        self.assertIn("AUTH_BOOT_TIMEOUT_MS", AUTH)
        self.assertIn("AbortController", AUTH)
        self.assertIn("sharedRefreshRequest", AUTH)
        self.assertIn("refreshSession()", AUTH)
        self.assertIn("setBootError", AUTH)
        self.assertIn("bootError", AUTH)
        self.assertIn("api.login(email, password, { signal })", AUTH)
        self.assertIn("requestRefresh(signal ? controller.signal : undefined)", AUTH)

    def test_api_auth_methods_accept_abort_signals(self) -> None:
        self.assertIn('login: (email: string, password: string, options: Pick<RequestInit, "signal"> = {})', API)
        self.assertIn('refresh: (options: Pick<RequestInit, "signal"> = {})', API)
        self.assertIn('logout: (token?: string | null, options: Pick<RequestInit, "signal"> = {})', API)

    def test_login_warning_style_exists(self) -> None:
        self.assertIn(".base44-inline-alert.warning", STYLES)
        self.assertIn("color: var(--color-warning);", STYLES)


if __name__ == "__main__":
    unittest.main()
