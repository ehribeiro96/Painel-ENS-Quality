from __future__ import annotations

import re

import requests

from tests.operational_http import OperationalTestCase


class LegacyAndSpaRoutesTest(OperationalTestCase):
    def test_legacy_signature_routes_are_mounted(self) -> None:
        public = requests.get(f"{self.client.base_url}/assinaturas/", timeout=20)
        self.assertEqual(public.status_code, 200)
        self.assertIn("html", public.text.lower())

        admin = requests.get(f"{self.client.base_url}/admin/", allow_redirects=False, timeout=20)
        self.assertIn(admin.status_code, {200, 302})

    def test_spa_fallback_and_vite_assets(self) -> None:
        root = requests.get(f"{self.client.base_url}/", timeout=20)
        self.assertEqual(root.status_code, 200)
        self.assertIn("<div id=\"root\"", root.text)

        for path in ("/assets/example-id", "/users", "/imports", "/signatures", "/audit-logs"):
            response = requests.get(f"{self.client.base_url}{path}", timeout=20)
            self.assertEqual(response.status_code, 200)
            self.assertIn("<div id=\"root\"", response.text)

        asset_match = re.search(r"/_assets/[^\"']+", root.text)
        self.assertIsNotNone(asset_match)
        asset = requests.get(f"{self.client.base_url}{asset_match.group(0)}", timeout=20)
        self.assertEqual(asset.status_code, 200)
        self.assertGreater(len(asset.content), 1000)
