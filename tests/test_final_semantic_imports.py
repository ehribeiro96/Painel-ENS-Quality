from __future__ import annotations

import asyncio
import unittest
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.core.database import base as _database_base  # noqa: F401
from app.domains.imports.schemas import ImportCorrection
from app.domains.imports.service import ImportService
from app.services.import_ai_analysis import SUGGESTIONS_REPORT_KEY, decide_ai_suggestion
from app.shared.enums import ImportDecision

ROOT = Path(__file__).resolve().parents[1]


class _Asset:
    def __init__(self, hostname: str) -> None:
        self.id = uuid.uuid4()
        self.hostname = hostname
        self.serial = None
        self.patrimony = None
        self.location = None
        self.status = "AVAILABLE"
        self.deleted_at = None


class _Scalars:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def scalars(self):  # noqa: ANN201
        return self.values


class _ImportSession:
    def __init__(self, job: object, staging: object, asset: object | None = None) -> None:
        self.job = job
        self.staging = staging
        self.asset = asset
        self.statements: list[str] = []
        self.added: list[object] = []

    def add(self, value: object) -> None:
        self.added.append(value)

    async def flush(self) -> None:
        return None

    async def scalar(self, statement):  # noqa: ANN001, ANN201
        sql = str(statement)
        self.statements.append(sql)
        if "FROM import_jobs" in sql:
            return self.job
        if "FROM import_staging_assets" in sql:
            return self.staging
        return None

    async def execute(self, statement):  # noqa: ANN001, ANN201
        sql = str(statement)
        self.statements.append(sql)
        if "FROM import_staging_assets" in sql:
            return _Scalars([self.staging])
        if "FROM assets" in sql:
            return _Scalars([self.asset] if self.asset else [])
        return _Scalars([])


class _ConcurrentSession(_ImportSession):
    def __init__(
        self,
        job: object,
        staging: object,
        lock: asyncio.Lock,
        *,
        asset: object | None = None,
        acquired: asyncio.Event | None = None,
        gate: asyncio.Event | None = None,
    ) -> None:
        super().__init__(job, staging, asset)
        self.lock = lock
        self.acquired = acquired
        self.gate = gate
        self.holds_lock = False

    async def scalar(self, statement):  # noqa: ANN001, ANN201
        sql = str(statement)
        if "FROM import_jobs" in sql:
            self.statements.append(sql)
            await self.lock.acquire()
            self.holds_lock = True
            if self.acquired:
                self.acquired.set()
            if self.gate:
                await self.gate.wait()
            return self.job
        return await super().scalar(statement)

    async def commit(self) -> None:
        if self.holds_lock:
            self.holds_lock = False
            self.lock.release()

    async def rollback(self) -> None:
        await self.commit()


def _job(status: str = "REVIEW_REQUIRED") -> SimpleNamespace:
    suggestion = ImportCorrection(
        id=uuid.uuid4(),
        row=2,
        field="hostname",
        original_value="PC ANTIGO",
        proposed_value="PC-EXISTENTE",
        reason="synthetic",
        method="hermes",
        confidence=0.9,
        requires_review=True,
        status="PENDING",
    )
    return SimpleNamespace(
        id=uuid.uuid4(),
        source="SPREADSHEET",
        filename="synthetic.csv",
        status=status,
        total_rows=1,
        valid_rows=0,
        invalid_rows=0,
        created_rows=0,
        updated_rows=0,
        skipped_rows=0,
        conflict_rows=0,
        failed_rows=0,
        updated_by=None,
        report={
            "import_mode": "INITIAL_LOAD",
            "warnings": [],
            SUGGESTIONS_REPORT_KEY: [suggestion.model_dump(mode="json")],
        },
        suggestion=suggestion,
    )


def _staging(job: object) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        job_id=job.id,
        row_number=2,
        raw_payload={"hostname": "PC ANTIGO"},
        normalized_payload={"hostname": "PC ANTIGO", "asset_type": "DESKTOP", "identity_confidence": "MEDIUM"},
        identity_type="hostname",
        identity_value="PC ANTIGO",
        issues=[{"field": "hostname", "code": "review"}],
        decision=ImportDecision.REVIEW_REQUIRED.value,
        row_status="STAGED",
        matched_asset_id=None,
        merge_action="REVIEW",
        updated_by=None,
        deleted_at=None,
        identity_confidence="MEDIUM",
    )


