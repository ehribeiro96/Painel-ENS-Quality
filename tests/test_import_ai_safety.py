from __future__ import annotations

import asyncio
import json
import unittest
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.api.v1.dependencies.auth import require_role
from app.core.permissions.ai import has_ai_capability
from app.domains.ai_chat.providers import AiProviderResponse
from app.domains.imports.schemas import ImportAiAnalysis, ImportCorrection, ImportFileSummary
from app.services.import_ai_analysis import (
    IDENTITY_FIELDS,
    ImportAiAnalysisError,
    analyze_import,
    decide_ai_suggestion,
    list_ai_suggestions,
    persist_ai_suggestions,
)
from app.shared.enums import AiCapability, AuditAction, Role
from fastapi import HTTPException


class _Provider:
    def __init__(self, suggestions: list[dict[str, object]]) -> None:
        self.suggestions = suggestions

    async def generate(self, messages, mode=None):  # noqa: ANN001, ANN201, ARG002
        return AiProviderResponse(
            content=json.dumps({"ai_suggestions": self.suggestions}),
            provider="hermes",
            model="test",
        )


class _SlowProvider:
    async def generate(self, messages, mode=None):  # noqa: ANN001, ANN201, ARG002
        await asyncio.sleep(1)


class _Session:
    def __init__(self, rows: list[Any] | None = None, job: Any | None = None) -> None:
        self.added: list[Any] = []
        self.rows = rows or []
        self.job = job

    def add(self, value: object) -> None:
        self.added.append(value)

    async def flush(self) -> None:
        return None

    async def scalar(self, statement):  # noqa: ANN001, ANN201
        if "FROM import_jobs" in str(statement):
            return self.job
        return self.rows[0] if self.rows else None

    async def execute(self, statement):  # noqa: ANN001, ANN201
        if "FROM assets" in str(statement):
            return SimpleNamespace(scalars=lambda: [])
        return SimpleNamespace(scalars=lambda: self.rows)


def _review_job(report: dict[str, object]) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(), source="SPREADSHEET", filename="synthetic.csv", status="REVIEW_REQUIRED",
        total_rows=1, valid_rows=0, invalid_rows=0, created_rows=0, updated_rows=0,
        skipped_rows=0, conflict_rows=0, failed_rows=0, updated_by=None, report=report,
    )


def _review_staging(job: SimpleNamespace, hostname: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(), job_id=job.id, row_number=1, raw_payload={"hostname": hostname},
        normalized_payload={"hostname": hostname, "asset_type": "DESKTOP", "identity_confidence": "MEDIUM"},
        identity_type="hostname", identity_value=hostname, issues=[{"field": "hostname"}],
        decision="REVIEW_REQUIRED", row_status="STAGED", matched_asset_id=None, merge_action="REVIEW",
        updated_by=None, deleted_at=None, identity_confidence="MEDIUM",
    )


