from __future__ import annotations

import os
import time
import unittest
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import requests

ROOT = Path(__file__).resolve().parents[1]


def require_operational_env(testcase: unittest.TestCase) -> tuple[str, str, str]:
    base_url = os.getenv("OPERATIONAL_BASE_URL", "").rstrip("/")
    admin_email = os.getenv("ADMIN_EMAIL", "estevao.quality@ens.edu.br")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not base_url:
        testcase.skipTest("OPERATIONAL_BASE_URL is not set; skipping Docker-backed operational regression")
    if not admin_password:
        testcase.skipTest("ADMIN_PASSWORD is not set; skipping auth-backed operational regression")
    return base_url, admin_email, admin_password


def unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid4().hex[:10]}@ens.edu.br"


@dataclass
class OperationalClient:
    base_url: str
    admin_email: str
    admin_password: str

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.api = f"{self.base_url}/api/v1"
        self.token: str | None = None

    def login(self) -> dict:
        response = self.session.post(
            f"{self.api}/auth/login",
            json={"email": self.admin_email, "password": self.admin_password},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        self.token = payload["access_token"]
        return payload

    def headers(self) -> dict[str, str]:
        if not self.token:
            self.login()
        return {"Authorization": f"Bearer {self.token}"}

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.api}{path}", headers=self.headers(), timeout=20, **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self.session.post(f"{self.api}{path}", json=json, headers=self.headers(), timeout=20, **kwargs)

    def put(self, path: str, json: dict | None = None) -> requests.Response:
        return self.session.put(f"{self.api}{path}", json=json, headers=self.headers(), timeout=20)

    def delete(self, path: str) -> requests.Response:
        return self.session.delete(f"{self.api}{path}", headers=self.headers(), timeout=20)


class OperationalTestCase(unittest.TestCase):
    client: OperationalClient

    @classmethod
    def setUpClass(cls) -> None:
        base_url, admin_email, admin_password = require_operational_env(cls("run"))
        wait_for_ready(base_url)
        cls.client = OperationalClient(base_url, admin_email, admin_password)
        cls.client.login()

    def create_user(self, role: str = "VIEWER", password: str | None = None, prefix: str = "qa.user") -> dict:
        payload = {
            "name": f"QA {role.title()}",
            "email": unique_email(prefix),
            "role": role,
            "status": "ACTIVE",
            "department": "TI",
            "business_unit": "Matriz",
        }
        if password:
            payload["password"] = password
        response = self.client.post("/users", payload)
        response.raise_for_status()
        return response.json()

    def create_asset(self, **overrides) -> dict:
        suffix = uuid4().hex[:8].upper()
        payload = {
            "hostname": f"RJMTEST{suffix}",
            "patrimony": f"PAT-TEST-{suffix}",
            "serial": f"SN-TEST-{suffix}",
            "manufacturer": "Dell",
            "model": "Latitude",
            "asset_type": "NOTEBOOK",
            "status": "STOCK",
            "location": "Matriz",
        }
        payload.update(overrides)
        response = self.client.post("/assets", payload)
        response.raise_for_status()
        return response.json()


def wait_for_ready(base_url: str) -> None:
    deadline = time.time() + 90
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/health/ready", timeout=5)
            if response.status_code == 200:
                return
        except Exception as exc:  # noqa: BLE001 - used only for retry diagnostics
            last_error = exc
        time.sleep(2)
    raise AssertionError(f"Operational app did not become ready at {base_url}: {last_error}")
