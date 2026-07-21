from __future__ import annotations

import asyncio
import os
import unittest
import uuid
from datetime import UTC, datetime

from app.core.database import base as _database_base  # noqa: F401
from app.core.database.session import AsyncSessionLocal, engine
from app.domains.assets.models import Asset
from app.domains.audit.models import AuditLog
from app.domains.imports.models import ImportConflict, ImportJob, ImportStagingAsset, ImportValidationError
from app.domains.imports.schemas import ImportCorrection
from app.domains.imports.service import ImportService
from app.services.import_ai_analysis import SUGGESTIONS_REPORT_KEY, decide_ai_suggestion
from app.shared.enums import AssetStatus, AssetType, ImportDecision
from sqlalchemy import delete, func, select

POSTGRES_ENABLED = os.getenv("APOEMA_POSTGRES_TESTS") == "1"


@unittest.skipUnless(POSTGRES_ENABLED, "requires authorized PostgreSQL integration database")
class ImportReviewPostgresConcurrencyTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.job_id = uuid.uuid4()
        self.suggestion_id = uuid.uuid4()
        self.first_actor = uuid.uuid4()
        self.second_actor = uuid.uuid4()
        self.asset_ids: list[uuid.UUID] = []
        suggestion = ImportCorrection(
            id=self.suggestion_id,
            row=2,
            field="hostname",
            original_value="B4-OLD",
            proposed_value=f"B4-{self.job_id.hex[:12]}",
            reason="identity-map regression",
            method="hermes",
            confidence=0.9,
            requires_review=True,
            status="PENDING",
        )
        async with AsyncSessionLocal() as session:
            session.add(
                ImportJob(
                    id=self.job_id,
                    source="SPREADSHEET",
                    filename="b4-real-session.csv",
                    status="REVIEW_REQUIRED",
                    total_rows=1,
                    report={
                        "import_mode": "INITIAL_LOAD",
                        SUGGESTIONS_REPORT_KEY: [suggestion.model_dump(mode="json")],
                    },
                )
            )
            session.add(
                ImportStagingAsset(
                    job_id=self.job_id,
                    row_number=2,
                    raw_payload={"hostname": "B4-OLD"},
                    normalized_payload={"hostname": "B4-OLD", "asset_type": "DESKTOP"},
                    identity_type="hostname",
                    identity_value="B4-OLD",
                    decision=ImportDecision.REVIEW_REQUIRED.value,
                    row_status="STAGED",
                    merge_action="REVIEW",
                    issues=[{"field": "hostname", "code": "review"}],
                )
            )
            await session.commit()

    async def asyncTearDown(self) -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(AuditLog).where(AuditLog.entity_id == self.suggestion_id))
            await session.execute(delete(ImportConflict).where(ImportConflict.job_id == self.job_id))
            await session.execute(delete(ImportValidationError).where(ImportValidationError.job_id == self.job_id))
            await session.execute(delete(ImportStagingAsset).where(ImportStagingAsset.job_id == self.job_id))
            await session.execute(delete(ImportJob).where(ImportJob.id == self.job_id))
            if self.asset_ids:
                await session.execute(delete(Asset).where(Asset.id.in_(self.asset_ids)))
            await session.commit()
        await engine.dispose()

    async def _review_race(self, winner_decision: str, waiter_decision: str) -> tuple[object, object]:
        winner_preloaded = asyncio.Event()
        waiter_preloaded = asyncio.Event()
        winner_locked = asyncio.Event()
        waiter_started = asyncio.Event()
        object_ids: list[int] = []

        async def winner() -> object:
            async with AsyncSessionLocal() as session:
                job = await session.get(ImportJob, self.job_id)
                object_ids.append(id(job))
                winner_preloaded.set()
                await asyncio.wait_for(waiter_preloaded.wait(), timeout=5)
                await session.scalar(select(ImportJob).where(ImportJob.id == self.job_id).with_for_update())
                winner_locked.set()
                await asyncio.wait_for(waiter_started.wait(), timeout=5)
                result = await decide_ai_suggestion(
                    self.job_id,
                    self.suggestion_id,
                    winner_decision,
                    session,
                    self.first_actor,
                )
                await session.commit()
                return result

        async def waiter() -> object:
            async with AsyncSessionLocal() as session:
                job = await session.get(ImportJob, self.job_id)
                object_ids.append(id(job))
                waiter_preloaded.set()
                await asyncio.wait_for(winner_preloaded.wait(), timeout=5)
                await asyncio.wait_for(winner_locked.wait(), timeout=5)
                waiter_started.set()
                try:
                    result = await decide_ai_suggestion(
                        self.job_id,
                        self.suggestion_id,
                        waiter_decision,
                        session,
                        self.second_actor,
                    )
                    await session.commit()
                    return result
                except ValueError as exc:
                    await session.rollback()
                    return exc

        results = await asyncio.wait_for(
            asyncio.gather(asyncio.create_task(winner()), asyncio.create_task(waiter())),
            timeout=10,
        )
        self.assertEqual(2, len(set(object_ids)))
        async with AsyncSessionLocal() as session:
            audit_count = await session.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.entity == "ImportAiSuggestion", AuditLog.entity_id == self.suggestion_id)
            )
            final_job = await session.get(ImportJob, self.job_id)
            self.assertEqual(1, audit_count)
            self.assertEqual(winner_decision, final_job.report[SUGGESTIONS_REPORT_KEY][0]["status"])
        return results[0], results[1]

    async def test_approve_approve_is_idempotent_with_one_effective_audit(self) -> None:
        winner, waiter = await self._review_race("APPROVED", "APPROVED")
        self.assertEqual("APPROVED", winner.status)
        self.assertEqual("APPROVED", waiter.status)

    async def test_approve_reject_keeps_first_decision_and_conflicts(self) -> None:
        winner, waiter = await self._review_race("APPROVED", "REJECTED")
        self.assertEqual("APPROVED", winner.status)
        self.assertIsInstance(waiter, ValueError)
        self.assertEqual("suggestion_already_decided", str(waiter))

    async def test_reject_approve_keeps_first_decision_and_conflicts(self) -> None:
        winner, waiter = await self._review_race("REJECTED", "APPROVED")
        self.assertEqual("REJECTED", winner.status)
        self.assertIsInstance(waiter, ValueError)
        self.assertEqual("suggestion_already_decided", str(waiter))

    async def test_reject_reject_is_idempotent_with_one_effective_audit(self) -> None:
        winner, waiter = await self._review_race("REJECTED", "REJECTED")
        self.assertEqual("REJECTED", winner.status)
        self.assertEqual("REJECTED", waiter.status)

    async def test_preloaded_job_observes_committed_opposite_decision_after_lock(self) -> None:
        async with AsyncSessionLocal() as stale_session, AsyncSessionLocal() as winner_session:
            stale_job = await stale_session.get(ImportJob, self.job_id)
            winner_job = await winner_session.get(ImportJob, self.job_id)
            self.assertIsNotNone(stale_job)
            self.assertIsNotNone(winner_job)
            self.assertIsNot(stale_job, winner_job)

            approved = await decide_ai_suggestion(
                self.job_id,
                self.suggestion_id,
                "APPROVED",
                winner_session,
                self.first_actor,
            )
            await winner_session.commit()
            self.assertEqual("APPROVED", approved.status)

            with self.assertRaisesRegex(ValueError, "suggestion_already_decided"):
                await decide_ai_suggestion(
                    self.job_id,
                    self.suggestion_id,
                    "REJECTED",
                    stale_session,
                    self.second_actor,
                )
            await stale_session.rollback()

        async with AsyncSessionLocal() as verification_session:
            final_job = await verification_session.get(ImportJob, self.job_id)
            final_staging = await verification_session.scalar(
                select(ImportStagingAsset).where(ImportStagingAsset.job_id == self.job_id)
            )
            self.assertEqual(
                "APPROVED",
                final_job.report[SUGGESTIONS_REPORT_KEY][0]["status"],
            )
            self.assertEqual(
                f"B4-{self.job_id.hex[:12]}",
                final_staging.normalized_payload["hostname"],
            )

    async def test_waiter_observes_applying_status_after_lock(self) -> None:
        job_preloaded = asyncio.Event()
        updater_locked = asyncio.Event()
        reviewer_started = asyncio.Event()

        async def updater() -> None:
            async with AsyncSessionLocal() as session:
                await asyncio.wait_for(job_preloaded.wait(), timeout=5)
                job = await session.scalar(select(ImportJob).where(ImportJob.id == self.job_id).with_for_update())
                updater_locked.set()
                await asyncio.wait_for(reviewer_started.wait(), timeout=5)
                job.status = "APPLYING"
                await session.commit()

        async def reviewer() -> ValueError:
            async with AsyncSessionLocal() as session:
                await session.get(ImportJob, self.job_id)
                job_preloaded.set()
                await asyncio.wait_for(updater_locked.wait(), timeout=5)
                reviewer_started.set()
                try:
                    await decide_ai_suggestion(
                        self.job_id,
                        self.suggestion_id,
                        "APPROVED",
                        session,
                        self.second_actor,
                    )
                except ValueError as exc:
                    await session.rollback()
                    return exc
                self.fail("review must not proceed after APPLYING")

        _, error = await asyncio.wait_for(
            asyncio.gather(asyncio.create_task(updater()), asyncio.create_task(reviewer())),
            timeout=10,
        )
        self.assertEqual("import_not_reviewable", str(error))

    async def test_approve_reclassifies_create_row_against_existing_asset_without_applying(self) -> None:
        target_hostname = f"B4-{self.job_id.hex[:12]}"
        asset_id = uuid.uuid4()
        self.asset_ids.append(asset_id)
        async with AsyncSessionLocal() as session:
            asset = Asset(
                id=asset_id,
                hostname=target_hostname,
                asset_type=AssetType.DESKTOP,
                status=AssetStatus.STOCK,
            )
            session.add(asset)
            staging = await session.scalar(select(ImportStagingAsset).where(ImportStagingAsset.job_id == self.job_id))
            staging.decision = ImportDecision.CREATE.value
            staging.issues = []
            staging.merge_action = "CREATE_ASSET"
            job = await session.get(ImportJob, self.job_id)
            job.status = "READY_TO_APPLY"
            await session.commit()

        async with AsyncSessionLocal() as session:
            result = await decide_ai_suggestion(
                self.job_id,
                self.suggestion_id,
                "APPROVED",
                session,
                self.first_actor,
            )
            await session.commit()
            self.assertEqual("APPROVED", result.status)

        async with AsyncSessionLocal() as session:
            final_job = await session.get(ImportJob, self.job_id)
            final_staging = await session.scalar(
                select(ImportStagingAsset).where(ImportStagingAsset.job_id == self.job_id)
            )
            unchanged_asset = await session.get(Asset, asset_id)
            self.assertEqual(ImportDecision.SAFE_UPDATE.value, final_staging.decision)
            self.assertEqual(asset_id, final_staging.matched_asset_id)
            self.assertEqual("UPDATE_TRUSTED_FIELDS", final_staging.merge_action)
            self.assertEqual("hostname", final_staging.identity_type)
            self.assertEqual(target_hostname.upper(), final_staging.identity_value)
            self.assertEqual("MEDIUM", final_staging.identity_confidence)
            self.assertEqual([], final_staging.conflicts if hasattr(final_staging, "conflicts") else [])
            self.assertEqual([], final_staging.issues)
            self.assertTrue(final_job.report["can_apply"])
            self.assertEqual([], final_job.report["apply_blockers"])
            self.assertEqual(AssetStatus.STOCK, unchanged_asset.status)
            self.assertEqual(target_hostname, unchanged_asset.hostname)


