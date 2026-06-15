from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any

from app.shared.enums import AssetStatus, AssetType

GLOBAL_NULL_TOKENS = {"", "66", "undefined", "not scanned", "nan", "none", "null", "n/a", "na", "-"}
IPV4_PATTERN = re.compile(r"^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.|$)){4}$")
COLUMN_SPECIFIC_NULL_TOKENS = {
    "model": {"66"},
    "manufacturer": {"66"},
    "location": {"66"},
    "contact": {"66"},
    "asset_type": {"66"},
    "source_notes": {"66"},
}
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

COLUMN_ALIASES = {
    "hostname": "hostname",
    "name": "hostname",
    "host": "hostname",
    "computer": "hostname",
    "computer name": "hostname",
    "assetname": "hostname",
    "nome do computador": "hostname",
    "nome do ativo": "hostname",
    "serial": "serial",
    "serial number": "serial",
    "serial_number": "serial",
    "serialnumber": "serial",
    "service tag": "serial",
    "numero de serie": "serial",
    "número de série": "serial",
    "sn": "serial",
    "patrimonio": "patrimony",
    "patrimônio": "patrimony",
    "patrimony": "patrimony",
    "asset tag": "patrimony",
    "assettag": "patrimony",
    "barcode": "patrimony",
    "numero patrimonio": "patrimony",
    "numero de patrimonio": "patrimony",
    "número de patrimônio": "patrimony",
    "fabricante": "manufacturer",
    "manufacturer": "manufacturer",
    "marca": "manufacturer",
    "vendor": "manufacturer",
    "modelo": "model",
    "model": "model",
    "device model": "model",
    "tipo": "asset_type",
    "tipo de equipamento": "asset_type",
    "type": "asset_type",
    "custom1": "asset_type",
    "custom2": "source_notes",
    "fallback_asset_type": "fallback_asset_type",
    "usuário": "user",
    "usuario": "user",
    "user": "user",
    "last user": "user",
    "lastuser": "user",
    "last logged on user": "user",
    "colaborador": "user",
    "email": "user_email",
    "e-mail": "user_email",
    "email do usuario": "user_email",
    "e-mail do usuario": "user_email",
    "localização": "location",
    "localizacao": "location",
    "location": "location",
    "building": "unit",
    "so": "operating_system",
    "os": "operating_system",
    "sistema operacional": "operating_system",
    "operating system": "operating_system",
    "ip": "ip_address",
    "ip address": "ip_address",
    "ip location": "network_location",
    "último login": "last_login",
    "ultimo login": "last_login",
    "last login": "last_login",
    "lastseen": "last_login",
    "last seen": "last_login",
    "status": "status",
    "state": "source_state",
    "firstseen": "first_seen",
    "lasttried": "last_tried",
    "fqdn": "fqdn",
    "dns name": "dns_name",
    "scanserver": "source",
    "observacoes": "notes",
    "observações": "notes",
    "notes": "notes",
}

MANUFACTURER_ALIASES = {
    "HEWLETT PACKARD": "HP",
    "HEWLETT-PACKARD": "HP",
    "HP INC": "HP",
    "HP INC.": "HP",
    "DELL INC": "DELL",
    "DELL INC.": "DELL",
    "LENOVO GROUP LIMITED": "LENOVO",
    "LENOVO PC HK LIMITED": "LENOVO",
}

ASSET_TYPE_ALIASES = {
    "LAPTOP": AssetType.NOTEBOOK.value,
    "NOTEBOOK": AssetType.NOTEBOOK.value,
    "DESKTOP": AssetType.DESKTOP.value,
    "PC": AssetType.DESKTOP.value,
    "MONITOR": AssetType.MONITOR.value,
    "DOCK": AssetType.DOCK.value,
    "DOCKING": AssetType.DOCK.value,
    "PHONE": AssetType.MOBILE.value,
    "MOBILE": AssetType.MOBILE.value,
    "CELULAR": AssetType.MOBILE.value,
    "PRINTER": AssetType.PRINTER.value,
    "IMPRESSORA": AssetType.PRINTER.value,
    "HEADSET": AssetType.PERIPHERAL.value,
    "WEBCAM": AssetType.PERIPHERAL.value,
    "PERIPHERAL": AssetType.PERIPHERAL.value,
    "PERIFERICO": AssetType.PERIPHERAL.value,
    "PERIFÉRICO": AssetType.PERIPHERAL.value,
    "KITWIRELESS": AssetType.PERIPHERAL.value,
    "ADAPTADOR": AssetType.PERIPHERAL.value,
    "CHIP": AssetType.MOBILE.value,
    "SERVIDOR": AssetType.OTHER.value,
    "SERVER": AssetType.OTHER.value,
    "NETWORK DEVICE": AssetType.OTHER.value,
}

