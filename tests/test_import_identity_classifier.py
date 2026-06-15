from __future__ import annotations

import sys
import unittest

from tests.operational_http import ROOT

sys.path.insert(0, str(ROOT / "backend"))

from app.domains.imports.classification.identity_classifier import (
    analyze_identity,
    identity_for,
    is_ip_only,
    is_valid_hostname,
    is_valid_patrimony,
    is_valid_serial,
)
from app.domains.imports.normalization.lansweeper_normalizer import normalize_asset_row


class ImportIdentityClassifierTest(unittest.TestCase):
    def test_serial_valid_is_primary_identity(self) -> None:
        analysis = analyze_identity({"serial": "SN-001", "hostname": "RJM22135", "asset_family": "COMPUTER"})
        self.assertTrue(is_valid_serial("SN-001"))
        self.assertEqual(analysis.primary_type, "serial")
        self.assertEqual(analysis.primary_value, "SN-001")
        self.assertEqual(analysis.confidence, "HIGH")

    def test_patrimony_valid_is_primary_identity_when_present(self) -> None:
        analysis = analyze_identity({"patrimony": "PAT-001", "hostname": "RJM22135"})
        self.assertTrue(is_valid_patrimony("PAT-001"))
        self.assertEqual(analysis.primary_type, "patrimony")
        self.assertEqual(analysis.primary_value, "PAT-001")

    def test_hostname_valid_and_non_ip_is_accepted(self) -> None:
        analysis = analyze_identity({"hostname": "RJM22135"})
        self.assertTrue(is_valid_hostname("RJM22135"))
        self.assertEqual(analysis.primary_type, "hostname")
        self.assertEqual(identity_for({"hostname": "RJM22135"}), ("hostname", "RJM22135"))

    def test_ip_is_not_hostname_and_ip_only_is_reviewable(self) -> None:
        normalized = normalize_asset_row({"Name": "192.168.3.43", "Scanserver": "scan-rj"}, {"Name": "hostname", "Scanserver": "source"})
        analysis = analyze_identity(normalized)
        self.assertFalse(is_valid_hostname("192.168.3.43"))
        self.assertTrue(analysis.ip_only)
        self.assertTrue(is_ip_only(normalized))
        self.assertEqual(analysis.reason, "Linha sem identidade patrimonial forte; IP/name de origem preservado como chave externa para revisao.")

    def test_missing_identity_is_not_usable(self) -> None:
        analysis = analyze_identity({})
        self.assertIsNone(analysis.primary_type)
        self.assertEqual(analysis.recommended_action, "Revisar mapeamento ou completar dados da linha.")

    def test_generic_hostname_is_not_strong_identity(self) -> None:
        analysis = analyze_identity({"hostname": "404 - not found"})
        self.assertEqual(analysis.primary_type, "source_external_key")
        self.assertFalse(analysis.hostname_valid)

    def test_source_external_key_is_preserved(self) -> None:
        normalized = normalize_asset_row({"Name": "192.168.3.44", "Scanserver": "scan-rj"}, {"Name": "hostname", "Scanserver": "source"})
        analysis = analyze_identity(normalized)
        self.assertIsNotNone(analysis.source_external_key)
        self.assertEqual(analysis.primary_type, "source_external_key")
