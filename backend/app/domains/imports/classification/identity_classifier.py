from __future__ import annotations

import hashlib
import ipaddress
import re
import unicodedata
from dataclasses import dataclass
from typing import Any

INVALID_SERIALS = {
    "UNDEFINED",
    "NOT-SCANNED",
    "TO-BE-FILLED-BY-O.E.M.",
    "SYSTEM-SERIAL-NUMBER",
    "DEFAULT-STRING",
    "00000000",
    "123456789",
    "N/A",
    "NONE",
    "NULL",
}

GENERIC_HOSTNAME_TOKENS = {
    "LOGIN",
    "LOG-IN",
    "LOGON",
    "404---NOT-FOUND",
    "MSG-LOGIN-PAGE-TITLE",
}


@dataclass(frozen=True)
class IdentityAnalysis:
    primary_type: str | None
    primary_value: str | None
    secondary_type: str | None
    secondary_value: str | None
    confidence: str
    hostname_valid: bool
    serial_valid: bool
    patrimony_valid: bool
    ip_only: bool
    source_external_key: str | None
    reason: str
    recommended_action: str


def _normalize_text(value: Any, *, uppercase: bool = True) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"undefined", "not scanned", "nan", "none", "null", "n/a", "na", "-"}:
        return None
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.upper() if uppercase else text


def _normalize_identifier(value: Any, *, field: str | None = None) -> str | None:
    text = _normalize_text(value)
    if text is None:
        return None
    normalized = re.sub(r"[\s_]+", "-", text)
    if field == "serial" and normalized in INVALID_SERIALS:
        return None
    if field == "hostname" and normalized in GENERIC_HOSTNAME_TOKENS:
        return None
    return normalized


def _looks_like_ip_address(value: str | None) -> bool:
    if not value:
        return False
    try:
        ipaddress.ip_address(value.strip())
    except ValueError:
        return False
    return True


def _source_external_key(normalized: dict[str, Any]) -> str | None:
    source = _normalize_text(normalized.get("source"), uppercase=False) or "lansweeper"
    name = _normalize_text(normalized.get("hostname"), uppercase=False)
    ip_address = _normalize_text(normalized.get("ip_address"), uppercase=False)
    if not ip_address and not name:
        return None
    material = "|".join(
        [
            "lansweeper",
            source,
            name or "",
            ip_address or "",
            str(normalized.get("asset_type") or ""),
            _normalize_text((normalized.get("source_metadata") or {}).get("mac_address"), uppercase=False) or "",
        ]
    )
    return f"lansweeper:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


def _confidence(serial: str | None, patrimony: str | None, hostname: str | None, asset_family: str | None) -> str:
    if serial or patrimony:
        return "HIGH"
    if hostname and asset_family in {"PERIPHERAL", "ACCESSORY"}:
        return "LOW"
    if hostname:
        return "MEDIUM"
    return "NONE"


def is_valid_serial(value: Any) -> bool:
    return _normalize_identifier(value, field="serial") is not None


def is_valid_patrimony(value: Any) -> bool:
    return _normalize_identifier(value, field="patrimony") is not None


def is_valid_hostname(value: Any) -> bool:
    normalized = _normalize_identifier(value, field="hostname")
    return normalized is not None and not _looks_like_ip_address(normalized)


def is_ip_only(normalized: dict[str, Any]) -> bool:
    return bool(normalized.get("ip_address") and not any(normalized.get(key) for key in ("serial", "patrimony", "hostname")))


def analyze_identity(normalized: dict[str, Any]) -> IdentityAnalysis:
    serial = _normalize_identifier(normalized.get("serial"), field="serial")
    patrimony = _normalize_identifier(normalized.get("patrimony"), field="patrimony")
    hostname = _normalize_identifier(normalized.get("hostname"), field="hostname")
    if hostname and _looks_like_ip_address(hostname):
        hostname = None
    ip_address = _normalize_text(normalized.get("ip_address"), uppercase=False)
    asset_family = _normalize_text(normalized.get("asset_family"))
    source_external_key = normalized.get("source_external_key") or _source_external_key(normalized)
    primary_type: str | None = None
    primary_value: str | None = None
    if serial:
        primary_type, primary_value = "serial", serial
    elif patrimony:
        primary_type, primary_value = "patrimony", patrimony
    elif hostname:
        primary_type, primary_value = "hostname", hostname
    elif source_external_key:
        primary_type, primary_value = "source_external_key", str(source_external_key)
    secondary_type: str | None = None
    secondary_value: str | None = None
    if primary_type != "serial" and serial:
        secondary_type, secondary_value = "serial", serial
    elif primary_type != "patrimony" and patrimony:
        secondary_type, secondary_value = "patrimony", patrimony
    elif primary_type != "hostname" and hostname:
        secondary_type, secondary_value = "hostname", hostname
    confidence = _confidence(serial, patrimony, hostname, asset_family)
    ip_only = is_ip_only({"ip_address": ip_address, "serial": serial, "patrimony": patrimony, "hostname": hostname})
    if ip_only:
        reason = "Linha sem identidade patrimonial forte; IP/name de origem preservado como chave externa para revisao."
        recommended_action = "Revisar antes de aplicar ou completar serial/patrimonio/hostname."
    elif primary_type in {"serial", "patrimony"}:
        reason = "Identidade patrimonial forte identificada."
        recommended_action = "Prosseguir com a classificação normal."
    elif primary_type == "hostname":
        reason = "Hostname válido identificado."
        recommended_action = "Verificar conflitos com ativos existentes."
    elif primary_type == "source_external_key":
        reason = "Identidade externa preservada como chave de origem."
        recommended_action = "Revisar antes de aplicar."
    else:
        reason = "Linha sem identidade aproveitável."
        recommended_action = "Revisar mapeamento ou completar dados da linha."
    return IdentityAnalysis(
        primary_type=primary_type,
        primary_value=primary_value,
        secondary_type=secondary_type,
        secondary_value=secondary_value,
        confidence=confidence,
        hostname_valid=hostname is not None and not _looks_like_ip_address(hostname),
        serial_valid=serial is not None,
        patrimony_valid=patrimony is not None,
        ip_only=ip_only,
        source_external_key=str(source_external_key) if source_external_key else None,
        reason=reason,
        recommended_action=recommended_action,
    )


def identity_for(normalized: dict[str, Any]) -> tuple[str | None, str | None]:
    analysis = analyze_identity(normalized)
    return analysis.primary_type, analysis.primary_value
