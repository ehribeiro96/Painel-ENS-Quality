from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.domains.imports.parsing import read_spreadsheet_file  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "imports"


class SpreadsheetReaderTest(unittest.TestCase):
    def test_csv_valid_is_loaded_without_sheet_name(self) -> None:
        content = (FIXTURES / "lansweeper_valid.csv").read_bytes()

        dataframe, sheet_name = read_spreadsheet_file("lansweeper_valid.csv", content)

        self.assertIsNone(sheet_name)
        self.assertGreater(len(dataframe.index), 0)
        self.assertGreater(len(dataframe.columns), 0)

    def test_xlsx_with_report_sheet_uses_report_sheet(self) -> None:
        content = (FIXTURES / "lansweeper_corrected_shape.xlsx").read_bytes()

        dataframe, sheet_name = read_spreadsheet_file("lansweeper_corrected_shape.xlsx", content)

        self.assertEqual("report", sheet_name)
        self.assertGreater(len(dataframe.index), 0)
        self.assertIn("Name", dataframe.columns)

    def test_missing_report_sheet_can_be_rejected_in_strict_mode(self) -> None:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Inventario"
        worksheet.append(["Name", "Serialnumber"])
        worksheet.append(["RJMTEST001", "SN-001"])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "inventory.xlsx"
            workbook.save(temp_path)
            content = temp_path.read_bytes()

        with self.assertRaises(ValueError) as ctx:
            read_spreadsheet_file("inventory.xlsx", content, require_report_sheet=True)

        self.assertEqual("missing_report_sheet", str(ctx.exception))

    def test_empty_file_is_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            read_spreadsheet_file("empty.csv", b"")

        self.assertEqual("empty_import_file", str(ctx.exception))

    def test_invalid_extension_is_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            read_spreadsheet_file("inventory.txt", b"ignored")

        self.assertEqual("unsupported_import_file", str(ctx.exception))
