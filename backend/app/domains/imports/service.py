from __future__ import annotations

import hashlib
import io
import time
from collections import Counter
from datetime import datetime
from uuid import UUID

import pandas as pd
from app.core.config.settings import settings
from app.core.observability.metrics import metrics
from app.domains.assets.models import Asset
from app.domains.audit.service import AuditService
from app.domains.imports.conflict_detection.detector import detect_row_conflict
from app.domains.imports.merge_engine.policy import apply_trusted_updates, build_asset_from_import
from app.domains.imports.models import ImportConflict, ImportJob, ImportStagingAsset, ImportValidationError
from app.domains.imports.normalization.asset_normalizer import identity_for, normalize_asset_row
from app.domains.imports.presets import (
    detect_import_preset,
    distribution,
    effective_mapping,
    empty_columns,
    import_warnings,
    schema_signature,
)
from app.domains.imports.validators.asset_validator import validate_normalized_asset, validate_raw_row_security
from app.shared.audit_context import AuditContext
from app.shared.enums import AuditAction, ImportDecision, ImportRowStatus
from app.shared.snapshots import asset_snapshot
from fastapi import UploadFile
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class ImportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def import_lansweeper(self, file: UploadFile, actor_id: UUID | None, audit_context: AuditContext | None = None) -> ImportJob:
        return await self.upload_spreadsheet(file, actor_id, audit_context, source="LANSWEEPER", import_mode="INITIAL_LOAD")

    async def upload_spreadsheet(
        self,
        file: UploadFile,
        actor_id: UUID | None,
        audit_context: AuditContext | None = None,
        *,
        source: str = "SPREADSHEET",
        import_mode: str = "INITIAL_LOAD",
    ) -> ImportJob:
        started = time.perf_counter()
        content = await file.read()
        if len(content) > settings.upload_max_mb * 1024 * 1024:
            raise ValueError("upload_too_large")
        filename = self._safe_filename(file.filename or "upload")
        self._validate_upload_metadata(filename, content, file.content_type)
        import_mode = self._validate_import_mode(import_mode)
        dataframe, detected_sheet = self._parse_file(filename, content)
        if len(dataframe.index) > settings.import_max_rows:
            raise ValueError("import_row_limit_exceeded")
        raw_rows = dataframe.fillna("").to_dict(orient="records")
        columns = list(map(str, dataframe.columns))
        base_mapping = self._detected_mapping(dataframe.columns)
        preset = detect_import_preset(columns)
        detected_mapping = effective_mapping(preset, base_mapping, raw_rows)
        normalized_rows = [normalize_asset_row(row, detected_mapping) for row in raw_rows]
        existing_by_serial, existing_by_patrimony, existing_by_hostname = await self._load_existing_assets(normalized_rows)
        duplicate_plan = self._build_internal_duplicate_plan(normalized_rows)
        file_hash = hashlib.sha256(content).hexdigest()
        empty = empty_columns(raw_rows, columns)
        warnings = import_warnings(raw_rows, detected_mapping)
        previous_jobs = await self.session.execute(
            select(ImportJob)
            .where(ImportJob.deleted_at.is_(None))
            .order_by(ImportJob.created_at.desc())
            .limit(50)
        )
        if any((job.report or {}).get("file_hash") == file_hash for job in previous_jobs.scalars()):
            warnings.append("Arquivo semelhante já importado anteriormente.")

        job = ImportJob(
            source=source,
            filename=filename,
            status="STAGED",
            total_rows=len(dataframe.index),
            report={
                "pipeline": ["UPLOAD", "RAW_IMPORT_RECORD", "STAGING_VALIDATION", "NORMALIZATION", "CONFLICT_DETECTION", "MERGE_DECISION", "AWAITING_CONFIRMATION", "APPLY_CHANGES", "AUDIT_REPORT"],
                "columns": columns,
                "detected_columns": columns,
                "detected_mapping": detected_mapping,
                "mapping_json": detected_mapping,
                "import_mode": import_mode,
                "preset_name": preset.name if preset else None,
                "preset_version": preset.version if preset else None,
                "detected_sheet": detected_sheet,
                "schema_signature": schema_signature(columns),
                "missing_expected_columns": [column for column in (preset.expected_columns if preset else ()) if column not in columns],
                "empty_columns": empty,
                "warnings": warnings,
                "distributions": self._build_distributions(raw_rows, normalized_rows),
                "summary": self._build_summary(raw_rows, normalized_rows),
                "file_type": self._file_type(filename),
                "file_hash": file_hash,
                "upload_limits": {"upload_max_mb": settings.upload_max_mb, "import_max_rows": settings.import_max_rows},
                "deduplication_order": self._deduplication_order(detected_mapping),
                "preview": [],
            },
            created_by=actor_id,
            updated_by=actor_id,
        )
        self.session.add(job)
        await self.session.flush()

        seen_identities: set[tuple[str, str]] = set()
        staging_rows: list[ImportStagingAsset] = []
        for index, raw_row in enumerate(raw_rows, start=2):
            normalized = normalized_rows[index - 2]
            decision, detection_issues, matched_asset_id, merge_action = self._classify_row(
                raw_row,
                normalized,
                duplicate_plan.get(index - 2),
                existing_by_serial,
                existing_by_patrimony,
                existing_by_hostname,
                seen_identities,
            )
            identity_type, identity_value = identity_for(normalized)

            staging = ImportStagingAsset(
                job_id=job.id,
                row_number=index,
                raw_payload=self._safe_json_dict(raw_row),
                normalized_payload=normalized,
                identity_type=identity_type,
                identity_value=identity_value,
                decision=decision.value,
                row_status=ImportRowStatus.STAGED.value,
                matched_asset_id=matched_asset_id,
                merge_action=merge_action,
                issues=detection_issues,
                created_by=actor_id,
                updated_by=actor_id,
            )
            self.session.add(staging)
            staging_rows.append(staging)
            await self.session.flush()
            await self._persist_row_issues(job, staging, decision, detection_issues, actor_id)

        self._refresh_job_counts(job, staging_rows)
        job.report = self._build_report(job, staging_rows, {"created": 0, "updated": 0, "failed": 0}, was_applied=False)
        job.updated_by = actor_id

        await AuditService(self.session).record(
            action=AuditAction.IMPORT,
            entity="ImportJob",
            entity_id=job.id,
            actor_id=actor_id,
            after={"event": "import_uploaded", "report": job.report},
            source="spreadsheet_import",
            context=audit_context,
        )
        metrics.observe("itam_import_upload_duration_ms", (time.perf_counter() - started) * 1000, {"source": source.lower()})
        return job

    async def apply_import(self, job: ImportJob, actor_id: UUID | None, audit_context: AuditContext | None = None) -> ImportJob:
        locked = await self.session.scalar(select(ImportJob).where(ImportJob.id == job.id).with_for_update())
        if locked is not None:
            job = locked
        if job.status in {"APPLIED", "APPLIED_WITH_ISSUES", "CANCELLED"}:
            raise ValueError("import_not_applicable")
        if (job.report or {}).get("import_mode") == "PREVIEW_ONLY":
            raise ValueError("preview_only_import_not_applicable")
        result = await self.session.execute(
            select(ImportStagingAsset)
            .where(ImportStagingAsset.job_id == job.id, ImportStagingAsset.deleted_at.is_(None))
            .order_by(ImportStagingAsset.row_number)
        )
        staging_rows = list(result.scalars())
        blockers = [row for row in staging_rows if row.decision == ImportDecision.CONFLICT.value]
        if blockers:
            raise ValueError("import_has_blocking_conflicts")
        if not any(row.decision in self._applicable_decisions() for row in staging_rows):
            raise ValueError("import_has_no_applicable_rows")
        job.status = "APPLYING"
        await AuditService(self.session).record(
            action=AuditAction.IMPORT,
            entity="ImportJob",
            entity_id=job.id,
            actor_id=actor_id,
            before=job.report,
            after={"event": "import_apply_started", "safe_rows": sum(1 for row in staging_rows if row.decision in self._applicable_decisions())},
            source="spreadsheet_import",
            context=audit_context,
        )
        applied = await self._apply_safe_merges(job, staging_rows, actor_id, audit_context)
        job.created_rows = applied["created"]
        job.updated_rows = applied["updated"]
        job.skipped_rows = sum(1 for row in staging_rows if row.row_status == ImportRowStatus.SKIPPED.value)
        job.failed_rows = applied["failed"]
        job.status = "APPLIED_WITH_ISSUES" if (job.invalid_rows or job.conflict_rows or job.failed_rows) else "APPLIED"
        job.report = self._build_report(job, staging_rows, applied, was_applied=True)
        job.updated_by = actor_id

        await AuditService(self.session).record(
            action=AuditAction.IMPORT,
            entity="ImportJob",
            entity_id=job.id,
            actor_id=actor_id,
            after={"event": "import_apply_finished", "report": job.report},
            source="spreadsheet_import",
            context=audit_context,
        )
        return job

    def _applicable_decisions(self) -> set[str]:
        return {ImportDecision.CREATE.value, ImportDecision.SAFE_UPDATE.value, ImportDecision.SAFE_MERGE.value}

    async def update_mapping(
        self,
        job: ImportJob,
        mapping: dict[str, str],
        actor_id: UUID | None,
        audit_context: AuditContext | None = None,
        import_mode: str | None = None,
    ) -> ImportJob:
        if job.status in {"APPLIED", "APPLIED_WITH_ISSUES", "CANCELLED"}:
            raise ValueError("import_mapping_not_editable")
        before = dict(job.report or {})
        result = await self.session.execute(
            select(ImportStagingAsset)
            .where(ImportStagingAsset.job_id == job.id, ImportStagingAsset.deleted_at.is_(None))
            .order_by(ImportStagingAsset.row_number)
        )
        staging_rows = list(result.scalars())
        raw_rows = [row.raw_payload for row in staging_rows]
        normalized_rows = [normalize_asset_row(row, mapping) for row in raw_rows]
        existing_by_serial, existing_by_patrimony, existing_by_hostname = await self._load_existing_assets(normalized_rows)
        duplicate_plan = self._build_internal_duplicate_plan(normalized_rows)

        await self.session.execute(delete(ImportConflict).where(ImportConflict.job_id == job.id))
        await self.session.execute(delete(ImportValidationError).where(ImportValidationError.job_id == job.id))

        seen_identities: set[tuple[str, str]] = set()
        for index, (staging, normalized) in enumerate(zip(staging_rows, normalized_rows, strict=True)):
            decision, detection_issues, matched_asset_id, merge_action = self._classify_row(
                staging.raw_payload,
                normalized,
                duplicate_plan.get(index),
                existing_by_serial,
                existing_by_patrimony,
                existing_by_hostname,
                seen_identities,
            )
            identity_type, identity_value = identity_for(normalized)
            staging.normalized_payload = normalized
            staging.identity_type = identity_type
            staging.identity_value = identity_value
            staging.decision = decision.value
            staging.row_status = ImportRowStatus.STAGED.value
            staging.matched_asset_id = matched_asset_id
            staging.merge_action = merge_action
            staging.issues = detection_issues
            staging.updated_by = actor_id
            await self.session.flush()
            await self._persist_row_issues(job, staging, decision, detection_issues, actor_id)

        self._refresh_job_counts(job, staging_rows)
        previous_report = dict(job.report or {})
        next_import_mode = self._validate_import_mode(import_mode or str(previous_report.get("import_mode") or "INITIAL_LOAD"))
        job.report = {
            **previous_report,
            "mapping_json": mapping,
            "mapping_updated": True,
            "import_mode": next_import_mode,
            "summary": self._build_summary(raw_rows, normalized_rows),
            "distributions": self._build_distributions(raw_rows, normalized_rows),
            "quality": self._build_quality(staging_rows, normalized_rows),
        }
        rebuilt_report = self._build_report(job, staging_rows, {"created": 0, "updated": 0, "failed": 0}, was_applied=False)
        rebuilt_report["mapping_json"] = mapping
        rebuilt_report["mapping_updated"] = True
        rebuilt_report["import_mode"] = next_import_mode
        job.report = rebuilt_report
        job.updated_by = actor_id
        await AuditService(self.session).record(
            action=AuditAction.IMPORT,
            entity="ImportJob",
            entity_id=job.id,
            actor_id=actor_id,
            before={"mapping_json": before.get("mapping_json")},
            after={"event": "import_mapping_updated", "mapping_json": mapping, "valid_rows": job.valid_rows, "invalid_rows": job.invalid_rows, "conflict_rows": job.conflict_rows},
            source="spreadsheet_import",
            context=audit_context,
        )
        return job

    async def cancel_import(self, job: ImportJob, actor_id: UUID | None, audit_context: AuditContext | None = None) -> ImportJob:
        if job.status in {"APPLIED", "APPLIED_WITH_ISSUES"}:
            raise ValueError("applied_import_cannot_be_cancelled")
        before = {"status": job.status}
        job.status = "CANCELLED"
        job.updated_by = actor_id
        await AuditService(self.session).record(
            action=AuditAction.IMPORT,
            entity="ImportJob",
            entity_id=job.id,
            actor_id=actor_id,
            before=before,
            after={"event": "import_cancelled", "status": job.status},
            source="spreadsheet_import",
            context=audit_context,
        )
        return job

    def _safe_filename(self, filename: str) -> str:
        safe = filename.split("/")[-1].split("\\")[-1].replace("\x00", "").strip()
        return safe[:260] or "upload"

    def _validate_import_mode(self, import_mode: str) -> str:
        normalized = (import_mode or "INITIAL_LOAD").upper()
        if normalized not in {"INITIAL_LOAD", "SAFE_REIMPORT", "PREVIEW_ONLY"}:
            raise ValueError("invalid_import_mode")
        return normalized

    def _validate_upload_metadata(self, filename: str, content: bytes, content_type: str | None = None) -> None:
        if len(filename) > 260 or "/" in filename or "\\" in filename or "\x00" in filename:
            raise ValueError("invalid_upload_filename")
        suffix = filename.lower()
        if not suffix.endswith((".csv", ".xlsx")):
            raise ValueError("unsupported_import_file")
        if suffix.endswith(".xlsm"):
            raise ValueError("unsupported_import_file")
        if content_type and content_type not in {
            "text/csv",
            "application/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/octet-stream",
        }:
            raise ValueError("unsupported_import_content_type")
        if suffix.endswith(".xlsx") and not content.startswith(b"PK"):
            raise ValueError("invalid_xlsx_payload")
        if suffix.endswith(".csv") and b"\x00" in content:
            raise ValueError("invalid_csv_payload")
        if not content:
            raise ValueError("empty_import_file")

    def _file_type(self, filename: str) -> str:
        if filename.lower().endswith(".xlsx"):
            return "xlsx"
        return "csv"

    def _detected_mapping(self, columns) -> dict[str, str]:
        from app.domains.imports.normalization.asset_normalizer import normalize_column_name

        mapping: dict[str, str] = {}
        for column in columns:
            normalized = normalize_column_name(column)
            if normalized in {
                "hostname",
                "serial",
                "patrimony",
                "manufacturer",
                "model",
                "asset_type",
                "fallback_asset_type",
                "user",
                "user_email",
                "location",
                "unit",
                "network_location",
                "operating_system",
                "ip_address",
                "last_login",
                "status",
                "source_state",
                "notes",
                "first_seen",
                "last_tried",
                "fqdn",
                "dns_name",
                "source_notes",
                "source",
            }:
                mapping[str(column)] = normalized
        return mapping

    def _parse_file(self, filename: str, content: bytes) -> tuple[pd.DataFrame, str | None]:
        suffix = filename.lower()
        if suffix.endswith(".csv"):
            return pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, encoding="utf-8-sig"), None
        if suffix.endswith(".xlsx"):
            workbook = pd.ExcelFile(io.BytesIO(content))
            sheet_name = "report" if "report" in workbook.sheet_names else workbook.sheet_names[0]
            return pd.read_excel(workbook, sheet_name=sheet_name, dtype=str, keep_default_na=False), sheet_name
        raise ValueError("unsupported_import_file")

    def _deduplication_order(self, mapping: dict[str, str]) -> list[str]:
        order = ["serial"]
        if "patrimony" in set(mapping.values()):
            order.append("patrimony")
        order.append("hostname")
        return order

    def _build_internal_duplicate_plan(self, normalized_rows: list[dict[str, object]]) -> dict[int, dict[str, object]]:
        plan: dict[int, dict[str, object]] = {}

        def group_by(field: str) -> dict[str, list[int]]:
            groups: dict[str, list[int]] = {}
            for index, row in enumerate(normalized_rows):
                value = row.get(field)
                if value:
                    groups.setdefault(str(value), []).append(index)
            return groups

        for serial, indexes in group_by("serial").items():
            hostnames = {str(normalized_rows[index].get("hostname")) for index in indexes if normalized_rows[index].get("hostname")}
            if len(hostnames) > 1:
                for index in indexes:
                    plan[index] = {
                        "decision": ImportDecision.CONFLICT,
                        "issue": {
                            "code": "serial_hostname_divergence",
                            "identity_type": "serial",
                            "identity_value": serial,
                            "rows": [row + 2 for row in indexes],
                            "hostnames": sorted(hostnames),
                            "message": f"Conflito real: serial {serial} aparece com hostnames diferentes.",
                            "suggested_action": "Revisar manualmente antes do apply.",
                        },
                    }

        for hostname, indexes in group_by("hostname").items():
            serials = {str(normalized_rows[index].get("serial")) for index in indexes if normalized_rows[index].get("serial")}
            if len(serials) > 1:
                for index in indexes:
                    plan[index] = {
                        "decision": ImportDecision.CONFLICT,
                        "issue": {
                            "code": "hostname_serial_divergence",
                            "identity_type": "hostname",
                            "identity_value": hostname,
                            "rows": [row + 2 for row in indexes],
                            "serials": sorted(serials),
                            "message": f"Conflito real: hostname {hostname} aparece com seriais diferentes.",
                            "suggested_action": "Revisar manualmente antes do apply.",
                        },
                    }

        primary_groups: dict[tuple[str, str], list[int]] = {}
        for index, row in enumerate(normalized_rows):
            identity_type, identity_value = identity_for(row)
            if identity_type and identity_value:
                primary_groups.setdefault((identity_type, identity_value), []).append(index)

        for (identity_type, identity_value), indexes in primary_groups.items():
            if len(indexes) < 2 or any(index in plan for index in indexes):
                continue
            canonical = max(indexes, key=lambda index: self._canonical_score(normalized_rows[index]))
            for index in indexes:
                if index == canonical:
                    continue
                plan[index] = {
                    "decision": ImportDecision.SKIPPED_DUPLICATE_IN_FILE,
                    "issue": {
                        "code": "skipped_duplicate_in_file",
                        "identity_type": identity_type,
                        "identity_value": identity_value,
                        "rows": [row + 2 for row in indexes],
                        "canonical_row": canonical + 2,
                        "message": f"Duplicidade no arquivo: {identity_type} {identity_value} aparece em múltiplas linhas. O sistema manterá a linha {canonical + 2} e ignorará esta duplicata equivalente.",
                        "suggested_action": "Nenhuma ação necessária se os dados forem equivalentes.",
                    },
                }
        return plan

    def _canonical_score(self, row: dict[str, object]) -> tuple[int, int, float, int, int, int]:
        useful_fields = sum(1 for value in row.values() if value not in (None, "", {}, []))
        return (
            1 if row.get("serial") else 0,
            1 if row.get("hostname") else 0,
            self._last_seen_score(row),
            useful_fields,
            1 if row.get("asset_type") and row.get("asset_type") != "OTHER" else 0,
            1 if row.get("status") else 0,
        )

    def _last_seen_score(self, row: dict[str, object]) -> float:
        value = row.get("last_login") or (row.get("source_metadata") or {}).get("last_seen")
        if not value:
            return 0.0
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
        except ValueError:
            parsed = pd.to_datetime(str(value), errors="coerce")
            if pd.isna(parsed):
                return 0.0
            return parsed.timestamp()

    def _classify_row(
        self,
        raw_row: dict[str, object],
        normalized: dict[str, object],
        duplicate_action: dict[str, object] | None,
        existing_by_serial: dict[str, Asset],
        existing_by_patrimony: dict[str, Asset],
        existing_by_hostname: dict[str, Asset],
        seen_identities: set[tuple[str, str]],
    ) -> tuple[ImportDecision, list[dict[str, object]], UUID | None, str | None]:
        validation_issues = self._dedupe_issues(validate_raw_row_security(raw_row) + validate_normalized_asset(normalized))
        if validation_issues:
            return ImportDecision.INVALID, validation_issues, None, None

        if duplicate_action:
            decision = duplicate_action["decision"]
            issue = duplicate_action["issue"]
            if decision == ImportDecision.SKIPPED_DUPLICATE_IN_FILE:
                return ImportDecision.SKIPPED_DUPLICATE_IN_FILE, [issue], None, "SKIP_DUPLICATE_IN_FILE"
            if decision == ImportDecision.CONFLICT:
                return ImportDecision.CONFLICT, [issue], None, "REVIEW"

        detection = detect_row_conflict(normalized, existing_by_serial, existing_by_patrimony, existing_by_hostname, seen_identities)
        return detection.decision, detection.issues, detection.matched_asset_id, detection.merge_action

    def _dedupe_issues(self, issues: list[dict[str, object]]) -> list[dict[str, object]]:
        seen: set[tuple[str, str]] = set()
        deduped: list[dict[str, object]] = []
        for issue in issues:
            key = (str(issue.get("field") or "row"), str(issue.get("code") or "validation_error"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(issue)
        return deduped

    def _build_summary(self, raw_rows: list[dict[str, object]], normalized_rows: list[dict[str, object]]) -> dict[str, int]:
        return {
            "total_rows": len(normalized_rows),
            "rows_with_valid_serial": sum(1 for row in normalized_rows if row.get("serial")),
            "rows_without_valid_serial": sum(1 for row in normalized_rows if not row.get("serial")),
            "rows_with_hostname": sum(1 for row in normalized_rows if row.get("hostname")),
            "rows_without_hostname": sum(1 for row in normalized_rows if not row.get("hostname")),
            "rows_without_patrimony": sum(1 for row in normalized_rows if not row.get("patrimony")),
            "rows_with_user_hint": sum(1 for row in normalized_rows if (row.get("source_metadata") or {}).get("imported_user_hint")),
            "rows_with_location": sum(1 for row in normalized_rows if row.get("location")),
            "rows_with_recognized_status": sum(1 for row in normalized_rows if row.get("status")),
            "rows_with_recognized_type": sum(1 for row in normalized_rows if row.get("asset_type") and row.get("asset_type") != "OTHER"),
        }

    def _build_distributions(self, raw_rows: list[dict[str, object]], normalized_rows: list[dict[str, object]]) -> dict[str, dict[str, int]]:
        return {
            "state": distribution(raw_rows, "State"),
            "custom1": distribution(raw_rows, "Custom1"),
            "location": distribution(raw_rows, "Location"),
            "building": distribution(raw_rows, "Building"),
            "asset_family": dict(Counter(str(row.get("asset_family") or "OTHER") for row in normalized_rows)),
        }

    def _build_quality(self, staging_rows: list[ImportStagingAsset], normalized_rows: list[dict[str, object]]) -> dict[str, float | int]:
        total = max(len(normalized_rows), 1)
        decisions = Counter(row.decision for row in staging_rows)

        def pct(value: int) -> float:
            return round((value / total) * 100, 2)

        return {
            "pct_with_valid_serial": pct(sum(1 for row in normalized_rows if row.get("serial"))),
            "pct_with_hostname": pct(sum(1 for row in normalized_rows if row.get("hostname"))),
            "pct_without_patrimony": pct(sum(1 for row in normalized_rows if not row.get("patrimony"))),
            "pct_with_recognized_type": pct(sum(1 for row in normalized_rows if row.get("asset_type") and row.get("asset_type") != "OTHER")),
            "pct_with_recognized_status": pct(sum(1 for row in normalized_rows if row.get("status"))),
            "pct_with_user_hint": pct(sum(1 for row in normalized_rows if (row.get("source_metadata") or {}).get("imported_user_hint"))),
            "pct_with_location": pct(sum(1 for row in normalized_rows if row.get("location"))),
            "pct_create": pct(decisions[ImportDecision.CREATE.value]),
            "pct_safe_update": pct(decisions[ImportDecision.SAFE_UPDATE.value] + decisions[ImportDecision.SAFE_MERGE.value]),
            "pct_review_required": pct(decisions[ImportDecision.REVIEW_REQUIRED.value]),
            "pct_conflict": pct(decisions[ImportDecision.CONFLICT.value]),
            "pct_invalid": pct(decisions[ImportDecision.INVALID.value]),
        }

    def _refresh_job_counts(self, job: ImportJob, staging_rows: list[ImportStagingAsset]) -> None:
        counts = Counter(row.decision for row in staging_rows)
        job.valid_rows = counts[ImportDecision.CREATE.value] + counts[ImportDecision.SAFE_UPDATE.value] + counts[ImportDecision.SAFE_MERGE.value]
        job.invalid_rows = counts[ImportDecision.INVALID.value]
        job.conflict_rows = counts[ImportDecision.CONFLICT.value]
        job.created_rows = 0
        job.updated_rows = 0
        job.skipped_rows = 0
        job.failed_rows = 0
        if (job.report or {}).get("import_mode") == "PREVIEW_ONLY":
            job.status = "PREVIEW_ONLY"
        else:
            blocking = counts[ImportDecision.CONFLICT.value]
            job.status = "READY_TO_APPLY" if job.valid_rows and not blocking else "REVIEW_REQUIRED"

    async def _load_existing_assets(
        self,
        normalized_rows: list[dict[str, object]],
    ) -> tuple[dict[str, Asset], dict[str, Asset], dict[str, Asset]]:
        serials = {str(row["serial"]) for row in normalized_rows if row.get("serial")}
        patrimonies = {str(row["patrimony"]) for row in normalized_rows if row.get("patrimony")}
        hostnames = {str(row["hostname"]) for row in normalized_rows if row.get("hostname")}
        if not serials and not patrimonies and not hostnames:
            return {}, {}, {}

        result = await self.session.execute(
            select(Asset).where(
                Asset.deleted_at.is_(None),
                or_(Asset.serial.in_(serials), Asset.patrimony.in_(patrimonies), Asset.hostname.in_(hostnames)),
            )
        )
        assets = list(result.scalars())
        return (
            {asset.serial: asset for asset in assets if asset.serial},
            {asset.patrimony: asset for asset in assets if asset.patrimony},
            {asset.hostname: asset for asset in assets if asset.hostname},
        )

    async def _persist_row_issues(
        self,
        job: ImportJob,
        staging: ImportStagingAsset,
        decision: ImportDecision,
        issues: list[dict[str, object]],
        actor_id: UUID | None,
    ) -> None:
        if decision in {ImportDecision.CREATE, ImportDecision.SAFE_UPDATE, ImportDecision.SAFE_MERGE, ImportDecision.SKIPPED, ImportDecision.SKIPPED_DUPLICATE_IN_FILE}:
            return
        seen: set[tuple[int | None, str, str]] = set()
        for issue in issues:
            field_name = str(issue.get("field") or "row")
            error_code = str(issue.get("code") or "validation_error")
            key = (staging.row_number, field_name, error_code)
            if key in seen:
                continue
            seen.add(key)
            if decision == ImportDecision.INVALID:
                self.session.add(
                    ImportValidationError(
                        job_id=job.id,
                        staging_asset_id=staging.id,
                        row_number=staging.row_number,
                        field_name=field_name,
                        error_code=error_code,
                        message=str(issue.get("message") or issue.get("code") or "Linha invalida."),
                        created_by=actor_id,
                        updated_by=actor_id,
                    )
                )
            else:
                self.session.add(
                    ImportConflict(
                        job_id=job.id,
                        staging_asset_id=staging.id,
                        conflict_type=error_code,
                        severity="HIGH" if decision == ImportDecision.CONFLICT else "MEDIUM",
                        details=issue,
                        created_by=actor_id,
                        updated_by=actor_id,
                    )
                )

    async def _apply_safe_merges(
        self,
        job: ImportJob,
        staging_rows: list[ImportStagingAsset],
        actor_id: UUID | None,
        audit_context: AuditContext | None,
    ) -> dict[str, int]:
        counters = {"created": 0, "updated": 0, "failed": 0}
        for staging in staging_rows:
            if staging.decision not in self._applicable_decisions():
                staging.row_status = ImportRowStatus.SKIPPED.value
                continue
            try:
                async with self.session.begin_nested():
                    if staging.matched_asset_id is None:
                        normalized_for_create = dict(staging.normalized_payload)
                        normalized_for_create["notes"] = f"Importado do Lansweeper no lote {job.id}." if job.report.get("preset_name") else f"Importado por planilha no lote {job.id}."
                        asset = build_asset_from_import(normalized_for_create, actor_id)
                        self.session.add(asset)
                        await self.session.flush()
                        staging.matched_asset_id = asset.id
                        staging.row_status = ImportRowStatus.APPLIED.value
                        counters["created"] += 1
                        await AuditService(self.session).record(
                            action=AuditAction.CREATE,
                            entity="Asset",
                            entity_id=asset.id,
                            actor_id=actor_id,
                            after=asset_snapshot(asset),
                            source="spreadsheet_import",
                            context=audit_context,
                        )
                        await AuditService(self.session).record(
                            action=AuditAction.IMPORT,
                            entity="ImportJob",
                            entity_id=job.id,
                            actor_id=actor_id,
                            after={"event": "import_row_created_asset", "row_number": staging.row_number, "asset_id": str(asset.id)},
                            source="spreadsheet_import",
                            context=audit_context,
                        )
                    else:
                        asset = await self.session.get(Asset, staging.matched_asset_id, with_for_update=True)
                        if asset is None or asset.deleted_at is not None:
                            staging.row_status = ImportRowStatus.FAILED.value
                            counters["failed"] += 1
                            continue
                        before, after, changed = apply_trusted_updates(asset, staging.normalized_payload, actor_id)
                        staging.row_status = ImportRowStatus.APPLIED.value if changed else ImportRowStatus.SKIPPED.value
                        if changed:
                            counters["updated"] += 1
                            await AuditService(self.session).record(
                                action=AuditAction.UPDATE,
                                entity="Asset",
                                entity_id=asset.id,
                                actor_id=actor_id,
                                before=before,
                                after=after,
                                source="spreadsheet_import",
                                context=audit_context,
                            )
                            await AuditService(self.session).record(
                                action=AuditAction.IMPORT,
                                entity="ImportJob",
                                entity_id=job.id,
                                actor_id=actor_id,
                                after={"event": "import_row_updated_asset", "row_number": staging.row_number, "asset_id": str(asset.id)},
                                source="spreadsheet_import",
                                context=audit_context,
                            )
                        else:
                            await AuditService(self.session).record(
                                action=AuditAction.IMPORT,
                                entity="ImportJob",
                                entity_id=job.id,
                                actor_id=actor_id,
                                after={"event": "import_row_skipped", "row_number": staging.row_number, "asset_id": str(asset.id)},
                                source="spreadsheet_import",
                                context=audit_context,
                            )
            except Exception as exc:
                staging.row_status = ImportRowStatus.FAILED.value
                staging.issues = [
                    *(staging.issues or []),
                    {
                        "field": "row",
                        "code": "apply_failed",
                        "message": f"Linha nao aplicada por erro isolado: {type(exc).__name__}.",
                    },
                ]
                counters["failed"] += 1
                await self.session.flush()
        return counters

    def _build_report(self, job: ImportJob, staging_rows: list[ImportStagingAsset], counters: dict[str, int], *, was_applied: bool) -> dict[str, object]:
        decision_counts = Counter(row.decision for row in staging_rows)
        status_counts = Counter(row.row_status for row in staging_rows)
        normalized_rows = [row.normalized_payload for row in staging_rows]
        current_report = job.report or {}
        applicable_rows_count = sum(1 for row in staging_rows if row.decision in self._applicable_decisions())
        blocking_conflicts_count = decision_counts[ImportDecision.CONFLICT.value]
        review_required_count = decision_counts[ImportDecision.REVIEW_REQUIRED.value]
        apply_blockers: list[str] = []
        if current_report.get("import_mode") == "PREVIEW_ONLY":
            apply_blockers.append("Modo PREVIEW_ONLY nao permite apply.")
        if blocking_conflicts_count:
            apply_blockers.append("Existem conflitos bloqueantes pendentes.")
        if not applicable_rows_count:
            apply_blockers.append("Nao existem linhas aplicaveis.")
        can_apply = applicable_rows_count > 0 and not blocking_conflicts_count and current_report.get("import_mode") != "PREVIEW_ONLY"
        preview = [
            {
                "row_number": row.row_number,
                "decision": row.decision,
                "status": row.row_status,
                "identity_type": row.identity_type,
                "identity_value": row.identity_value,
                "identity_confidence": row.identity_confidence,
                "merge_action": row.merge_action,
                "issues": row.issues,
                "normalized": row.normalized_payload,
            }
            for row in staging_rows[:50]
        ]
        return {
            "source": job.source,
            "filename": job.filename,
            "columns": list(current_report.get("columns", [])),
            "detected_columns": list(current_report.get("detected_columns", current_report.get("columns", []))),
            "detected_mapping": dict(current_report.get("detected_mapping", {})),
            "mapping_json": dict(current_report.get("mapping_json", {})),
            "import_mode": current_report.get("import_mode", "INITIAL_LOAD"),
            "preset_name": current_report.get("preset_name"),
            "preset_version": current_report.get("preset_version"),
            "detected_sheet": current_report.get("detected_sheet"),
            "schema_signature": current_report.get("schema_signature"),
            "missing_expected_columns": list(current_report.get("missing_expected_columns", [])),
            "empty_columns": list(current_report.get("empty_columns", [])),
            "warnings": list(current_report.get("warnings", [])),
            "summary": dict(current_report.get("summary", {})),
            "distributions": dict(current_report.get("distributions", {})),
            "quality": self._build_quality(staging_rows, normalized_rows),
            "file_type": current_report.get("file_type"),
            "file_hash": current_report.get("file_hash"),
            "status": job.status,
            "applied": was_applied,
            "total_rows": job.total_rows,
            "valid_rows": job.valid_rows,
            "invalid_rows": job.invalid_rows,
            "conflict_rows": job.conflict_rows,
            "created_rows": counters["created"],
            "updated_rows": counters["updated"],
            "skipped_rows": job.skipped_rows,
            "failed_rows": counters["failed"],
            "decision_counts": dict(decision_counts),
            "row_status_counts": dict(status_counts),
            "duplicate_groups_count": self._duplicate_groups_count(staging_rows),
            "duplicate_rows_skipped": decision_counts[ImportDecision.SKIPPED_DUPLICATE_IN_FILE.value],
            "canonical_rows_selected": self._duplicate_groups_count(staging_rows),
            "invalid_rows_ignored": decision_counts[ImportDecision.INVALID.value],
            "applicable_rows_count": applicable_rows_count,
            "blocking_conflicts_count": blocking_conflicts_count,
            "review_required_count": review_required_count,
            "can_apply": can_apply,
            "apply_blockers": apply_blockers,
            "deduplication_order": list(current_report.get("deduplication_order", ["serial", "patrimony", "hostname"])),
            "merge_policy": {
                "trusted_fields": ["hostname", "patrimony", "serial", "manufacturer", "model", "asset_type", "operating_system", "ip_address", "last_login"],
                "protected_fields": ["current_user_id", "location", "status", "notes", "movements"],
            },
            "preview": preview,
        }

    def _duplicate_groups_count(self, staging_rows: list[ImportStagingAsset]) -> int:
        groups: set[tuple[str, str, int | None]] = set()
        for row in staging_rows:
            if row.decision != ImportDecision.SKIPPED_DUPLICATE_IN_FILE.value:
                continue
            issue = row.issues[0] if row.issues else {}
            groups.add((str(issue.get("identity_type")), str(issue.get("identity_value")), issue.get("canonical_row")))
        return len(groups)

    def _safe_json_dict(self, row: dict[str, object]) -> dict[str, object]:
        return {str(key): None if value is None else str(value) for key, value in row.items()}
