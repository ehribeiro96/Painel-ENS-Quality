from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from uuid import uuid4

from tests.operational_http import ROOT

sys.path.insert(0, str(ROOT / "backend"))

from app.domains.imports.classification.conflict_detector import build_internal_duplicate_plan
from app.domains.imports.classification.row_classifier import classify_row
from app.domains.imports.normalization.lansweeper_normalizer import normalize_asset_row
from app.shared.enums import ImportDecision


@dataclass(frozen=True)
class FakeAsset:
    id: object
    location: str | None = None
    status: str = "IN_USE"


class ImportRowClassifierTest(unittest.TestCase):
    def test_safe_create_is_preserved(self) -> None:
        raw_row = {"Name": "RJM22135", "Serialnumber": "SN-001"}
        normalized = normalize_asset_row(raw_row, {"Name": "hostname", "Serialnumber": "serial"})
        decision, issues, matched_asset_id, merge_action = classify_row(raw_row, normalized, None, {}, {}, {}, set())
        self.assertEqual(decision, ImportDecision.CREATE)
        self.assertEqual(issues, [])
        self.assertIsNone(matched_asset_id)
        self.assertEqual(merge_action, "CREATE_ASSET")

    def test_safe_update_is_preserved_when_existing_asset_matches(self) -> None:
        raw_row = {"Name": "RJM22135", "Serialnumber": "SN-001", "Location": "RJ"}
        normalized = normalize_asset_row(raw_row, {"Name": "hostname", "Serialnumber": "serial", "Location": "location"})
        existing = FakeAsset(id=uuid4(), location="RJ", status="IN_USE")
        decision, issues, matched_asset_id, merge_action = classify_row(raw_row, normalized, None, {"SN-001": existing}, {}, {}, set())
        self.assertEqual(decision, ImportDecision.SAFE_UPDATE)
        self.assertEqual(issues, [])
        self.assertEqual(matched_asset_id, existing.id)
        self.assertEqual(merge_action, "UPDATE_TRUSTED_FIELDS")

    def test_review_required_is_preserved_for_ip_only_source_key(self) -> None:
        raw_row = {"Name": "192.168.3.43", "Scanserver": "scan-rj"}
        normalized = normalize_asset_row(raw_row, {"Name": "hostname", "Scanserver": "source"})
        decision, issues, matched_asset_id, merge_action = classify_row(raw_row, normalized, None, {}, {}, {}, set())
        self.assertEqual(decision, ImportDecision.REVIEW_REQUIRED)
        self.assertIsNone(matched_asset_id)
        self.assertEqual(merge_action, "REVIEW_IP_ONLY_SOURCE_KEY")
        self.assertIn("reason", issues[0])
        self.assertIn("recommended_action", issues[0])

    def test_invalid_row_stays_invalid(self) -> None:
        raw_row = {}
        normalized = {}
        decision, issues, matched_asset_id, merge_action = classify_row(raw_row, normalized, None, {}, {}, {}, set())
        self.assertEqual(decision, ImportDecision.INVALID)
        self.assertIsNone(matched_asset_id)
        self.assertIsNone(merge_action)
        self.assertTrue(issues)

    def test_duplicate_equivalent_row_is_skipped(self) -> None:
        raw_row = {"Name": "RJM22135", "Serialnumber": "SN-001"}
        first = normalize_asset_row(raw_row, {"Name": "hostname", "Serialnumber": "serial"})
        second = normalize_asset_row(raw_row, {"Name": "hostname", "Serialnumber": "serial"})
        plan = build_internal_duplicate_plan([first, second])
        duplicate_action = plan.get(1) or plan.get(0)
        self.assertIsNotNone(duplicate_action)
        decision, issues, matched_asset_id, merge_action = classify_row(raw_row, second, duplicate_action, {}, {}, {}, set())
        self.assertEqual(decision, ImportDecision.SKIPPED_DUPLICATE_IN_FILE)
        self.assertIsNone(matched_asset_id)
        self.assertEqual(merge_action, "SKIP_DUPLICATE_IN_FILE")
        self.assertIn("reason", issues[0])

    def test_conflict_preserves_reason_and_recommended_action(self) -> None:
        raw_row = {"Name": "RJM1", "Serialnumber": "SN-001"}
        normalized = normalize_asset_row(raw_row, {"Name": "hostname", "Serialnumber": "serial"})
        plan = build_internal_duplicate_plan(
            [
                normalized,
                normalize_asset_row({"Name": "RJM2", "Serialnumber": "SN-001"}, {"Name": "hostname", "Serialnumber": "serial"}),
            ]
        )
        decision, issues, matched_asset_id, merge_action = classify_row(raw_row, normalized, plan[0], {}, {}, {}, set())
        self.assertEqual(decision, ImportDecision.CONFLICT)
        self.assertIsNone(matched_asset_id)
        self.assertEqual(merge_action, "REVIEW")
        self.assertIn("reason", issues[0])
        self.assertIn("recommended_action", issues[0])
