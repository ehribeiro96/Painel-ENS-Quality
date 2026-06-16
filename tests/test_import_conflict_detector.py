from __future__ import annotations

import sys
import unittest

import pytest

from tests.operational_http import ROOT

sys.path.insert(0, str(ROOT / "backend"))

from app.domains.imports.classification.conflict_detector import build_internal_duplicate_plan
from app.domains.imports.normalization.lansweeper_normalizer import normalize_asset_row
from app.shared.enums import ImportDecision

pytestmark = [pytest.mark.imports, pytest.mark.unit]


class ImportConflictDetectorTest(unittest.TestCase):
    def test_serial_duplicate_generates_conflict_with_human_fields(self) -> None:
        first = normalize_asset_row({"Name": "RJM1", "Serialnumber": "SN-001"}, {"Name": "hostname", "Serialnumber": "serial"})
        second = normalize_asset_row({"Name": "RJM2", "Serialnumber": "SN-001"}, {"Name": "hostname", "Serialnumber": "serial"})
        plan = build_internal_duplicate_plan([first, second])
        self.assertEqual(plan[0]["decision"], ImportDecision.CONFLICT)
        self.assertIn("reason", plan[0]["issue"])
        self.assertIn("conflict_key", plan[0]["issue"])
        self.assertIn("recommended_action", plan[0]["issue"])

    def test_hostname_duplicate_with_different_serials_generates_conflict(self) -> None:
        first = normalize_asset_row({"Name": "RJM1", "Serialnumber": "SN-001"}, {"Name": "hostname", "Serialnumber": "serial"})
        second = normalize_asset_row({"Name": "RJM1", "Serialnumber": "SN-002"}, {"Name": "hostname", "Serialnumber": "serial"})
        plan = build_internal_duplicate_plan([first, second])
        self.assertEqual(plan[0]["decision"], ImportDecision.CONFLICT)
        self.assertEqual(plan[1]["decision"], ImportDecision.CONFLICT)
        self.assertTrue(str(plan[0]["issue"]["message"]).startswith("Conflito real"))

    def test_equivalent_duplicate_is_skipped_with_reason(self) -> None:
        first = normalize_asset_row({"Name": "RJM1", "Serialnumber": "SN-001", "Lastseen": "2026-01-01"}, {"Name": "hostname", "Serialnumber": "serial", "Lastseen": "last_login"})
        second = normalize_asset_row({"Name": "RJM1", "Serialnumber": "SN-001", "Lastseen": "2026-06-01"}, {"Name": "hostname", "Serialnumber": "serial", "Lastseen": "last_login"})
        plan = build_internal_duplicate_plan([first, second])
        self.assertEqual(plan[0]["decision"], ImportDecision.SKIPPED_DUPLICATE_IN_FILE)
        self.assertIn("reason", plan[0]["issue"])
        self.assertIn("conflict_key", plan[0]["issue"])
        self.assertIn("recommended_action", plan[0]["issue"])
