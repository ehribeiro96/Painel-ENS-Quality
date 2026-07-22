from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH = (ROOT / "frontend/itam-platform/src/lib/auth.tsx").read_text(encoding="utf-8")
API = (ROOT / "frontend/itam-platform/src/lib/api.ts").read_text(encoding="utf-8")
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
MAIN = (ROOT / "frontend/itam-platform/src/main.tsx").read_text(encoding="utf-8")
LOGIN_PAGE = ROOT / "frontend/itam-platform/src/pages/LoginPage.tsx"
NOT_FOUND_PAGE = ROOT / "frontend/itam-platform/src/pages/NotFoundPage.tsx"
APPSHELL = ROOT / "frontend/itam-platform/src/components/AppShell.tsx"


class AuthProviderStrictModeBootContractTest(unittest.TestCase):
    def test_auth_provider_treats_abort_as_neutral_during_boot(self) -> None:
        self.assertIn("function isAbortError(error: unknown)", AUTH)
        self.assertIn('error.name === "AbortError"', AUTH)
        self.assertIn("if (isAbortError(error))", AUTH)
        self.assertIn("throw error;", AUTH)

        abort_branch = re.search(r"if \(isAbortError\(error\)\) \{\s*throw error;\s*\}", AUTH)
        self.assertIsNotNone(abort_branch)
        self.assertNotIn("clearSession()", abort_branch.group(0))
        self.assertNotIn("setUser(null)", abort_branch.group(0))
        self.assertNotIn("setLoading(false)", abort_branch.group(0))

    def test_boot_refresh_respects_cleanup_abort_signal(self) -> None:
        self.assertIn("let sharedRefreshRequest: Promise<TokenResponse> | null = null;", AUTH)
        self.assertIn("function requestRefresh(signal?: AbortSignal)", AUTH)
        self.assertIn("if (!signal && sharedRefreshRequest)", AUTH)
        self.assertIn("sharedRefreshRequest = refreshRequest;", AUTH)
        self.assertIn("refreshSession(controller.signal)", AUTH)
        self.assertIn("controller.abort();", AUTH)

    def test_session_is_cleared_only_for_real_unauthorized_refresh(self) -> None:
        unauthorized_branch = re.search(r"if \(error instanceof ApiError && \(error.status === 401 \|\| error.status === 403\)\) \{(?P<body>.*?)\n        \}", AUTH, re.S)
        self.assertIsNotNone(unauthorized_branch)
        self.assertIn("clearSession();", unauthorized_branch.group("body"))
        self.assertIn("return tokenRef.current;", unauthorized_branch.group("body"))
        self.assertNotRegex(AUTH, r"catch\(\(error: unknown\) => \{\s*clearSession\(\);")

    def test_api_refresh_accepts_signal_and_keeps_credentials_include(self) -> None:
        self.assertIn('refresh: (options: Pick<RequestInit, "signal"> = {})', API)
        self.assertIn('request<TokenResponse>("/auth/refresh", { method: "POST", skipAuthRefresh: true, ...options })', API)
        self.assertIn('credentials: fetchInit.credentials ?? "include"', API)
        self.assertIn("let refreshError: unknown = null;", API)
        self.assertIn("throw refreshError;", API)
        refresh_retry = re.search(
            r"const nextToken = await refreshAccessToken\(\)\.catch\(\(error: unknown\) => \{\s*refreshError = error;\s*return null;\s*\}\);",
            API,
        )
        self.assertIsNotNone(refresh_retry)

    def test_protected_route_waits_for_loading_before_login_redirect(self) -> None:
        loading_index = APP.index("if (loading)")
        redirect_index = APP.index('<Navigate to="/login"')
        self.assertLess(loading_index, redirect_index)
        self.assertIn("return <RouteLoading />;", APP[loading_index:redirect_index])
        self.assertIn("<StrictMode>", MAIN)

    def test_login_and_apoema_only_boundaries_remain_intact(self) -> None:
        self.assertTrue(LOGIN_PAGE.exists())
        self.assertTrue(NOT_FOUND_PAGE.exists())
        self.assertFalse(APPSHELL.exists())
        self.assertIn('path="/login" element={<LoginPage />}', APP)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', APP)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', APP)
        self.assertIn('path="/ai-chat" element={<Navigate to="/apoema/chat" replace />} ', APP.replace("\n", " "))

        for legacy_alias in (
            'path="/assets"',
            'path="/audit-logs"',
            'path="/imports"',
            'path="/macros"',
            'path="/stock"',
            'path="/signatures"',
            'path="/assignments"',
            'path="/users"',
            'path="/settings"',
        ):
            self.assertNotIn(legacy_alias, APP)


if __name__ == "__main__":
    unittest.main()
