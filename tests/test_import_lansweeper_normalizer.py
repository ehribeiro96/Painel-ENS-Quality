from __future__ import annotations

import sys
import unittest

from tests.operational_http import ROOT

sys.path.insert(0, str(ROOT / "backend"))

from app.domains.imports.normalization.lansweeper_normalizer import normalize_asset_row


class ImportLansweeperNormalizerTest(unittest.TestCase):
    def test_name_ip_does_not_become_hostname(self) -> None:
        row = normalize_asset_row({"Name": "192.168.3.43"}, {"Name": "hostname"})
        self.assertIsNone(row["hostname"])
        self.assertEqual(row["ip_address"], "192.168.3.43")

    def test_name_ip_second_case_does_not_become_hostname(self) -> None:
        row = normalize_asset_row({"Name": "192.168.3.44"}, {"Name": "hostname"})
        self.assertIsNone(row["hostname"])
        self.assertEqual(row["ip_address"], "192.168.3.44")

    def test_valid_hostname_is_preserved(self) -> None:
        row = normalize_asset_row({"Name": "RJM22135"}, {"Name": "hostname"})
        self.assertEqual(row["hostname"], "RJM22135")
        self.assertIsNone(row["ip_address"])

    def test_empty_barcode_does_not_create_patrimony(self) -> None:
        row = normalize_asset_row({"Barcode": ""}, {"Barcode": "patrimony"})
        self.assertIsNone(row["patrimony"])

    def test_undefined_placeholder_becomes_null(self) -> None:
        row = normalize_asset_row({"Manufacturer": "Undefined"}, {"Manufacturer": "manufacturer"})
        self.assertIsNone(row["manufacturer"])

    def test_not_scanned_placeholder_becomes_null(self) -> None:
        row = normalize_asset_row({"Model": "Not scanned"}, {"Model": "model"})
        self.assertIsNone(row["model"])

    def test_custom1_wins_over_type(self) -> None:
        row = normalize_asset_row(
            {"Custom1": "MONITOR", "Type": "Windows"},
            {"Custom1": "asset_type", "Type": "fallback_asset_type"},
        )
        self.assertEqual(row["asset_type"], "MONITOR")
        self.assertEqual(row["asset_family"], "MONITOR")

    def test_type_fallback_is_used_when_custom1_is_empty(self) -> None:
        row = normalize_asset_row(
            {"Custom1": "", "Type": "Windows"},
            {"Custom1": "asset_type", "Type": "fallback_asset_type"},
        )
        self.assertEqual(row["asset_type"], "OTHER")
        self.assertEqual(row["fallback_asset_type"], "WINDOWS")

    def test_lastuser_stays_in_hint_metadata_and_not_current_user(self) -> None:
        row = normalize_asset_row(
            {"lastuser": "ENS\\usuario", "Name": "RJM22135"},
            {"lastuser": "source_metadata.imported_user_hint", "Name": "hostname"},
        )
        self.assertEqual(row["source_metadata"]["imported_user_hint"], "ENS\\usuario")
        self.assertNotIn("current_user_id", row)

    def test_common_fields_are_preserved(self) -> None:
        row = normalize_asset_row(
            {
                "Name": "RJM22135",
                "Serialnumber": "SN-001",
                "Manufacturer": "HP Inc.",
                "Model": "EliteBook 840",
                "Location": "rj",
                "State": "Active",
                "Custom1": "NOTEBOOK",
                "Type": "Windows",
            },
            {
                "Name": "hostname",
                "Serialnumber": "serial",
                "Manufacturer": "manufacturer",
                "Model": "model",
                "Location": "location",
                "State": "source_state",
                "Custom1": "asset_type",
                "Type": "fallback_asset_type",
            },
        )
        self.assertEqual(row["serial"], "SN-001")
        self.assertEqual(row["manufacturer"], "HP")
        self.assertEqual(row["model"], "ELITEBOOK 840")
        self.assertEqual(row["location"], "RJ")
        self.assertEqual(row["source_metadata"]["source_state"], "ACTIVE")

    def test_numeric_placeholder_is_treated_as_null_like_current_behavior(self) -> None:
        row = normalize_asset_row({"Name": "66", "Serialnumber": "66", "Barcode": "66"}, {"Name": "hostname", "Serialnumber": "serial", "Barcode": "patrimony"})
        self.assertIsNone(row["hostname"])
        self.assertIsNone(row["serial"])
        self.assertIsNone(row["patrimony"])
