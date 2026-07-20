from __future__ import annotations

import json
import re

from app.core.config.settings import settings
from app.domains.ai_chat.providers import AiProvider, AiProviderMessage, HermesTerminalProvider
from app.domains.macros.schemas import ItilMacroGenerateRequest, ItilMacroOutput
from pydantic import ValidationError


class ItilMacroGenerationError(RuntimeError):
    pass


ITIL_PRIORITY_MATRIX = {
    ("high", "high"): "P1",
    ("high", "medium"): "P2",
    ("high", "low"): "P3",
    ("medium", "high"): "P2",
    ("medium", "medium"): "P3",
    ("medium", "low"): "P4",
    ("low", "high"): "P3",
    ("low", "medium"): "P4",
    ("low", "low"): "P4",
}


def calculate_itil_priority(impact: str, urgency: str) -> str:
    if "unknown" in (impact, urgency):
        return "unknown"
    return ITIL_PRIORITY_MATRIX[(impact, urgency)]


def _json_object(content: str) -> dict[str, object]:
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", content.strip(), flags=re.IGNORECASE)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ItilMacroGenerationError("hermes_invalid_json") from exc
    if not isinstance(value, dict):
        raise ItilMacroGenerationError("hermes_invalid_output")
    return value


async def generate_itil_macro(payload: ItilMacroGenerateRequest, provider: AiProvider | None = None) -> ItilMacroOutput:
    prompt = (
        "Gere uma macro operacional ITIL em português brasileiro. Responda SOMENTE com JSON válido, sem markdown, "
        "seguindo exatamente os campos do contrato. Não invente fatos, prioridade, indisponibilidade, identificadores "
        "ou ações. Use null/unknown e missing_information quando faltar dado. Prioridade só pode ser derivada quando "
        "impacto e urgência estiverem explícitos.\n\n"
        f"Contrato: {json.dumps(ItilMacroOutput.model_json_schema(), ensure_ascii=False)}\n\n"
        f"Dados informados: {payload.model_dump_json(exclude_none=True)}"
    )
    response = await (provider or HermesTerminalProvider(settings)).generate(
        [
            AiProviderMessage(role="system", content="Você estrutura registros ITIL auditáveis sem criar fatos."),
            AiProviderMessage(role="user", content=prompt),
        ]
    )
    try:
        output = ItilMacroOutput.model_validate(_json_object(response.content))
        expected_priority = calculate_itil_priority(output.impact, output.urgency)
        if output.priority != expected_priority:
            output = output.model_copy(
                update={
                    "priority": expected_priority,
                    "warnings": [*output.warnings, "Prioridade do provider normalizada pela matriz ITIL determinística."],
                }
            )
        return output
    except ValidationError as exc:
        raise ItilMacroGenerationError("hermes_invalid_output") from exc
