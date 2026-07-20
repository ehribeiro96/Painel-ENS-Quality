from __future__ import annotations

import asyncio
import json
import re
import time
import uuid
from collections import Counter
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from app.core.config.settings import settings
from app.domains.ai_chat.providers import AiProvider, AiProviderMessage, HermesTerminalProvider
from app.domains.audit.service import AuditService
from app.domains.imports.models import ImportJob, ImportStagingAsset
from app.domains.imports.schemas import ImportAiAnalysis, ImportAiDiagnostics, ImportCorrection, ImportFileSummary
from app.shared.enums import AuditAction, ImportDecision
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

IDENTITY_FIELDS = {"serial", "patrimony", "ip_address", "mac_address", "user", "location"}
# ponytail: mantém a requisição síncrona; migrar para job assíncrono se análises concorrentes virarem gargalo.
IMPORT_AI_BACKEND_TIMEOUT_SECONDS = 120
IMPORT_AI_FRONTEND_TIMEOUT_MS = 125000
SUGGESTIONS_REPORT_KEY = "ai_suggestions"


class ImportAiAnalysisError(RuntimeError):
    pass


def _json_object(content: str) -> dict[str, object]:
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", content.strip(), flags=re.IGNORECASE)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ImportAiAnalysisError("hermes_invalid_json") from exc
    if not isinstance(value, dict):
        raise ImportAiAnalysisError("hermes_invalid_output")
    return value


async def analyze_import(
    job: ImportJob,
    rows: list[ImportStagingAsset],
    provider: AiProvider | None = None,
    *,
    timeout_seconds: float = IMPORT_AI_BACKEND_TIMEOUT_SECONDS,
) -> ImportAiAnalysis:
    started = time.perf_counter()
    prompt_chars = 0
    payload_bytes = 0
    hermes_ms = 0
    provider_name = "hermes"
    model_name = getattr(settings, "hermes_model", "hermes-agent") or "hermes-agent"
    deterministic: list[ImportCorrection] = []
    for row in rows:
        for field, proposed in row.normalized_payload.items():
            original = row.raw_payload.get(field)
            if original is not None and proposed != original:
                deterministic.append(ImportCorrection(row=row.row_number, field=field, original_value=original, proposed_value=proposed, reason="Normalização segura do importador", method="deterministic", confidence=1, requires_review=False))
    ambiguous = [row for row in rows if row.decision in {ImportDecision.REVIEW_REQUIRED.value, ImportDecision.CONFLICT.value}]
    suggestions: list[ImportCorrection] = []
    if ambiguous:
        sample = [{"row": row.row_number, "values": row.normalized_payload, "issues": row.issues} for row in ambiguous[:30]]
        prompt = "Sugira somente correções semânticas. Responda apenas JSON com ai_suggestions conforme o schema. Não invente serial, patrimônio, IP, MAC, usuário ou localização. Toda sugestão requer revisão humana.\n" + json.dumps({"schema": ImportCorrection.model_json_schema(), "rows": sample}, ensure_ascii=False, default=str)
        messages = [AiProviderMessage(role="system", content="Você analisa planilhas sem alterar dados."), AiProviderMessage(role="user", content=prompt)]
        prompt_chars = sum(len(message.content) for message in messages)
        payload_bytes = len(json.dumps([{"role": message.role, "content": message.content} for message in messages], ensure_ascii=False).encode("utf-8"))
        selected_provider = provider or HermesTerminalProvider(settings, timeout_seconds=max(1, int(timeout_seconds)), source="imports-ai-analysis")
        hermes_started = time.perf_counter()
        try:
            response = await asyncio.wait_for(selected_provider.generate(messages), timeout=timeout_seconds)
        except TimeoutError as exc:
            raise ImportAiAnalysisError("hermes_timeout") from exc
        finally:
            hermes_ms = round((time.perf_counter() - hermes_started) * 1000)
        provider_name = response.provider or provider_name
        model_name = response.model or model_name
        raw = _json_object(response.content).get("ai_suggestions", [])
        if not isinstance(raw, list):
            raise ImportAiAnalysisError("hermes_invalid_output")
        try:
            candidates = [
                ImportCorrection.model_validate({**item, "id": None, "method": "hermes", "requires_review": True, "status": None, "decided_by": None, "decided_at": None})
                for item in raw
                if isinstance(item, dict)
            ]
        except ValidationError as exc:
            raise ImportAiAnalysisError("hermes_invalid_output") from exc
        by_row = {row.row_number: row for row in ambiguous}
        for item in candidates:
            if item.row not in by_row:
                continue
            source_row = by_row[item.row]
            source_value = source_row.raw_payload.get(item.field)
            if source_value is None or source_value == "":
                source_value = source_row.normalized_payload.get(item.field)
            if source_value is None or source_value == "" or item.proposed_value is None or item.proposed_value == "" or item.proposed_value == source_value:
                continue
            suggestions.append(item.model_copy(update={"original_value": source_value, "method": "hermes", "requires_review": True}))
    invalid = [row.row_number for row in rows if row.decision == ImportDecision.INVALID.value]
    summary = ImportFileSummary(rows_total=job.total_rows, rows_valid=job.valid_rows, rows_auto_corrected=len({item.row for item in deterministic}), rows_need_review=len(ambiguous), rows_invalid=job.invalid_rows)
    confidence = 1 if not ambiguous and not invalid else max(0, round(job.valid_rows / max(job.total_rows, 1), 2))
    diagnostics = ImportAiDiagnostics(
        total_ms=round((time.perf_counter() - started) * 1000),
        payload_bytes=payload_bytes,
        prompt_chars=prompt_chars,
        hermes_ms=hermes_ms,
        frontend_timeout_ms=IMPORT_AI_FRONTEND_TIMEOUT_MS,
        backend_timeout_ms=round(timeout_seconds * 1000),
        provider=provider_name,
        model=model_name,
    )
    return ImportAiAnalysis(file_summary=summary, deterministic_corrections=deterministic, ai_suggestions=suggestions, ambiguous_rows=[row.row_number for row in ambiguous], invalid_rows=invalid, warnings=list((job.report or {}).get("warnings", [])), confidence=confidence, safe_to_apply=bool(job.report.get("can_apply") and not ambiguous and not invalid), diagnostics=diagnostics)


