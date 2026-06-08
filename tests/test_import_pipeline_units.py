from __future__ import annotations

import sys
import unittest
from types import SimpleNamespace

import pandas as pd

from tests.operational_http import ROOT

sys.path.insert(0, str(ROOT / "backend"))

from app.domains.imports.normalization.asset_normalizer import normalize_asset_row
from app.domains.imports.presets import detect_import_preset, effective_mapping, empty_columns, import_warnings
from app.domains.imports.service import ImportService
from app.domains.imports.validators.asset_validator import validate_normalized_asset, validate_raw_row_security
from app.shared.enums import ImportDecision

FIXTURES = ROOT / "tests" / "fixtures" / "imports"


class ImportPipelineUnitTest(unittest.TestCase):
    def test_column_aliases_and_normalization(self) -> None:
        row = normalize_asset_row(
            {
                "Nome do computador": " rjmimp001 ",
                "Service Tag": " sn-imp-001 ",
                "Número de patrimônio": " pat imp 001 ",
                "Marca": "HP Inc.",
                "Device Model": " elitebook 840 ",
                "E-mail do usuário": "colaborador.import@ens.edu.br",
                "IP": "10.20.30.11",
            }
        )
        self.assertEqual(row["hostname"], "RJMIMP001")
        self.assertEqual(row["serial"], "SN-IMP-001")
        self.assertEqual(row["patrimony"], "PAT-IMP-001")
        self.assertEqual(row["manufacturer"], "HP")
        self.assertEqual(row["user_email"], "colaborador.import@ens.edu.br")
        self.assertEqual(validate_normalized_asset(row), [])

    def test_formula_payload_is_blocked(self) -> None:
        issues = validate_raw_row_security({"Hostname": "=cmd", "Usuario": "*malicious"})
        self.assertGreaterEqual(len(issues), 2)
        self.assertEqual({issue["code"] for issue in issues}, {"suspicious_formula_payload"})

    def test_missing_identity_is_invalid(self) -> None:
        issues = validate_normalized_asset({"hostname": None, "serial": None, "patrimony": None, "asset_type": "NOTEBOOK"})
        self.assertIn("missing_identity", {issue["code"] for issue in issues})

    def test_lansweeper_preset_and_barcode_empty_warning(self) -> None:
        columns = ["Name", "Type", "Custom1", "Serialnumber", "State", "Scanserver", "Barcode"]
        rows = [{"Name": "RJMLSW001", "Custom1": "NOTEBOOK", "Type": "Windows", "Serialnumber": "SN-1", "State": "Active", "Scanserver": "ls", "Barcode": ""}]
        preset = detect_import_preset(columns)
        self.assertIsNotNone(preset)
        self.assertEqual(preset.version, "2026.06.ENS.1")
        mapping = effective_mapping(preset, {}, rows)
        self.assertNotIn("Barcode", mapping)
        self.assertIn("Barcode", empty_columns(rows, columns))
        self.assertIn("Coluna de patrimônio vazia", import_warnings(rows, mapping)[0])

    def test_lansweeper_normalization_custom1_state_metadata_and_confidence(self) -> None:
        mapping = {
            "Name": "hostname",
            "Custom1": "asset_type",
            "Type": "fallback_asset_type",
            "Manufacturer": "manufacturer",
            "Model": "model",
            "Serialnumber": "serial",
            "State": "source_state",
            "Building": "source_metadata.unit",
            "IP Location": "source_metadata.network_location",
            "lastuser": "source_metadata.imported_user_hint",
            "Scanserver": "source_metadata.source",
        }
        row = normalize_asset_row(
            {
                "Name": " rjmlsw001 ",
                "Custom1": "NOTEBOOK",
                "Type": "Windows",
                "Manufacturer": "66",
                "Model": "66",
                "Serialnumber": "SN-LSW-001",
                "State": "Active",
                "Building": "RJ",
                "IP Location": "Acad RJ",
                "lastuser": "ENS\\usuario",
                "Scanserver": "lansweeper",
            },
            mapping,
        )
        self.assertEqual(row["hostname"], "RJMLSW001")
        self.assertEqual(row["serial"], "SN-LSW-001")
        self.assertIsNone(row["manufacturer"])
        self.assertIsNone(row["model"])
        self.assertEqual(row["asset_type"], "NOTEBOOK")
        self.assertEqual(row["asset_family"], "COMPUTER")
        self.assertEqual(row["status"], "IN_USE")
        self.assertEqual(row["identity_confidence"], "HIGH")
        self.assertEqual(row["source_metadata"]["unit"], "RJ")
        self.assertEqual(row["source_metadata"]["imported_user_hint"], "ENS\\usuario")

    def test_type_fallback_invalid_serial_and_disposal_reason(self) -> None:
        row = normalize_asset_row(
            {
                "Name": "RJMLSW007",
                "Custom1": "Undefined",
                "Type": "Network device",
                "Serialnumber": "System Serial Number",
                "State": "Stolen",
            },
            {"Name": "hostname", "Custom1": "asset_type", "Type": "fallback_asset_type", "Serialnumber": "serial", "State": "source_state"},
        )
        self.assertIsNone(row["serial"])
        self.assertEqual(row["asset_type"], "OTHER")
        self.assertEqual(row["asset_family"], "NETWORK")
        self.assertEqual(row["identity_confidence"], "MEDIUM")
        self.assertEqual(row["status"], "DISCARDED")
        self.assertEqual(row["source_metadata"]["source_disposal_reason"], "stolen")

    def test_lansweeper_ip_address_never_becomes_hostname(self) -> None:
        columns = ["Name", "Type", "Custom1", "Serialnumber", "State", "Scanserver", "IP Address"]
        row = {
            "Name": "RJMLSW010",
            "Type": "Windows",
            "Custom1": "NOTEBOOK",
            "Serialnumber": "SN-LSW-010",
            "State": "Active",
            "Scanserver": "lansweeper",
            "IP Address": "10.0.33.14",
        }
        mapping = effective_mapping(detect_import_preset(columns), {}, [row])
        normalized = normalize_asset_row(row, mapping)
        self.assertEqual(normalized["hostname"], "RJMLSW010")
        self.assertEqual(normalized["ip_address"], "10.0.33.14")
        self.assertNotEqual(normalized["hostname"], normalized["ip_address"])

    def test_lansweeper_name_ip_becomes_reviewable_source_identity_not_hostname(self) -> None:
        service = ImportService(None)  # type: ignore[arg-type]
        row = normalize_asset_row(
            {
                "Name": "10.10.10.20",
                "IP Address": "",
                "Type": "Network device",
                "Custom1": "Undefined",
                "Scanserver": "scan-rj",
                "State": "Active",
            },
            {"Name": "hostname", "IP Address": "ip_address", "Type": "fallback_asset_type", "Custom1": "asset_type", "Scanserver": "source", "State": "source_state"},
        )
        self.assertIsNone(row["hostname"])
        self.assertEqual(row["ip_address"], "10.10.10.20")
        self.assertEqual(row["identity_confidence"], "NONE")
        self.assertTrue(str(row["source_external_key"]).startswith("lansweeper:"))
        self.assertEqual(validate_normalized_asset(row), [])
        decision, issues, _, merge_action = service._classify_row(
            {"Name": "10.10.10.20"},
            row,
            None,
            {},
            {},
            {},
            set(),
        )
        self.assertEqual(decision, ImportDecision.REVIEW_REQUIRED)
        self.assertEqual(merge_action, "REVIEW_IP_ONLY_SOURCE_KEY")
        self.assertEqual(issues[0]["code"], "weak_source_external_identity")

    def test_generic_hostname_tokens_are_not_strong_identity(self) -> None:
        row = normalize_asset_row(
            {"Name": "404 - not found", "Type": "Webserver", "Scanserver": "scan-rj"},
            {"Name": "hostname", "Type": "fallback_asset_type", "Scanserver": "source"},
        )
        self.assertIsNone(row["hostname"])
        self.assertTrue(str(row["source_external_key"]).startswith("lansweeper:"))

    def test_placeholder_66_is_null_globally_for_lansweeper_shape(self) -> None:
        row = normalize_asset_row(
            {"Name": "66", "Serialnumber": "66", "Barcode": "66", "Custom1": "66", "Type": "Monitor"},
            {"Name": "hostname", "Serialnumber": "serial", "Barcode": "patrimony", "Custom1": "asset_type", "Type": "fallback_asset_type"},
        )
        self.assertIsNone(row["hostname"])
        self.assertIsNone(row["serial"])
        self.assertIsNone(row["patrimony"])
        self.assertEqual(row["asset_type"], "MONITOR")

    def test_duplicate_equivalent_rows_are_skipped_and_latest_lastseen_is_canonical(self) -> None:
        service = ImportService(None)  # type: ignore[arg-type]
        older = normalize_asset_row(
            {"Name": "RJMLSW020", "Serialnumber": "SN-LSW-020", "Custom1": "NOTEBOOK", "State": "Active", "Lastseen": "2026-01-01"},
            {"Name": "hostname", "Serialnumber": "serial", "Custom1": "asset_type", "State": "source_state", "Lastseen": "last_login"},
        )
        newer = normalize_asset_row(
            {"Name": "RJMLSW020", "Serialnumber": "SN-LSW-020", "Custom1": "NOTEBOOK", "State": "Active", "Lastseen": "2026-06-01"},
            {"Name": "hostname", "Serialnumber": "serial", "Custom1": "asset_type", "State": "source_state", "Lastseen": "last_login"},
        )
        plan = service._build_internal_duplicate_plan([older, newer])
        self.assertEqual(plan[0]["decision"], ImportDecision.SKIPPED_DUPLICATE_IN_FILE)
        self.assertEqual(plan[0]["issue"]["canonical_row"], 3)

    def test_real_duplicate_conflict_is_blocking(self) -> None:
        service = ImportService(None)  # type: ignore[arg-type]
        first = normalize_asset_row({"Name": "RJMLSW030", "Serialnumber": "SN-LSW-030"}, {"Name": "hostname", "Serialnumber": "serial"})
        second = normalize_asset_row({"Name": "RJMLSW031", "Serialnumber": "SN-LSW-030"}, {"Name": "hostname", "Serialnumber": "serial"})
        plan = service._build_internal_duplicate_plan([first, second])
        self.assertEqual(plan[0]["decision"], ImportDecision.CONFLICT)
        self.assertEqual(plan[1]["decision"], ImportDecision.CONFLICT)

    def test_review_required_rows_do_not_block_partial_apply_report(self) -> None:
        service = ImportService(None)  # type: ignore[arg-type]
        job = SimpleNamespace(
            source="LANSWEEPER",
            filename="assets.xlsx",
            report={"import_mode": "INITIAL_LOAD"},
            status="READY_TO_APPLY",
            total_rows=2,
            valid_rows=1,
            invalid_rows=0,
            conflict_rows=0,
            skipped_rows=0,
        )
        rows = [
            SimpleNamespace(row_number=2, decision=ImportDecision.CREATE.value, row_status="STAGED", normalized_payload={"serial": "SN-1"}, identity_type="serial", identity_value="SN-1", identity_confidence="HIGH", merge_action="CREATE_ASSET", issues=[]),
            SimpleNamespace(row_number=3, decision=ImportDecision.REVIEW_REQUIRED.value, row_status="STAGED", normalized_payload={"source_external_key": "lansweeper:abc"}, identity_type="source_external_key", identity_value="lansweeper:abc", identity_confidence="NONE", merge_action="REVIEW", issues=[]),
        ]
        report = service._build_report(job, rows, {"created": 0, "updated": 0, "failed": 0}, was_applied=False)
        self.assertTrue(report["can_apply"])
        self.assertEqual(report["review_required_count"], 1)
        self.assertEqual(report["blocking_conflicts_count"], 0)

    def test_lansweeper_corrected_shape_fixture_classification(self) -> None:
        dataframe = pd.read_excel(FIXTURES / "lansweeper_corrected_shape.xlsx", sheet_name="report", dtype=str, keep_default_na=False)
        rows = dataframe.fillna("").to_dict(orient="records")
        columns = list(map(str, dataframe.columns))
        preset = detect_import_preset(columns)
        self.assertIsNotNone(preset)
        mapping = effective_mapping(preset, {}, rows)
        self.assertNotIn("Barcode", mapping)
        self.assertIn("Coluna de patrimônio vazia", import_warnings(rows, mapping)[0])

        normalized = [normalize_asset_row(row, mapping) for row in rows]
        service = ImportService(None)  # type: ignore[arg-type]
        duplicate_plan = service._build_internal_duplicate_plan(normalized)
        seen: set[tuple[str, str]] = set()
        decisions: list[tuple[str, list[dict[str, object]], dict[str, object]]] = []
        for index, (raw, row) in enumerate(zip(rows, normalized, strict=True)):
            decision, issues, _, _ = service._classify_row(raw, row, duplicate_plan.get(index), {}, {}, {}, seen)
            decisions.append((decision.value, issues, row))

        self.assertEqual(len(rows), 22)
        self.assertEqual(len(columns), 56)
        self.assertEqual(sum(1 for _, _, row in decisions if row.get("hostname") is None and row.get("ip_address") in {"192.168.3.43", "192.168.3.44"}), 2)
        self.assertEqual(sum(1 for decision, issues, _ in decisions if decision == ImportDecision.REVIEW_REQUIRED.value and issues and issues[0].get("code") == "weak_source_external_identity"), 2)
        self.assertEqual(sum(1 for decision, _, _ in decisions if decision == ImportDecision.CONFLICT.value), 14)
        self.assertEqual(sum(1 for decision, _, _ in decisions if decision == ImportDecision.SKIPPED_DUPLICATE_IN_FILE.value), 1)
        self.assertTrue(all(row.get("patrimony") is None for _, _, row in decisions))

        first = decisions[0][2]
        self.assertEqual(first["asset_type"], "NOTEBOOK")
        self.assertEqual(first["source_metadata"]["imported_user_hint"], "ENS\\usuario.teste")
        null_row = next(row for _, _, row in decisions if row.get("hostname") == "RJMCORNULL")
        self.assertIsNone(null_row["serial"])
        self.assertIsNone(null_row["manufacturer"])
        self.assertIsNone(null_row["model"])

        rjm21896_conflicts = [
            issue
            for decision, issues, _ in decisions
            if decision == ImportDecision.CONFLICT.value
            for issue in issues
            if issue.get("identity_value") == "RJM21896"
        ]
        self.assertEqual(len(rjm21896_conflicts), 6)
