from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITICAL_TESTS = (
    "tests/test_ai_feature_flag.py",
    "tests/test_user_permission_boundaries.py",
    "tests/test_health_endpoints.py",
    "tests/test_macro_idempotency.py",
    "tests/test_import_ai_safety.py",
    "tests/test_pr1_remediation_contracts.py",
    "tests/test_authprovider_strictmode_boot_contract.py",
    "tests/test_auth_session_hardening.py",
    "tests/test_login_frontend_contract.py",
)


class SecurityQualityGatePolicyTest(unittest.TestCase):
    def test_critical_security_tests_cannot_contain_skip_directives(self) -> None:
        forbidden = ("skipTest(", "pytest.skip(", "@unittest.skip", "@pytest.mark.skip")

        for relative in CRITICAL_TESTS:
            content = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(path=relative):
                for directive in forbidden:
                    self.assertNotIn(directive, content)

    def test_ci_runs_each_critical_security_test_explicitly(self) -> None:
        workflow = (ROOT / ".github/workflows/quality-gates.yml").read_text(encoding="utf-8")

        self.assertIn("Critical security tests (actual zero skips)", workflow)
        self.assertIn("--junitxml=/tmp/critical-pytest.xml", workflow)
        self.assertIn("python scripts/assert_pytest_report.py /tmp/critical-pytest.xml", workflow)
        for relative in CRITICAL_TESTS:
            with self.subTest(path=relative):
                self.assertIn(relative, workflow)


if __name__ == "__main__":
    unittest.main()
