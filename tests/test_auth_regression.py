from __future__ import annotations

import os

import requests

from tests.operational_http import OperationalTestCase


class AuthRegressionTest(OperationalTestCase):
    def test_login_me_refresh_logout_and_refresh_after_logout(self) -> None:
        login_payload = self.client.login()
        self.assertEqual(login_payload["user"]["email"], os.getenv("ADMIN_EMAIL", "estevao.quality@ens.edu.br"))
        self.assertIn("access_token", login_payload)
        self.assertIn("ens_itam_refresh", self.client.session.cookies)

        me = self.client.get("/auth/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], os.getenv("ADMIN_EMAIL", "estevao.quality@ens.edu.br"))

        refresh = self.client.session.post(f"{self.client.api}/auth/refresh", timeout=20)
        self.assertEqual(refresh.status_code, 200)
        self.assertIn("access_token", refresh.json())

        logout = self.client.session.post(f"{self.client.api}/auth/logout", headers=self.client.headers(), timeout=20)
        self.assertEqual(logout.status_code, 200)

        refresh_after_logout = self.client.session.post(f"{self.client.api}/auth/refresh", timeout=20)
        self.assertEqual(refresh_after_logout.status_code, 401)

    def test_invalid_login_and_protected_route_without_token(self) -> None:
        invalid = requests.post(
            f"{self.client.api}/auth/login",
            json={"email": os.getenv("ADMIN_EMAIL", "estevao.quality@ens.edu.br"), "password": "definitely-not-valid"},
            timeout=20,
        )
        self.assertEqual(invalid.status_code, 401)

        no_token = requests.get(f"{self.client.api}/assets", timeout=20)
        self.assertEqual(no_token.status_code, 401)

    def test_no_real_password_is_committed_in_docs_or_tests(self) -> None:
        forbidden = os.getenv("ADMIN_PASSWORD")
        if not forbidden:
            self.skipTest("ADMIN_PASSWORD is not set")
        scanned_roots = ["README.md", "docs", "tests", "scripts", "docker-compose.yml", ".env.example"]
        for root in scanned_roots:
            path = self.client_path(root)
            if path.is_file():
                self.assertNotIn(forbidden, path.read_text(encoding="utf-8", errors="ignore"), str(path))
            elif path.is_dir():
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        self.assertNotIn(forbidden, file_path.read_text(encoding="utf-8", errors="ignore"), str(file_path))

    @staticmethod
    def client_path(relative: str):
        from tests.operational_http import ROOT

        return ROOT / relative
