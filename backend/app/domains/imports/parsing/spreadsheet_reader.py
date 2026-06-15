from __future__ import annotations

import io

import pandas as pd


def _validate_extension(filename: str) -> str:
    suffix = filename.lower()
    if suffix.endswith(".csv"):
        return "csv"
    if suffix.endswith(".xlsx"):
        return "xlsx"
    raise ValueError("unsupported_import_file")


def read_spreadsheet_file(filename: str, content: bytes, *, require_report_sheet: bool = False) -> tuple[pd.DataFrame, str | None]:
    if not content:
        raise ValueError("empty_import_file")

    file_type = _validate_extension(filename)
    if file_type == "csv":
        return pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, encoding="utf-8-sig"), None

    workbook = pd.ExcelFile(io.BytesIO(content))
    if not workbook.sheet_names:
        raise ValueError("empty_import_file")

    if "report" in workbook.sheet_names:
        sheet_name = "report"
    elif require_report_sheet:
        raise ValueError("missing_report_sheet")
    else:
        sheet_name = workbook.sheet_names[0]

    return pd.read_excel(workbook, sheet_name=sheet_name, dtype=str, keep_default_na=False), sheet_name
