from __future__ import annotations

import re

PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
MAX_TEMPLATE_CHARS = 10000
MAX_RENDERED_CHARS = 20000


class MacroRenderError(ValueError):
    def __init__(self, message: str, missing_fields: list[str] | None = None) -> None:
        super().__init__(message)
        self.missing_fields = missing_fields or []


def extract_placeholders(template_text: str) -> list[str]:
    fields = []
    seen = set()
    for match in PLACEHOLDER_RE.finditer(template_text):
        field = match.group(1).strip()
        if field and field not in seen:
            fields.append(field)
            seen.add(field)
    return fields


def render_macro(template_text: str, values: dict[str, object], required_fields: list[str] | None = None) -> tuple[str, list[str]]:
    if len(template_text) > MAX_TEMPLATE_CHARS:
        raise MacroRenderError("template_too_large")

    required = extract_placeholders(template_text) if required_fields is None else required_fields
    missing = [field for field in required if not str(values.get(field) or "").strip()]
    if missing:
        raise MacroRenderError("missing_required_fields", missing)

    pending: list[str] = []

    def replace(match: re.Match[str]) -> str:
        field = match.group(1).strip()
        value = values.get(field)
        if value is None or str(value).strip() == "":
            pending.append(field)
            return f"{{{field}}}"
        return str(value)

    rendered = PLACEHOLDER_RE.sub(replace, template_text)
    if len(rendered) > MAX_RENDERED_CHARS:
        raise MacroRenderError("rendered_text_too_large")
    return rendered, sorted(set(pending))
