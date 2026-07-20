from __future__ import annotations

import json
import re

from app.core.config.settings import settings
from app.domains.ai_chat.providers import AiProvider, AiProviderMessage, HermesTerminalProvider
from app.domains.macros.schemas import ItilMacroGenerateRequest, ItilMacroOutput
from pydantic import ValidationError


class ItilMacroGenerationError(RuntimeError):
    pass


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
        return ItilMacroOutput.model_validate(_json_object(response.content))
    except ValidationError as exc:
        raise ItilMacroGenerationError("hermes_invalid_output") from exc