class ImportReviewSemanticBlockerTest(unittest.IsolatedAsyncioTestCase):
    async def test_approve_reclassifies_against_existing_assets_and_locks_in_order(self) -> None:
        job = _job()
        staging = _staging(job)
        asset = _Asset("PC-EXISTENTE")
        session = _ImportSession(job, staging, asset)
        actor_id = uuid.uuid4()

        approved = await decide_ai_suggestion(
            job,
            job.suggestion.id,
            "APPROVED",
            session,
            actor_id,
            datetime(2026, 7, 21, tzinfo=UTC),
        )

        self.assertEqual("APPROVED", approved.status)
        self.assertEqual(asset.id, staging.matched_asset_id)
        self.assertEqual(ImportDecision.SAFE_UPDATE.value, staging.decision)
        self.assertEqual("UPDATE_TRUSTED_FIELDS", staging.merge_action)
        self.assertEqual("PC-EXISTENTE", staging.identity_value)
        self.assertTrue(job.report["can_apply"])
        lock_statements = [sql for sql in session.statements if "FOR UPDATE" in sql]
        self.assertIn("FROM import_jobs", lock_statements[0])
        self.assertIn("FROM import_staging_assets", lock_statements[1])

    async def test_terminal_or_applying_job_is_not_reviewable(self) -> None:
        for status in ("APPLYING", "APPLIED", "APPLIED_WITH_ISSUES", "CANCELLED", "FAILED"):
            with self.subTest(status=status):
                job = _job(status)
                staging = _staging(job)
                session = _ImportSession(job, staging)
                with self.assertRaisesRegex(ValueError, "import_not_reviewable"):
                    await decide_ai_suggestion(job, job.suggestion.id, "APPROVED", session, uuid.uuid4())
                self.assertEqual("PC ANTIGO", staging.normalized_payload["hostname"])


class ImportCancelApplySemanticBlockerTest(unittest.IsolatedAsyncioTestCase):
    async def test_cancel_locks_job_and_rejects_applying(self) -> None:
        job = _job("APPLYING")
        session = _ImportSession(job, _staging(job))

        with self.assertRaisesRegex(ValueError, "import_not_cancellable"):
            await ImportService(session).cancel_import(job, uuid.uuid4())

        self.assertEqual("APPLYING", job.status)
        self.assertTrue(any("FROM import_jobs" in sql and "FOR UPDATE" in sql for sql in session.statements))

    async def test_cancelled_is_idempotent_under_the_same_lock_protocol(self) -> None:
        job = _job("CANCELLED")
        session = _ImportSession(job, _staging(job))

        result = await ImportService(session).cancel_import(job, uuid.uuid4())

        self.assertIs(job, result)
        self.assertTrue(any("FROM import_jobs" in sql and "FOR UPDATE" in sql for sql in session.statements))
        self.assertEqual([], session.added)

    def test_apply_and_cancel_both_use_the_import_job_row_lock(self) -> None:
        source = (ROOT / "backend/app/domains/imports/service.py").read_text(encoding="utf-8")
        apply_body = source.split("async def apply_import", 1)[1].split("async def update_mapping", 1)[0]
        cancel_body = source.split("async def cancel_import", 1)[1].split("def _safe_filename", 1)[0]

        self.assertIn("select(ImportJob)", apply_body)
        self.assertIn("with_for_update()", apply_body)
        self.assertIn("select(ImportJob)", cancel_body)
        self.assertIn("with_for_update()", cancel_body)
        self.assertIn("import_not_cancellable", cancel_body)