ASSET_FAMILY_ALIASES = {
    "NOTEBOOK": "COMPUTER",
    "LAPTOP": "COMPUTER",
    "DESKTOP": "COMPUTER",
    "PC": "COMPUTER",
    "SERVIDOR": "SERVER",
    "SERVER": "SERVER",
    "MONITOR": "MONITOR",
    "HEADSET": "PERIPHERAL",
    "WEBCAM": "PERIPHERAL",
    "PRINTER": "PERIPHERAL",
    "IMPRESSORA": "PERIPHERAL",
    "KITWIRELESS": "ACCESSORY",
    "ADAPTADOR": "ACCESSORY",
    "CELULAR": "MOBILE",
    "MOBILE": "MOBILE",
    "PHONE": "MOBILE",
    "CHIP": "MOBILE",
    "NETWORK DEVICE": "NETWORK",
    "ROUTER": "NETWORK",
    "SWITCH": "NETWORK",
}

STATE_STATUS_ALIASES = {
    "ACTIVE": AssetStatus.IN_USE.value,
    "STOCK": AssetStatus.STOCK.value,
    "BROKEN": AssetStatus.DEFECTIVE.value,
    "SOLD": AssetStatus.DISCARDED.value,
    "DONATE": AssetStatus.DISCARDED.value,
    "STOLEN": AssetStatus.DISCARDED.value,
    "NON-ACTIVE": AssetStatus.CONFIG_PENDING.value,
}