@unittest.skipUnless(POSTGRES_ENABLED, "requires authorized PostgreSQL integration database")
class ImportCancelApplyPostgresConcurrencyTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.job_id = uuid.uuid4()
        self.cancel_actor = uuid.uuid4()
        self.apply_actor = uuid.uuid4()
        self.hostname = f"B5-{self.job_id.hex[:12]}"
        async with AsyncSessionLocal() as session:
            session.add(
                ImportJob(
                    id=self.job_id,
                    source="SPREADSHEET",
                    filename="b5-real-session.csv",
                    status="READY_TO_APPLY",
                    total_rows=1,
                    valid_rows=1,
                    report={"import_mode": "INITIAL_LOAD", "can_apply": True},
                )
            )
            session.add(
                ImportStagingAsset(
                    job_id=self.job_id,
                    row_number=2,
                    raw_payload={"hostname": self.hostname},
                    normalized_payload={"hostname": self.hostname, "asset_type": "DESKTOP"},
                    identity_type="hostname",
                    identity_value=self.hostname.upper(),
                    decision=ImportDecision.CREATE.value,
                    row_status="STAGED",
                    merge_action="CREATE_ASSET",
                    issues=[],
                )
            )
            await session.commit()

    async def asyncTearDown(self) -> None:
        async with AsyncSessionLocal() as session:
            asset = await session.scalar(select(Asset).where(Asset.hostname == self.hostname))
            entity_ids = [self.job_id]
            if asset is not None:
                entity_ids.append(asset.id)
            await session.execute(
                delete(AuditLog).where(
                    (AuditLog.actor_id.in_([self.cancel_actor, self.apply_actor]))
                    | (AuditLog.entity_id.in_(entity_ids))
                )
            )
            await session.execute(delete(ImportConflict).where(ImportConflict.job_id == self.job_id))
            await session.execute(delete(ImportValidationError).where(ImportValidationError.job_id == self.job_id))
            await session.execute(delete(ImportStagingAsset).where(ImportStagingAsset.job_id == self.job_id))
            await session.execute(delete(ImportJob).where(ImportJob.id == self.job_id))
            if asset is not None:
                await session.delete(asset)
            await session.commit()
        await engine.dispose()

    async def test_cancel_wins_and_waiting_apply_observes_cancelled(self) -> None:
        apply_preloaded = asyncio.Event()
        cancel_locked = asyncio.Event()
        apply_started = asyncio.Event()

        async def cancel() -> ImportJob:
            async with AsyncSessionLocal() as session:
                await asyncio.wait_for(apply_preloaded.wait(), timeout=5)
                await session.scalar(select(ImportJob).where(ImportJob.id == self.job_id).with_for_update())
                cancel_locked.set()
                await asyncio.wait_for(apply_started.wait(), timeout=5)
                result = await ImportService(session).cancel_import(self.job_id, self.cancel_actor)
                await session.commit()
                return result

        async def apply() -> ImportJob | ValueError:
            async with AsyncSessionLocal() as session:
                await session.get(ImportJob, self.job_id)
                apply_preloaded.set()
                await asyncio.wait_for(cancel_locked.wait(), timeout=5)
                apply_started.set()
                try:
                    result = await ImportService(session).apply_import(self.job_id, self.apply_actor)
                    await session.commit()
                    return result
                except ValueError as exc:
                    await session.rollback()
                    return exc

        cancelled, apply_result = await asyncio.wait_for(
            asyncio.gather(asyncio.create_task(cancel()), asyncio.create_task(apply())),
            timeout=10,
        )
        async with AsyncSessionLocal() as session:
            final_job = await session.get(ImportJob, self.job_id)
            applied_asset = await session.scalar(select(Asset).where(Asset.hostname == self.hostname))
            observed_status = final_job.status
            observed_asset_exists = applied_asset is not None
        print(
            {
                "cancel_result": cancelled.status,
                "apply_result": type(apply_result).__name__,
                "final_job_status": observed_status,
                "asset_applied": observed_asset_exists,
            }
        )
        self.assertEqual("CANCELLED", cancelled.status)
        self.assertIsInstance(apply_result, ValueError)
        self.assertEqual("import_not_applicable", str(apply_result))
        self.assertEqual("CANCELLED", observed_status)
        self.assertFalse(observed_asset_exists)

    async def test_apply_wins_and_waiting_cancel_observes_applied(self) -> None:
        cancel_preloaded = asyncio.Event()
        apply_locked = asyncio.Event()
        cancel_started = asyncio.Event()

        async def apply() -> ImportJob:
            async with AsyncSessionLocal() as session:
                await asyncio.wait_for(cancel_preloaded.wait(), timeout=5)
                await session.scalar(select(ImportJob).where(ImportJob.id == self.job_id).with_for_update())
                apply_locked.set()
                await asyncio.wait_for(cancel_started.wait(), timeout=5)
                result = await ImportService(session).apply_import(self.job_id, self.apply_actor)
                await session.commit()
                return result

        async def cancel() -> ImportJob | ValueError:
            async with AsyncSessionLocal() as session:
                await session.get(ImportJob, self.job_id)
                cancel_preloaded.set()
                await asyncio.wait_for(apply_locked.wait(), timeout=5)
                cancel_started.set()
                try:
                    result = await ImportService(session).cancel_import(self.job_id, self.cancel_actor)
                    await session.commit()
                    return result
                except ValueError as exc:
                    await session.rollback()
                    return exc

        applied, cancel_result = await asyncio.wait_for(
            asyncio.gather(asyncio.create_task(apply()), asyncio.create_task(cancel())),
            timeout=10,
        )
        async with AsyncSessionLocal() as session:
            final_job = await session.get(ImportJob, self.job_id)
            asset_count = await session.scalar(
                select(func.count()).select_from(Asset).where(Asset.hostname == self.hostname)
            )
        self.assertEqual("APPLIED", applied.status)
        self.assertIsInstance(cancel_result, ValueError)
        self.assertEqual("import_not_cancellable", str(cancel_result))
        self.assertEqual("APPLIED", final_job.status)
        self.assertEqual(1, asset_count)

    async def test_cancel_cancel_is_idempotent_with_one_effective_audit(self) -> None:
        first_locked = asyncio.Event()
        second_started = asyncio.Event()

        async def cancel(actor_id: uuid.UUID, *, winner: bool) -> ImportJob:
            async with AsyncSessionLocal() as session:
                if winner:
                    await session.scalar(select(ImportJob).where(ImportJob.id == self.job_id).with_for_update())
                    first_locked.set()
                    await asyncio.wait_for(second_started.wait(), timeout=5)
                else:
                    await asyncio.wait_for(first_locked.wait(), timeout=5)
                    second_started.set()
                result = await ImportService(session).cancel_import(self.job_id, actor_id)
                await session.commit()
                return result

        first, second = await asyncio.wait_for(
            asyncio.gather(
                asyncio.create_task(cancel(self.cancel_actor, winner=True)),
                asyncio.create_task(cancel(self.apply_actor, winner=False)),
            ),
            timeout=10,
        )
        async with AsyncSessionLocal() as session:
            cancel_audits = await session.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.entity_id == self.job_id, AuditLog.after.contains({"event": "import_cancelled"}))
            )
        self.assertEqual("CANCELLED", first.status)
        self.assertEqual("CANCELLED", second.status)
        self.assertEqual(1, cancel_audits)

    async def test_apply_apply_serializes_to_one_asset(self) -> None:
        first_locked = asyncio.Event()
        second_started = asyncio.Event()

        async def apply(actor_id: uuid.UUID, *, winner: bool) -> ImportJob | ValueError:
            async with AsyncSessionLocal() as session:
                if winner:
                    await session.scalar(select(ImportJob).where(ImportJob.id == self.job_id).with_for_update())
                    first_locked.set()
                    await asyncio.wait_for(second_started.wait(), timeout=5)
                else:
                    await asyncio.wait_for(first_locked.wait(), timeout=5)
                    await session.get(ImportJob, self.job_id)
                    second_started.set()
                try:
                    result = await ImportService(session).apply_import(self.job_id, actor_id)
                    await session.commit()
                    return result
                except ValueError as exc:
                    await session.rollback()
                    return exc

        first, second = await asyncio.wait_for(
            asyncio.gather(
                asyncio.create_task(apply(self.apply_actor, winner=True)),
                asyncio.create_task(apply(self.cancel_actor, winner=False)),
            ),
            timeout=10,
        )
        async with AsyncSessionLocal() as session:
            final_job = await session.get(ImportJob, self.job_id)
            asset_count = await session.scalar(
                select(func.count()).select_from(Asset).where(Asset.hostname == self.hostname)
            )
            apply_finished_audits = await session.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.entity_id == self.job_id, AuditLog.after.contains({"event": "import_apply_finished"}))
            )
        self.assertNotIsInstance(first, ValueError)
        self.assertEqual("APPLIED", getattr(first, "status", None))
        self.assertIsInstance(second, ValueError)
        self.assertEqual("import_not_applicable", str(second))
        self.assertEqual("APPLIED", final_job.status)
        self.assertEqual(1, asset_count)
        self.assertEqual(1, apply_finished_audits)

    async def test_cancel_state_contract_and_missing_job(self) -> None:
        for state, expected in (
            ("CANCELLED", None),
            ("APPLYING", "import_not_cancellable"),
            ("APPLIED", "import_not_cancellable"),
            ("APPLIED_WITH_ISSUES", "import_not_cancellable"),
            ("FAILED", "import_not_cancellable"),
        ):
            with self.subTest(state=state):
                async with AsyncSessionLocal() as session:
                    job = await session.get(ImportJob, self.job_id)
                    job.status = state
                    await session.commit()
                async with AsyncSessionLocal() as session:
                    if expected is None:
                        result = await ImportService(session).cancel_import(self.job_id, self.cancel_actor)
                        self.assertEqual("CANCELLED", result.status)
                    else:
                        with self.assertRaisesRegex(ValueError, expected):
                            await ImportService(session).cancel_import(self.job_id, self.cancel_actor)
                    await session.rollback()

        async with AsyncSessionLocal() as session:
            with self.assertRaisesRegex(ValueError, "import_not_found"):
                await ImportService(session).cancel_import(uuid.uuid4(), self.cancel_actor)

    async def test_apply_state_contract_and_missing_job(self) -> None:
        for state in ("CANCELLED", "APPLYING", "APPLIED", "APPLIED_WITH_ISSUES", "FAILED", "RECEIVED"):
            with self.subTest(state=state):
                async with AsyncSessionLocal() as session:
                    job = await session.get(ImportJob, self.job_id)
                    job.status = state
                    await session.commit()
                async with AsyncSessionLocal() as session:
                    await session.get(ImportJob, self.job_id)
                    with self.assertRaisesRegex(ValueError, "import_not_applicable"):
                        await ImportService(session).apply_import(self.job_id, self.apply_actor)
                    await session.rollback()

        async with AsyncSessionLocal() as session:
            with self.assertRaisesRegex(ValueError, "import_not_found"):
                await ImportService(session).apply_import(uuid.uuid4(), self.apply_actor)

    async def test_soft_deleted_job_is_not_applicable_or_cancellable(self) -> None:
        async with AsyncSessionLocal() as session:
            job = await session.get(ImportJob, self.job_id)
            job.deleted_at = datetime.now(UTC)
            await session.commit()

        async with AsyncSessionLocal() as session:
            with self.assertRaisesRegex(ValueError, "import_not_found"):
                await ImportService(session).apply_import(self.job_id, self.apply_actor)
            await session.rollback()

        async with AsyncSessionLocal() as session:
            with self.assertRaisesRegex(ValueError, "import_not_found"):
                await ImportService(session).cancel_import(self.job_id, self.cancel_actor)
            await session.rollback()

        async with AsyncSessionLocal() as session:
            job = await session.get(ImportJob, self.job_id)
            asset_count = await session.scalar(
                select(func.count()).select_from(Asset).where(Asset.hostname == self.hostname)
            )
        self.assertEqual("READY_TO_APPLY", job.status)
        self.assertEqual(0, asset_count)


if __name__ == "__main__":
    unittest.main()
