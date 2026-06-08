from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

LANSWEEPER_ASSETS_EXPORT_NAME = "Lansweeper Assets Export"
LANSWEEPER_ASSETS_EXPORT_VERSION = "2026.06.ENS.1"


@dataclass(frozen=True)
class ImportPreset:
    name: str
    version: str
    mapping: dict[str, str]
    expected_columns: tuple[str, ...]
    required_detection_columns: frozenset[str]


LANSWEEPER_ASSETS_EXPORT = ImportPreset(
    name=LANSWEEPER_ASSETS_EXPORT_NAME,
    version=LANSWEEPER_ASSETS_EXPORT_VERSION,
    mapping={
        "Name": "hostname",
        "Custom1": "asset_type",
        "Type": "fallback_asset_type",
        "Manufacturer": "manufacturer",
        "Model": "model",
        "Serialnumber": "serial",
        "State": "source_state",
        "Location": "location",
        "Building": "source_metadata.unit",
        "IP Location": "source_metadata.network_location",
        "IP Address": "ip_address",
        "OS": "operating_system",
        "lastuser": "source_metadata.imported_user_hint",
        "Firstseen": "source_metadata.first_seen",
        "Lastseen": "last_login",
        "LastTried": "source_metadata.last_tried",
        "FQDN": "source_metadata.fqdn",
        "DNS Name": "source_metadata.dns_name",
        "Custom2": "source_metadata.source_notes",
        "Scanserver": "source_metadata.source",
    },
    expected_columns=(
        "Name",
        "Type",
        "Custom1",
        "Serialnumber",
        "State",
        "Location",
        "Building",
        "IP Address",
        "IP Location",
        "OS",
        "lastuser",
        "Firstseen",
        "Lastseen",
        "LastTried",
        "FQDN",
        "DNS Name",
        "Custom2",
        "Scanserver",
    ),
    required_detection_columns=frozenset({"Name", "Type", "Custom1", "Serialnumber", "State", "Scanserver"}),
)


def detect_import_preset(columns: Iterable[Any]) -> ImportPreset | None:
    column_set = {str(column) for column in columns}
    if LANSWEEPER_ASSETS_EXPORT.required_detection_columns.issubset(column_set):
        return LANSWEEPER_ASSETS_EXPORT
    return None


def schema_signature(columns: Iterable[Any]) -> str:
    normalized = "\n".join(str(column) for column in columns)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def useful_value(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text.lower() not in {"nan", "none", "null", "undefined", "not scanned", "n/a", "na", "-"}


def empty_columns(raw_rows: list[dict[str, Any]], columns: Iterable[Any]) -> list[str]:
    empty: list[str] = []
    for column in columns:
        key = str(column)
        if not any(useful_value(row.get(key)) for row in raw_rows):
            empty.append(key)
    return empty


def effective_mapping(preset: ImportPreset | None, detected_mapping: dict[str, str], raw_rows: list[dict[str, Any]]) -> dict[str, str]:
    mapping = dict(preset.mapping if preset else detected_mapping)
    if "Barcode" in mapping and not any(useful_value(row.get("Barcode")) for row in raw_rows):
        mapping.pop("Barcode", None)
    elif preset and any(useful_value(row.get("Barcode")) for row in raw_rows):
        mapping["Barcode"] = "patrimony"
    return mapping


def import_warnings(raw_rows: list[dict[str, Any]], mapping: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    if raw_rows and "Barcode" not in mapping and all(not useful_value(row.get("Barcode")) for row in raw_rows):
        warnings.append("Coluna de patrimônio vazia nesta planilha. Os ativos serão identificados por serial e hostname.")
    return warnings


def distribution(raw_rows: list[dict[str, Any]], column: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in raw_rows:
        value = row.get(column)
        if useful_value(value):
            counter[str(value).strip()] += 1
    return dict(counter)
