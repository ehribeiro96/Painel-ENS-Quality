from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOEMA_APP = (ROOT / "frontend" / "itam-platform" / "src" / "apoema" / "ApoemaApp.tsx").read_text(encoding="utf-8")


class ApoemaNavigationTargetsContractTest(unittest.TestCase):
    def test_sidebar_navigation_uses_current_apoema_prefix(self) -> None:
        normalized = APOEMA_APP.replace("\n", " ")

        self.assertIn('import { Navigate, NavLink, Outlet, Route, Routes, useLocation } from "react-router-dom";', normalized)
        self.assertIn('const { pathname } = useLocation();', normalized)
        self.assertIn('const routeBase = pathname.startsWith("/apoema-preview") ? "/apoema-preview" : "/apoema";', normalized)
        self.assertIn('to={`${routeBase}/${item.to}`}', normalized)

    def test_apoema_and_preview_routes_remain_canonical(self) -> None:
        normalized = APOEMA_APP.replace("\n", " ")

        self.assertIn('function ApoemaShell({ theme }: { theme: ReturnType<typeof useThemeMode> }) {', normalized)
        self.assertIn('const routeBase = pathname.startsWith("/apoema-preview") ? "/apoema-preview" : "/apoema";', normalized)
        self.assertIn('to={`${routeBase}/${item.to}`}', normalized)
        self.assertIn('path="assets" element={<AssetsPage />}', normalized)
        self.assertIn('path="chat" element={<ChatPage />}', normalized)


if __name__ == "__main__":
    unittest.main()
