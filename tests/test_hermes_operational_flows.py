from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.domains.ai_chat.providers import AiProviderResponse  # noqa: E402
from app.domains.macros.ai_service import ItilMacroGenerationError, generate_itil_macro  # noqa: E402
from app.domains.macros.schemas import ItilMacroGenerateRequest  # noqa: E402
from app.services.import_ai_analysis import analyze_import  # noqa: E402


class FakeProvider:
    def __init__(self, content: str) -> None:
        self.content = content

    async def generate(self, messages, mode=None):  # noqa: ANN001, ANN201, ARG002
        return AiProviderResponse(content=self.content, provider="hermes", model="test")


class HermesOperationalFlowsTest(unittest.IsolatedAsyncioTestCase):
    async def test_macro_output_is_structured_and_missing_data_stays_explicit(self) -> None:
        content = json.dumps({
            "practice": "incident", "category": None, "subcategory": None, "service": None,
            "configuration_item": None, "impact": "unknown", "urgency": "unknown", "priority": "unknown",
            "title": "Falha de conectividade", "user_report": "Sem acesso à rede", "diagnosis": None,
            "actions_taken": [], "result": None, "current_status": "Em análise", "resolution": None,
            "next_action": "Coletar evidências", "closure_criteria": None,
            "missing_information": ["impacto", "urgência"], "warnings": [],
            "macro_text": "Usuário relata falha de conectividade. Impacto e urgência precisam ser confirmados."
        })
        result = await generate_itil_macro(ItilMacroGenerateRequest(summary="Sem acesso à rede"), FakeProvider(content))
        self.assertEqual(result.priority, "unknown")
        self.assertIn("impacto", result.missing_information)

    async def test_invalid_macro_output_is_rejected(self) -> None:
        with self.assertRaises(ItilMacroGenerationError):
            await generate_itil_macro(ItilMacroGenerateRequest(summary="Dados insuficientes"), FakeProvider("não é json"))

    async def test_import_ai_cannot_invent_identity_and_never_applies(self) -> None:
        response = json.dumps({"ai_suggestions": [{"row": 2, "field": "serial", "original_value": None, "proposed_value": "INVENTADO", "reason": "suposição", "method": "hermes", "confidence": .9, "requires_review": True}]})
        job = SimpleNamespace(total_rows=1, valid_rows=0, invalid_rows=0, report={"can_apply": False, "warnings": []})
        row = SimpleNamespace(row_number=2, raw_payload={"hostname": " pc-01 "}, normalized_payload={"hostname": "PC-01"}, decision="REVIEW_REQUIRED", issues=[])
        result = await analyze_import(job, [row], FakeProvider(response))
        self.assertEqual(result.ai_suggestions, [])
        self.assertFalse(result.safe_to_apply)
        self.assertEqual(result.file_summary.rows_need_review, 1)


if __name__ == "__main__":
    unittest.main()