def list_ai_suggestions(job: ImportJob) -> list[ImportCorrection]:
    values = (job.report or {}).get(SUGGESTIONS_REPORT_KEY, [])
    if not isinstance(values, list):
        return []
    try:
        return [ImportCorrection.model_validate(value) for value in values]
    except ValidationError as exc:
        raise ImportAiAnalysisError("stored_ai_suggestions_invalid") from exc


def _suggestion_fingerprint(suggestion: ImportCorrection) -> str:
    return json.dumps(
        {"row": suggestion.row, "field": suggestion.field, "original_value": suggestion.original_value, "proposed_value": suggestion.proposed_value},
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )


async def persist_ai_suggestions(
    job: ImportJob,
    analysis: ImportAiAnalysis,
    session: AsyncSession,
    actor_id: UUID,
) -> list[ImportCorrection]:
    existing = list_ai_suggestions(job)
    by_fingerprint = {_suggestion_fingerprint(item): item for item in existing}
    persisted: list[ImportCorrection] = []
    for suggestion in analysis.ai_suggestions:
        current = by_fingerprint.get(_suggestion_fingerprint(suggestion))
        if current is None:
            current = suggestion.model_copy(update={"id": uuid.uuid4(), "status": "PENDING", "decided_by": None, "decided_at": None, "requires_review": True, "method": "hermes"})
            existing.append(current)
            await AuditService(session).record(
                action=AuditAction.CREATE,
                entity="ImportAiSuggestion",
                entity_id=current.id,
                actor_id=actor_id,
                after={"import_id": str(job.id), "row": current.row, "field": current.field, "status": current.status},
            )
        persisted.append(current)
    report = dict(job.report or {})
    report[SUGGESTIONS_REPORT_KEY] = [item.model_dump(mode="json") for item in existing]
    if analysis.diagnostics is not None:
        report["ai_analysis_diagnostics"] = analysis.diagnostics.model_dump(mode="json")
    job.report = report
    await session.flush()
    return persisted