class ImportAiSafetyTest(unittest.IsolatedAsyncioTestCase):
    async def test_viewer_cannot_analyze_or_decide_ai_suggestions(self) -> None:
        self.assertFalse(has_ai_capability(Role.VIEWER, AiCapability.AI_IMPORT_ANALYSIS))
        role_guard = require_role(Role.ADMIN, Role.TECHNICIAN)

        with self.assertRaises(HTTPException) as raised:
            await role_guard(SimpleNamespace(role=Role.VIEWER))

        self.assertEqual(403, raised.exception.status_code)

    async def test_positive_hermes_suggestion_is_normalized_for_human_review(self) -> None:
        suggestion = {
            "row": 1,
            "field": "hostname",
            "original_value": "model-controlled-value",
            "proposed_value": "srv-financeiro",
            "reason": "Padronização semântica",
            "method": "normalização semântica de hostname",
            "confidence": 0.98,
            "requires_review": False,
        }
        job = SimpleNamespace(total_rows=1, valid_rows=0, invalid_rows=0, report={"can_apply": False, "warnings": []})
        row = SimpleNamespace(
            row_number=1,
            raw_payload={"hostname": "srv financeiro", "serial": "ENS-CONTROLLED-001"},
            normalized_payload={"hostname": "srv financeiro", "serial": "ENS-CONTROLLED-001"},
            decision="REVIEW_REQUIRED",
            issues=[],
        )

        result = await analyze_import(job, [row], _Provider([suggestion]))

        self.assertEqual(1, len(result.ai_suggestions))
        accepted = result.ai_suggestions[0]
        self.assertEqual("hermes", accepted.method)
        self.assertTrue(accepted.requires_review)
        self.assertEqual("srv financeiro", accepted.original_value)
        self.assertEqual("ENS-CONTROLLED-001", row.normalized_payload["serial"])
        self.assertFalse(result.safe_to_apply)

    async def test_backend_timeout_is_controlled_and_does_not_apply(self) -> None:
        job = SimpleNamespace(total_rows=1, valid_rows=0, invalid_rows=0, report={"can_apply": False, "warnings": []})
        row = SimpleNamespace(row_number=1, raw_payload={"hostname": "pc"}, normalized_payload={"hostname": "pc"}, decision="REVIEW_REQUIRED", issues=[])

        with self.assertRaisesRegex(ImportAiAnalysisError, "hermes_timeout"):
            await analyze_import(job, [row], _SlowProvider(), timeout_seconds=0.01)

    async def test_ai_cannot_forge_missing_critical_source_values(self) -> None:
        suggestions = [
            {
                "row": 1,
                "field": field,
                "original_value": "forged-source",
                "proposed_value": "invented-value",
                "reason": "guess",
                "method": "hermes",
                "confidence": 0.99,
                "requires_review": True,
            }
            for field in sorted(IDENTITY_FIELDS)
        ]
        job = SimpleNamespace(total_rows=1, valid_rows=0, invalid_rows=0, report={"can_apply": False, "warnings": []})
        row = SimpleNamespace(
            row_number=1,
            raw_payload={},
            normalized_payload={},
            decision="REVIEW_REQUIRED",
            issues=[],
        )

        result = await analyze_import(job, [row], _Provider(suggestions))

        self.assertEqual([], result.ai_suggestions)
        self.assertFalse(result.safe_to_apply)

    async def test_ai_suggestion_is_forced_to_human_review(self) -> None:
        suggestion = {
            "row": 1,
            "field": "hostname",
            "original_value": "pc-01",
            "proposed_value": "PC-01",
            "reason": "normalização",
            "method": "hermes",
            "confidence": 0.9,
            "requires_review": False,
        }
        job = SimpleNamespace(total_rows=1, valid_rows=0, invalid_rows=0, report={"can_apply": False, "warnings": []})
        row = SimpleNamespace(
            row_number=1,
            raw_payload={"hostname": "pc-01"},
            normalized_payload={"hostname": "pc-01"},
            decision="REVIEW_REQUIRED",
            issues=[],
        )

        result = await analyze_import(job, [row], _Provider([suggestion]))

        self.assertEqual(1, len(result.ai_suggestions))
        self.assertTrue(result.ai_suggestions[0].requires_review)
        self.assertFalse(result.safe_to_apply)

    async def test_suggestions_persist_pending_and_require_explicit_decision_with_audit(self) -> None:
        actor_id = uuid.uuid4()
        job = _review_job({})
        analysis = ImportAiAnalysis(
            file_summary=ImportFileSummary(rows_total=1, rows_valid=0, rows_auto_corrected=0, rows_need_review=1, rows_invalid=0),
            ai_suggestions=[ImportCorrection(row=1, field="hostname", original_value="pc antigo", proposed_value="pc-antigo", reason="padronização", method="hermes", confidence=0.9, requires_review=True)],
            confidence=0,
        )
        staging = _review_staging(job, "pc antigo")
        session = _Session([staging], job)

        persisted = await persist_ai_suggestions(job, analysis, session, actor_id)
        self.assertEqual("PENDING", persisted[0].status)
        self.assertEqual("pc antigo", persisted[0].original_value)
        self.assertNotIn("hostname", job.report)
        self.assertEqual("CREATE", session.added[-1].action.value)
        suggestion_id = persisted[0].id

        decided_at = datetime(2026, 7, 17, tzinfo=UTC)
        approved = await decide_ai_suggestion(job.id, suggestion_id, "APPROVED", session, actor_id, decided_at)
        self.assertEqual("APPROVED", approved.status)
        self.assertEqual("pc-antigo", staging.normalized_payload["hostname"])
        self.assertEqual("CREATE", staging.decision)
        self.assertTrue(job.report["can_apply"])
        self.assertEqual(actor_id, approved.decided_by)
        self.assertEqual(decided_at, approved.decided_at)
        self.assertEqual(AuditAction.STATUS_CHANGE, session.added[-1].action)
        self.assertEqual("PENDING", session.added[-1].before["status"])
        self.assertEqual("APPROVED", session.added[-1].after["status"])
        self.assertEqual("pc antigo", approved.original_value)
        self.assertEqual([approved], list_ai_suggestions(job))
        self.assertEqual(approved, await decide_ai_suggestion(job.id, suggestion_id, "APPROVED", session, actor_id))

        with self.assertRaisesRegex(ValueError, "suggestion_already_decided"):
            await decide_ai_suggestion(job.id, suggestion_id, "REJECTED", session, actor_id)

    async def test_suggestion_can_be_rejected_with_audit(self) -> None:
        actor_id = uuid.uuid4()
        job = _review_job({})
        analysis = ImportAiAnalysis(
            file_summary=ImportFileSummary(rows_total=1, rows_valid=0, rows_auto_corrected=0, rows_need_review=1, rows_invalid=0),
            ai_suggestions=[ImportCorrection(row=1, field="hostname", original_value="pc 1", proposed_value="pc-1", reason="padronização", method="hermes", confidence=0.9, requires_review=True)],
            confidence=0,
        )
        staging = _review_staging(job, "pc 1")
        session = _Session([staging], job)
        suggestion = (await persist_ai_suggestions(job, analysis, session, actor_id))[0]

        rejected = await decide_ai_suggestion(job.id, suggestion.id, "REJECTED", session, actor_id)

        self.assertEqual("REJECTED", rejected.status)
        self.assertEqual("REJECTED", session.added[-1].after["status"])
        self.assertEqual("pc 1", staging.normalized_payload["hostname"])
        self.assertFalse(job.report["can_apply"])

    async def test_protected_field_without_real_source_stays_blocked(self) -> None:
        actor_id = uuid.uuid4()
        job = _review_job({})
        analysis = ImportAiAnalysis(
            file_summary=ImportFileSummary(rows_total=1, rows_valid=0, rows_auto_corrected=0, rows_need_review=1, rows_invalid=0),
            ai_suggestions=[ImportCorrection(row=1, field="serial", original_value="forged", proposed_value="INVENTED", reason="guess", method="hermes", confidence=0.9, requires_review=True)],
            confidence=0,
        )
        staging = SimpleNamespace(
            id=uuid.uuid4(), job_id=job.id, row_number=1, raw_payload={}, normalized_payload={},
            issues=[{"field":"serial"}], decision="REVIEW_REQUIRED", matched_asset_id=None,
            row_status="STAGED", identity_type=None, identity_value=None, merge_action="REVIEW",
            updated_by=None, deleted_at=None, identity_confidence=None,
        )
        session = _Session([staging], job)
        suggestion = (await persist_ai_suggestions(job, analysis, session, actor_id))[0]

        with self.assertRaisesRegex(ValueError, "protected_field_source_required"):
            await decide_ai_suggestion(job.id, suggestion.id, "APPROVED", session, actor_id)

        self.assertEqual({}, staging.normalized_payload)
        self.assertEqual("REVIEW_REQUIRED", staging.decision)


if __name__ == "__main__":
    unittest.main()
