from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")

REMOVED_PAGES = [
    ROOT / "frontend/itam-platform/src/pages/AiChatPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/AssetDetailsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/AssetsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/AssignmentsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/AuditLogsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/DashboardPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/ImportsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/MacrosPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/SettingsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/SignaturesPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/StockPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/UserDetailsPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/UsersPage.tsx",
]

PRESERVED_PAGES = [
    ROOT / "frontend/itam-platform/src/pages/LoginPage.tsx",
    ROOT / "frontend/itam-platform/src/pages/NotFoundPage.tsx",
]


class ApoemaRemoveLegacyPagesContractTest(unittest.TestCase):
    def test_removed_pages_are_no_longer_present_on_disk(self) -> None:
        for path in REMOVED_PAGES:
            self.assertFalse(path.exists(), str(path))

    def test_preserved_pages_still_exist(self) -> None:
        for path in PRESERVED_PAGES:
            self.assertTrue(path.exists(), str(path))

    def test_app_only_imports_preserved_pages_from_src_pages(self) -> None:
        self.assertIn("./pages/LoginPage", APP)
        self.assertIn("./pages/NotFoundPage", APP)
        for page_name in (
            "AiChatPage",
            "AssetDetailsPage",
            "AssetsPage",
            "AssignmentsPage",
            "AuditLogsPage",
            "DashboardPage",
            "ImportsPage",
            "MacrosPage",
            "SettingsPage",
            "SignaturesPage",
            "StockPage",
            "UserDetailsPage",
            "UsersPage",
        ):
            self.assertNotIn(f"./pages/{page_name}", APP)


if __name__ == "__main__":
    unittest.main()