class ImportConcurrencySemanticBlockerTest(unittest.IsolatedAsyncioTestCase):
    async def _review_race(self, first: str, second: str):
        job = _job()
        staging = _staging(job)
        asset = _Asset("PC-EXISTENTE")
        lock = asyncio.Lock()
        acquired = asyncio.Event()
        gate = asyncio.Event()
        first_session = _ConcurrentSession(job, staging, lock, asset=asset, acquired=acquired, gate=gate)
        second_session = _ConcurrentSession(job, staging, lock, asset=asset)

        async def decide(session: _ConcurrentSession, decision: str):
            try:
                result = await decide_ai_suggestion(job, job.suggestion.id, decision, session, uuid.uuid4())
                await session.commit()
                return result
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                return exc

        first_task = asyncio.create_task(decide(first_session, first))
        await acquired.wait()
        second_task = asyncio.create_task(decide(second_session, second))
        gate.set()
        return await asyncio.wait_for(asyncio.gather(first_task, second_task), timeout=1)

    async def test_approve_reject_decisions_are_serialized_across_independent_sessions(self) -> None:
        same_approve = await self._review_race("APPROVED", "APPROVED")
        self.assertEqual(["APPROVED", "APPROVED"], [item.status for item in same_approve])

        opposite = await self._review_race("APPROVED", "REJECTED")
        self.assertEqual("APPROVED", opposite[0].status)
        self.assertIsInstance(opposite[1], ValueError)
        self.assertIn("suggestion_already_decided", str(opposite[1]))

        same_reject = await self._review_race("REJECTED", "REJECTED")
        self.assertEqual(["REJECTED", "REJECTED"], [item.status for item in same_reject])

    async def _apply_cancel_race(self, first: str):
        job = _job("READY_TO_APPLY")
        staging = _staging(job)
        staging.decision = ImportDecision.CREATE.value
        staging.issues = []
        staging.merge_action = "CREATE_ASSET"
        lock = asyncio.Lock()
        acquired = asyncio.Event()
        gate = asyncio.Event()
        first_session = _ConcurrentSession(job, staging, lock, acquired=acquired, gate=gate)
        second_session = _ConcurrentSession(job, staging, lock)

        async def run(session: _ConcurrentSession, operation: str):
            try:
                service = ImportService(session)
                result = await (service.apply_import(job, uuid.uuid4()) if operation == "apply" else service.cancel_import(job, uuid.uuid4()))
                await session.commit()
                return result
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                return exc

        second = "cancel" if first == "apply" else "apply"
        with patch.object(ImportService, "_apply_safe_merges", new=AsyncMock(return_value={"created": 0, "updated": 0, "failed": 0})):
            first_task = asyncio.create_task(run(first_session, first))
            await acquired.wait()
            second_task = asyncio.create_task(run(second_session, second))
            gate.set()
            results = await asyncio.wait_for(asyncio.gather(first_task, second_task), timeout=1)
        return job, results

    async def test_apply_cancel_race_has_only_valid_terminal_states(self) -> None:
        applied_job, applied_results = await self._apply_cancel_race("apply")
        self.assertEqual("APPLIED", applied_job.status)
        self.assertIsInstance(applied_results[1], ValueError)
        self.assertIn("import_not_cancellable", str(applied_results[1]))

        cancelled_job, cancelled_results = await self._apply_cancel_race("cancel")
        self.assertEqual("CANCELLED", cancelled_job.status)
        self.assertIsInstance(cancelled_results[1], ValueError)
        self.assertIn("import_not_applicable", str(cancelled_results[1]))


class ImportsFrontendRetrySemanticBlockerTest(unittest.TestCase):
    def test_retry_is_operation_aware_and_never_replays_mutations(self) -> None:
        source = (ROOT / "frontend/itam-platform/src/apoema/pages/ImportsPage.tsx").read_text(encoding="utf-8")

        for operation in ("latest", "preview", "staging", "conflicts", "validation-errors", "suggestions"):
            self.assertIn(f'"{operation}"', source)
        self.assertIn("retryLoad", source)
        self.assertIn("failedLoad", source)
        retry_body = source.split("async function retryLoad", 1)[1].split("async function", 1)[0]
        for mutation in ("importUpload", "approveAiSuggestion", "rejectAiSuggestion", "applyImport", "cancelImport"):
            self.assertNotIn(mutation, retry_body)


if __name__ == "__main__":
    unittest.main()
