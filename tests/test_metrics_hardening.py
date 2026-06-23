from __future__ import annotations

import sys
import unittest
from pathlib import Path

from starlette.requests import Request

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import main  # noqa: E402
from fastapi import HTTPException  # noqa: E402


def make_request(headers: dict[str, str] | None = None) -> Request:
    raw_headers = [(key.lower().encode("latin-1"), value.encode("latin-1")) for key, value in (headers or {}).items()]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/metrics",
        "headers": raw_headers,
        "query_string": b"",
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 8080),
        "scheme": "http",
        "root_path": "",
        "http_version": "1.1",
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


class MetricsHardeningTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.original_environment = main.settings.environment
        self.original_metrics_token = main.settings.metrics_token

    def tearDown(self) -> None:
        main.settings.environment = self.original_environment
        main.settings.metrics_token = self.original_metrics_token

    async def test_metrics_is_available_in_local_without_token(self) -> None:
        main.settings.environment = "local"
        main.settings.metrics_token = ""

        response = await main.prometheus_metrics(make_request())

        self.assertEqual(200, response.status_code)
        self.assertIn("text/plain", response.media_type)

    async def test_metrics_is_disabled_outside_local_without_token(self) -> None:
        main.settings.environment = "staging"
        main.settings.metrics_token = ""

        with self.assertRaises(HTTPException) as ctx:
            main._require_metrics_access(make_request())

        self.assertEqual(503, ctx.exception.status_code)
        self.assertEqual("metrics_disabled_without_token", ctx.exception.detail)

    async def test_metrics_requires_matching_token_outside_local(self) -> None:
        main.settings.environment = "production"
        main.settings.metrics_token = "expected-token"

        with self.assertRaises(HTTPException) as ctx:
            main._require_metrics_access(make_request({"x-metrics-token": "wrong-token"}))

        self.assertEqual(401, ctx.exception.status_code)
        self.assertEqual("invalid_metrics_token", ctx.exception.detail)

    async def test_metrics_returns_body_with_matching_token_outside_local(self) -> None:
        main.settings.environment = "production"
        main.settings.metrics_token = "expected-token"
        main.metrics.increment("itam_metrics_hardening_test")

        response = await main.prometheus_metrics(make_request({"x-metrics-token": "expected-token"}))

        self.assertEqual(200, response.status_code)
        self.assertIn("itam_metrics_hardening_test", response.body.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
