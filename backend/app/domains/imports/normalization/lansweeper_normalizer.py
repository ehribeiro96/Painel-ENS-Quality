from __future__ import annotations

from typing import Any

from app.domains.imports.classification.identity_classifier import identity_for as _identity_for
from app.domains.imports.normalization.asset_normalizer import normalize_asset_row as _normalize_asset_row
from app.domains.imports.normalization.asset_normalizer import normalize_column_name as _normalize_column_name


def normalize_column_name(column: Any) -> str:
    return _normalize_column_name(column)


def normalize_asset_row(raw: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
    return _normalize_asset_row(raw, mapping)


def identity_for(normalized: dict[str, Any]) -> tuple[str | None, str | None]:
    return _identity_for(normalized)


normalize_lansweeper_row = normalize_asset_row
