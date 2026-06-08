from __future__ import annotations

import ipaddress
from typing import Any

from app.shared.enums import AssetStatus, AssetType


def validate_normalized_asset(row: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not any(row.get(key) for key in ("serial", "patrimony", "hostname", "source_external_key")):
        issues.append({"field": "identity", "code": "missing_identity", "message": "Linha sem serial, patrimonio, hostname ou chave externa de origem."})
    if row.get("asset_type") not in {item.value for item in AssetType}:
        issues.append({"field": "asset_type", "code": "invalid_asset_type", "message": "Tipo de ativo invalido."})
    if row.get("status") and row.get("status") not in {item.value for item in AssetStatus}:
        issues.append({"field": "status", "code": "invalid_asset_status", "message": "Status de ativo invalido."})
    for key in ("serial", "patrimony", "hostname"):
        value = row.get(key)
        if value and len(str(value)) > 160:
            issues.append({"field": key, "code": "value_too_long", "message": f"{key} excede o tamanho permitido."})
    if row.get("user_email") and "@" not in str(row["user_email"]):
        issues.append({"field": "user_email", "code": "invalid_email", "message": "E-mail do usuario invalido."})
    if row.get("ip_address"):
        try:
            ipaddress.ip_address(str(row["ip_address"]))
        except ValueError:
            issues.append({"field": "ip_address", "code": "invalid_ip_address", "message": "IP invalido."})
    return issues


def validate_raw_row_security(row: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for key, value in row.items():
        if value is None:
            continue
        text = str(value).lstrip()
        if text != "-" and text.startswith(("=", "+", "-", "@", "*")):
            issues.append(
                {
                    "field": str(key),
                    "code": "suspicious_formula_payload",
                    "message": "Valor com prefixo de formula bloqueado por seguranca.",
                }
            )
    return issues