async def decide_ai_suggestion(
    job: ImportJob,
    suggestion_id: UUID | None,
    decision: Literal["APPROVED", "REJECTED"],
    session: AsyncSession,
    actor_id: UUID,
    decided_at: datetime | None = None,
) -> ImportCorrection:
    if suggestion_id is None:
        raise ValueError("suggestion_not_found")
    suggestions = list_ai_suggestions(job)
    index = next((index for index, item in enumerate(suggestions) if item.id == suggestion_id), None)
    if index is None:
        raise ValueError("suggestion_not_found")
    current = suggestions[index]
    if current.status == decision:
        return current
    if current.status != "PENDING":
        raise ValueError("suggestion_already_decided")
    staging = await session.scalar(
        select(ImportStagingAsset).where(
            ImportStagingAsset.job_id == job.id,
            ImportStagingAsset.row_number == current.row,
            ImportStagingAsset.deleted_at.is_(None),
        )
    )
    if staging is None:
        raise ValueError("suggestion_staging_row_not_found")
    previous_value = staging.normalized_payload.get(current.field)
    if decision == "APPROVED":
        source_value = staging.raw_payload.get(current.field)
        if current.field in IDENTITY_FIELDS and (source_value is None or source_value == ""):
            raise ValueError("protected_field_source_required")
        normalized = dict(staging.normalized_payload)
        normalized[current.field] = current.proposed_value
        staging.normalized_payload = normalized
        staging.issues = [
            issue for issue in staging.issues
            if issue.get("field") != current.field and issue.get("field_name") != current.field
        ]
        if not staging.issues and staging.decision in {ImportDecision.REVIEW_REQUIRED.value, ImportDecision.CONFLICT.value}:
            staging.decision = ImportDecision.SAFE_UPDATE.value if staging.matched_asset_id else ImportDecision.CREATE.value
    updated = current.model_copy(update={"status": decision, "decided_by": actor_id, "decided_at": decided_at or datetime.now(UTC)})
    suggestions[index] = updated
    report = dict(job.report or {})
    report[SUGGESTIONS_REPORT_KEY] = [item.model_dump(mode="json") for item in suggestions]
    rows_result = await session.execute(
        select(ImportStagingAsset).where(ImportStagingAsset.job_id == job.id, ImportStagingAsset.deleted_at.is_(None))
    )
    rows = list(rows_result.scalars())
    counts = Counter(row.decision for row in rows)
    applicable = sum(counts[value] for value in (ImportDecision.CREATE.value, ImportDecision.SAFE_UPDATE.value, ImportDecision.SAFE_MERGE.value))
    blocking = counts[ImportDecision.CONFLICT.value]
    review = counts[ImportDecision.REVIEW_REQUIRED.value]
    blockers = []
    if blocking:
        blockers.append("Existem conflitos bloqueantes pendentes.")
    if review:
        blockers.append("Existem linhas que exigem revisao humana.")
    if not applicable:
        blockers.append("Nao existem linhas aplicaveis.")
    if report.get("import_mode") == "PREVIEW_ONLY":
        blockers.append("Modo PREVIEW_ONLY nao permite apply.")
    report.update(
        {
            "decision_counts": dict(counts),
            "applicable_rows_count": applicable,
            "blocking_conflicts_count": blocking,
            "review_required_count": review,
            "apply_blockers": blockers,
            "can_apply": applicable > 0 and not blocking and not review and report.get("import_mode") != "PREVIEW_ONLY",
        }
    )
    job.report = report
    await AuditService(session).record(
        action=AuditAction.STATUS_CHANGE,
        entity="ImportAiSuggestion",
        entity_id=suggestion_id,
        actor_id=actor_id,
        before={"import_id": str(job.id), "row": current.row, "field": current.field, "status": current.status, "value": previous_value},
        after={"import_id": str(job.id), "row": updated.row, "field": updated.field, "status": updated.status, "value": staging.normalized_payload.get(current.field)},
    )
    await session.flush()
    return updated