def normalize_text(value: Any, *, uppercase: bool = True, field: str | None = None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in GLOBAL_NULL_TOKENS:
        return None
    if field and text in COLUMN_SPECIFIC_NULL_TOKENS.get(field, set()):
        return None
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text.upper() if uppercase else text


def normalize_identifier(value: Any, *, field: str | None = None) -> str | None:
    text = normalize_text(value, field=field)
    if text is None:
        return None
    normalized = re.sub(r"[\s_]+", "-", text)
    if field == "serial" and normalized in INVALID_SERIALS:
        return None
    if field == "hostname" and normalized in GENERIC_HOSTNAME_TOKENS:
        return None
    return normalized


def looks_like_ip_address(value: str | None) -> bool:
    return bool(value and IPV4_PATTERN.match(value.strip()))


def normalize_column_name(column: Any) -> str:
    text = normalize_text(column, uppercase=False) or ""
    key = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    key = key.lower().strip().replace("_", " ")
    key = re.sub(r"\s+", " ", key)
    return COLUMN_ALIASES.get(key, key.replace(" ", "_"))


def normalize_manufacturer(value: Any) -> str | None:
    text = normalize_text(value, field="manufacturer")
    if text is None:
        return None
    text = text.rstrip(".")
    return MANUFACTURER_ALIASES.get(text, text)


def normalize_asset_type(value: Any, fallback: Any = None) -> str:
    text = normalize_text(value, field="asset_type")
    if text and text in ASSET_TYPE_ALIASES:
        return ASSET_TYPE_ALIASES[text]
    fallback_text = normalize_text(fallback, field="asset_type")
    if fallback_text and fallback_text in ASSET_TYPE_ALIASES:
        return ASSET_TYPE_ALIASES[fallback_text]
    if text is None and fallback_text is None:
        return AssetType.OTHER.value
    return AssetType.OTHER.value


def normalize_asset_family(value: Any, fallback: Any = None) -> str:
    text = normalize_text(value, field="asset_type")
    if text and text in ASSET_FAMILY_ALIASES:
        return ASSET_FAMILY_ALIASES[text]
    fallback_text = normalize_text(fallback, field="asset_type")
    if fallback_text and fallback_text in ASSET_FAMILY_ALIASES:
        return ASSET_FAMILY_ALIASES[fallback_text]
    if text is None and fallback_text is None:
        return "OTHER"
    return "OTHER"


def normalize_status(source_state: Any, asset_type: str, identity_confidence: str) -> tuple[str | None, str | None]:
    state = normalize_text(source_state)
    if state is None:
        return None, None
    disposal_reason = None
    if state in {"SOLD", "DONATE", "STOLEN"}:
        disposal_reason = {"SOLD": "sold", "DONATE": "donated", "STOLEN": "stolen"}[state]
    if state == "ACTIVE" and (asset_type not in {AssetType.NOTEBOOK.value, AssetType.DESKTOP.value} or identity_confidence not in {"HIGH", "MEDIUM"}):
        return AssetStatus.CONFIG_PENDING.value, disposal_reason
    return STATE_STATUS_ALIASES.get(state), disposal_reason


def identity_confidence_for(serial: str | None, patrimony: str | None, hostname: str | None, asset_family: str) -> str:
    if serial or patrimony:
        return "HIGH"
    if hostname and asset_family in {"PERIPHERAL", "ACCESSORY"}:
        return "LOW"
    if hostname:
        return "MEDIUM"
    return "NONE"


def _source_external_key(source: Any, name: Any, ip_address: str | None, asset_type: str, raw: dict[str, Any]) -> str | None:
    source_text = normalize_text(source, uppercase=False) or "lansweeper"
    name_text = normalize_text(name, uppercase=False)
    if not ip_address and not name_text:
        return None
    material = "|".join(
        [
            "lansweeper",
            source_text,
            name_text or "",
            ip_address or "",
            asset_type,
            normalize_text(raw.get("MAC Address"), uppercase=False) or "",
        ]
    )
    return f"lansweeper:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


def normalize_asset_row(raw: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
    normalized_columns: dict[str, Any] = {}
    source_metadata: dict[str, Any] = {}
    for key, value in raw.items():
        mapped = (mapping or {}).get(str(key))
        normalized_key = mapped or normalize_column_name(key)
        if normalized_key.startswith("source_metadata."):
            source_metadata[normalized_key.split(".", 1)[1]] = value
        else:
            normalized_columns[normalized_key] = value
    source_state = normalized_columns.get("source_state") or normalized_columns.get("status")
    asset_type = normalize_asset_type(normalized_columns.get("asset_type"), normalized_columns.get("fallback_asset_type"))
    asset_family = normalize_asset_family(normalized_columns.get("asset_type"), normalized_columns.get("fallback_asset_type"))
    serial = normalize_identifier(normalized_columns.get("serial"), field="serial")
    patrimony = normalize_identifier(normalized_columns.get("patrimony"), field="patrimony")
    hostname = normalize_identifier(normalized_columns.get("hostname"), field="hostname")
    ip_address = normalize_text(normalized_columns.get("ip_address"), uppercase=False)
    if looks_like_ip_address(hostname):
        ip_address = ip_address or hostname
        hostname = None
    source_external_key = _source_external_key(
        normalized_columns.get("source") or source_metadata.get("source"),
        normalized_columns.get("hostname"),
        ip_address,
        asset_type,
        raw,
    )
    identity_confidence = identity_confidence_for(serial, patrimony, hostname, asset_family)
    status, disposal_reason = normalize_status(source_state, asset_type, identity_confidence)
    if source_state is not None:
        source_metadata["source_state"] = normalize_text(source_state)
    if disposal_reason:
        source_metadata["source_disposal_reason"] = disposal_reason
    metadata_fields = {
        "unit": ("unit", True),
        "network_location": ("network_location", True),
        "imported_user_hint": ("imported_user_hint", False),
        "first_seen": ("first_seen", False),
        "last_seen": ("last_seen", False),
        "last_tried": ("last_tried", False),
        "fqdn": ("fqdn", False),
        "dns_name": ("dns_name", False),
        "source_notes": ("source_notes", False),
        "source": ("source", False),
    }
    for target, (field, uppercase) in metadata_fields.items():
        value = source_metadata.get(target) if target in source_metadata else normalized_columns.get(field)
        normalized_value = normalize_text(value, uppercase=uppercase, field=field)
        if normalized_value is not None:
            source_metadata[target] = normalized_value
    last_login = normalize_text(normalized_columns.get("last_login"), uppercase=False)
    if last_login is not None:
        source_metadata.setdefault("last_seen", last_login)
    source_metadata["name_role"] = "hostname" if asset_family in {"COMPUTER", "SERVER"} else "asset_name"
    if source_external_key:
        source_metadata["source_external_key"] = source_external_key
    return {
        "hostname": hostname,
        "serial": serial,
        "patrimony": patrimony,
        "manufacturer": normalize_manufacturer(normalized_columns.get("manufacturer")),
        "brand": normalize_manufacturer(normalized_columns.get("manufacturer")),
        "model": normalize_text(normalized_columns.get("model"), field="model"),
        "asset_type": asset_type,
        "fallback_asset_type": normalize_text(normalized_columns.get("fallback_asset_type"), field="asset_type"),
        "asset_family": asset_family,
        "identity_confidence": identity_confidence,
        "source_external_key": source_external_key,
        "user": normalize_text(normalized_columns.get("user"), uppercase=False),
        "user_email": normalize_text(normalized_columns.get("user_email"), uppercase=False),
        "location": normalize_text(normalized_columns.get("location"), field="location"),
        "operating_system": normalize_text(normalized_columns.get("operating_system"), uppercase=False),
        "ip_address": ip_address,
        "last_login": last_login,
        "status": status,
        "notes": normalize_text(normalized_columns.get("notes"), uppercase=False),
        "source_metadata": source_metadata,
    }
