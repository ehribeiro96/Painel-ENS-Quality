from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ops" / "Review-LegacyEnsDbPreApply.ps1"


@unittest.skipIf(shutil.which("powershell") is None, "PowerShell is required for this operational script")
class LegacyEnsDbPreApplyReviewScriptTest(unittest.TestCase):
    def test_script_parses_without_errors(self) -> None:
        command = (
            "$errors=$null; $tokens=$null; "
            f"[System.Management.Automation.Language.Parser]::ParseFile('{SCRIPT}',[ref]$tokens,[ref]$errors) | Out-Null; "
            "if ($errors) { $errors | ConvertTo-Json -Depth 4; exit 1 }"
        )

        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual("", result.stdout.strip())
        self.assertEqual("", result.stderr.strip())
        self.assertEqual(0, result.returncode)

    def test_script_generates_masked_warning_report_without_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            dryrun = temp_path / "legacy_ens_db_dryrun_test.json"
            output = temp_path / "pre_apply_review.md"
            dryrun.write_text(
                json.dumps(
                    {
                        "sqlite_path": str(temp_path / "missing_ens.db"),
                        "mode": "DryRun",
                        "classification": "LEGACY_SQLITE_SEED_SOURCE",
                        "inventory": {
                            "quality": {
                                "duplicate_emails": 0,
                                "duplicate_logins": 2,
                            },
                            "sensitive_fields_discarded": [
                                "password_hash",
                                "eh_admin",
                                "must_change",
                            ],
                        },
                        "postgres_result": {
                            "total_read": 123,
                            "valid_candidates": 123,
                            "created": 122,
                            "updated": 1,
                            "ignored": 0,
                            "duplicates": 0,
                            "invalid": 0,
                            "without_email": 0,
                            "without_name": 0,
                            "failures": 0,
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(SCRIPT),
                    "-DryRunReportPath",
                    str(dryrun),
                    "-OutputPath",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            report = output.read_text(encoding="utf-8")
            self.assertIn("APPROVED_WITH_WARNINGS", report)
            self.assertIn("Apply executado nesta etapa: **nao**", report)
            self.assertIn("password_hash", report)
            self.assertNotIn("--mode Apply", result.stdout)
            self.assertNotIn("APPLY_LEGACY_ENS_DB", result.stdout)


if __name__ == "__main__":
    unittest.main()
