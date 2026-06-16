from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.main import _apply_security_headers  # noqa: E402
from starlette.responses import Response  # noqa: E402

pytestmark = [pytest.mark.security, pytest.mark.unit]


class SecurityHeadersTest(unittest.TestCase):
    def test_spa_routes_get_hardened_csp_without_unsafe_inline_script(self) -> None:
        response = Response()

        _apply_security_headers(response, "/")

        csp = response.headers["content-security-policy"]
        self.assertIn("script-src 'self'", csp)
        self.assertNotIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertNotIn("content-security-policy-report-only", response.headers)

    def test_legacy_routes_keep_enforced_inline_compatibility_and_report_only(self) -> None:
        response = Response()

        _apply_security_headers(response, "/admin/")

        enforced = response.headers["content-security-policy"]
        report_only = response.headers["content-security-policy-report-only"]
        self.assertIn("script-src 'self' 'unsafe-inline'", enforced)
        self.assertIn("script-src 'self'", report_only)
        self.assertNotIn("unsafe-inline", report_only)
