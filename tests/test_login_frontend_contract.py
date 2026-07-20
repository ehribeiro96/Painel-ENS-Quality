from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGIN = (ROOT / "frontend/itam-platform/src/pages/LoginPage.tsx").read_text(encoding="utf-8")
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
AUTH = (ROOT / "frontend/itam-platform/src/lib/auth.tsx").read_text(encoding="utf-8")
API = (ROOT / "frontend/itam-platform/src/lib/api.ts").read_text(encoding="utf-8")
SHELL = (ROOT / "frontend/itam-platform/src/apoema/components/DonorAppShell.tsx").read_text(encoding="utf-8")
STYLES = (ROOT / "frontend/itam-platform/src/styles.css").read_text(encoding="utf-8")


class LoginFrontendContractTest(unittest.TestCase):
    def test_login_page_exports_function_component_and_form(self) -> None:
        self.assertIn("export function LoginPage()", LOGIN)
        self.assertIn("rounded-[28px]", LOGIN)
        self.assertIn("bg-slate-950/70", LOGIN)
        self.assertIn("Apoema", LOGIN)
        self.assertIn('type="email"', LOGIN)
        self.assertIn('type="password"', LOGIN)
        self.assertIn("handleLogin", LOGIN)

    def test_login_page_handles_loading_and_error_states(self) -> None:
        self.assertIn("if (loading)", LOGIN)
        self.assertIn("Carregando módulo...", LOGIN)
        self.assertIn("getLoginErrorMessage", LOGIN)
        self.assertIn("Credenciais inválidas. Verifique e-mail e senha.", LOGIN)
        self.assertIn("Backend indisponível. Tente novamente em instantes.", LOGIN)
        self.assertIn("bootError", LOGIN)
        self.assertIn("transitioning", LOGIN)
        self.assertIn("Esqueceu a senha?", LOGIN)
        self.assertIn("requestReset", LOGIN)
        self.assertIn("setNewPassword", LOGIN)

    def test_login_page_does_not_use_mock_login_shortcut(self) -> None:
        lowered = LOGIN.lower()
        self.assertNotIn("mock login", lowered)
        self.assertNotIn("login mock", lowered)
        self.assertNotIn("base44surface", lowered)
        self.assertNotIn("base44pageheader", lowered)
        self.assertNotIn("base44shellaccent", lowered)
        self.assertNotIn("hermesops sentinel", lowered)

    def test_app_preserves_login_route_and_protected_routes(self) -> None:
        self.assertIn('path="/login" element={<LoginPage />} ', APP.replace("\n", " "))
        self.assertIn('path="/" element={<Navigate to="/apoema" replace />} ', APP.replace("\n", " "))
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="/ai-chat" element={<Navigate to="/apoema/chat" replace />} ', APP.replace("\n", " "))
        self.assertIn("RouteLoading", APP)

    def test_auth_context_has_timeout_and_boot_error_handling(self) -> None:
        self.assertIn("AUTH_BOOT_TIMEOUT_MS", AUTH)
        self.assertIn("AUTH_SESSION_STORAGE_KEY", AUTH)
        self.assertIn("window.localStorage", AUTH)
        self.assertIn("AbortController", AUTH)
        self.assertIn("sharedRefreshRequest", AUTH)
        self.assertIn("refreshSession(controller.signal)", AUTH)
        self.assertIn("setBootError", AUTH)
        self.assertIn("bootError", AUTH)
        self.assertIn("api.login(email, password, { signal })", AUTH)
        self.assertIn("requestRefresh(signal ? controller.signal : undefined)", AUTH)

    def test_api_auth_methods_accept_abort_signals(self) -> None:
        self.assertIn('login: (email: string, password: string, options: Pick<RequestInit, "signal"> = {})', API)
        self.assertIn('refresh: (options: Pick<RequestInit, "signal"> = {})', API)
        self.assertIn('logout: (token?: string | null, options: Pick<RequestInit, "signal"> = {})', API)

    def test_logout_waits_for_session_cleanup_before_navigation(self) -> None:
        self.assertIn("onClick={async () => {", SHELL)
        self.assertIn("await signOut();", SHELL)
        self.assertLess(SHELL.index("await signOut();"), SHELL.index('navigate("/login");'))
        self.assertNotIn("void signOut();", SHELL)

    def test_login_warning_style_exists(self) -> None:
        self.assertIn(".glass-surface", STYLES)
        self.assertIn(".shadow-glass", STYLES)
        self.assertNotIn(".apoema-login-shell", STYLES)
        self.assertNotIn(".apoema-login-feature", STYLES)


if __name__ == "__main__":
    unittest.main()
