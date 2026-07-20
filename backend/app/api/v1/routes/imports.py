from __future__ import annotations

import time
from typing import Literal
from uuid import UUID

from app.api.v1.dependencies.auth import get_current_user, require_ai_capability, require_role
from app.core.config.settings import settings
from app.core.database.session import get_session
from app.core.permissions.ai import ensure_ai_enabled
from app.domains.ai_chat.providers import AiProviderConfigurationError, AiProviderRequestError
from app.domains.audit.ai import (
    persist_failed_ai_operation_audits,
    record_ai_audit,
    record_ai_operation_audits,
    sanitize_ai_error,
)
from app.domains.imports.models import ImportConflict, ImportJob, ImportStagingAsset, ImportValidationError
from app.domains.imports.schemas import (
    ImportAiAnalysis,
    ImportApplyResponse,
    ImportConflictRead,
    ImportCorrection,
    ImportJobRead,
    ImportMappingUpdate,
    ImportPreview,
    ImportStagingAssetRead,
    ImportValidationErrorRead,
)
from app.domains.imports.service import ImportService
from app.domains.users.models import User
from app.services.import_ai_analysis import (
    ImportAiAnalysisError,
    analyze_import,
    decide_ai_suggestion,
    list_ai_suggestions,
    persist_ai_suggestions,
)
from app.shared.audit_context import build_audit_context
from app.shared.enums import AiCapability, Role
from app.shared.pagination import Page, PageParams
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/imports", tags=["Imports"])



async def _get_import_or_404(import_id: UUID, session: AsyncSession) -> ImportJob:
    job = await session.scalar(select(ImportJob).where(ImportJob.id == import_id, ImportJob.deleted_at.is_(None)))
    if job is None:
        raise HTTPException(status_code=404, detail="import_not_found")
    return job


@router.post("/{import_id}/ai-analysis", response_model=ImportAiAnalysis)
async def analyze_import_with_hermes(
    import_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_ai_capability(AiCapability.AI_IMPORT_ANALYSIS)),
):
    ensure_ai_enabled(settings)
    started = time.perf_counter()
    primitive_import_id = import_id
    job = await _get_import_or_404(import_id, session)
    job_id = job.id
    user_id = current_user.id
    user_role = current_user.role
    result = await session.execute(
        select(ImportStagingAsset)
        .where(ImportStagingAsset.job_id == primitive_import_id, ImportStagingAsset.deleted_at.is_(None))
        .order_by(ImportStagingAsset.row_number)
    )
    try:
        async def operation() -> ImportAiAnalysis:
            analysis = await analyze_import(job, list(result.scalars()))
            analysis.ai_suggestions = await persist_ai_suggestions(job, analysis, session, current_user.id)
            diagnostics = analysis.diagnostics
            await record_ai_operation_audits(
                session,
                event="IMPORT_ANALYSIS",
                user=current_user,
                provider=diagnostics.provider if diagnostics else "hermes",
                model=diagnostics.model if diagnostics else settings.hermes_model or "hermes-agent",
                resource_type="ImportJob",
                resource_id=job_id,
                status="SUCCESS",
                duration_ms=round((time.perf_counter() - started) * 1000),
            )
            return analysis

        return await commit_or_rollback(session, operation)
    except (AiProviderConfigurationError, AiProviderRequestError, ImportAiAnalysisError) as exc:
        await persist_failed_ai_operation_audits(
            event="IMPORT_ANALYSIS",
            user_id=user_id,
            user_role=user_role,
            provider="hermes",
            model=settings.hermes_model or "hermes-agent",
            resource_type="ImportJob",
            resource_id=job_id,
            duration_ms=round((time.perf_counter() - started) * 1000),
            error=exc,
        )
        code = sanitize_ai_error(exc) or "ai_operation_failed"
        http_status = 503 if isinstance(exc, AiProviderConfigurationError) else 502
        raise HTTPException(status_code=http_status, detail=code) from exc


@router.get("/{import_id}/ai-suggestions", response_model=list[ImportCorrection])
async def get_import_ai_suggestions(
    import_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[ImportCorrection]:
    return list_ai_suggestions(await _get_import_or_404(import_id, session))


async def _decide_import_ai_suggestion(
    import_id: UUID,
    suggestion_id: UUID,
    decision: Literal["APPROVED", "REJECTED"],
    session: AsyncSession,
    current_user: User,
) -> ImportCorrection:
    job = await _get_import_or_404(import_id, session)

    async def operation() -> ImportCorrection:
        suggestion = await decide_ai_suggestion(job, suggestion_id, decision, session, current_user.id)
        await record_ai_audit(
            session,
            event="AI_APPROVAL" if decision == "APPROVED" else "AI_REJECTION",
            user=current_user,
            provider="hermes",
            model=settings.hermes_model or "hermes-agent",
            resource_type="ImportAiSuggestion",
            resource_id=suggestion_id,
            status="SUCCESS",
            duration_ms=0,
        )
        return suggestion

    try:
        return await commit_or_rollback(session, operation)
    except ValueError as exc:
        code = str(exc)
        raise HTTPException(status_code=404 if code == "suggestion_not_found" else 409, detail=code) from exc


@router.post("/{import_id}/ai-suggestions/{suggestion_id}/approve", response_model=ImportCorrection)
async def approve_import_ai_suggestion(
    import_id: UUID,
    suggestion_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportCorrection:
    return await _decide_import_ai_suggestion(import_id, suggestion_id, "APPROVED", session, current_user)


@router.post("/{import_id}/ai-suggestions/{suggestion_id}/reject", response_model=ImportCorrection)
async def reject_import_ai_suggestion(
    import_id: UUID,
    suggestion_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportCorrection:
    return await _decide_import_ai_suggestion(import_id, suggestion_id, "REJECTED", session, current_user)


@router.post("/lansweeper", response_model=ImportJobRead, status_code=status.HTTP_201_CREATED)
async def import_lansweeper(
    request: Request,
    file: UploadFile = File(...),
    import_mode: str = Form("INITIAL_LOAD"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportJob:
    try:
        async def operation() -> ImportJob:
            return await ImportService(session).upload_spreadsheet(file, current_user.id, build_audit_context(request, current_user.id), source="LANSWEEPER", import_mode=import_mode)

        return await commit_or_rollback(session, operation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/spreadsheet/upload", response_model=ImportJobRead, status_code=status.HTTP_201_CREATED)
async def upload_spreadsheet(
    request: Request,
    file: UploadFile = File(...),
    import_mode: str = Form("INITIAL_LOAD"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportJob:
    try:
        async def operation() -> ImportJob:
            return await ImportService(session).upload_spreadsheet(file, current_user.id, build_audit_context(request, current_user.id), import_mode=import_mode)

        return await commit_or_rollback(session, operation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=Page[ImportJobRead])
async def list_imports(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Page[ImportJob]:
    params = PageParams(page=page, page_size=page_size)
    total = await session.scalar(select(func.count()).select_from(ImportJob).where(ImportJob.deleted_at.is_(None)))
    result = await session.execute(select(ImportJob).where(ImportJob.deleted_at.is_(None)).order_by(ImportJob.created_at.desc()).offset(params.offset).limit(params.page_size))
    return Page(items=list(result.scalars()), total=total or 0, page=page, page_size=page_size)


@router.get("/{import_id}", response_model=ImportJobRead)
async def get_import(import_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> ImportJob:
    return await _get_import_or_404(import_id, session)


@router.get("/{import_id}/preview", response_model=ImportPreview)
async def get_import_preview(
    import_id: UUID,
    limit: int = Query(20, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ImportPreview:
    job = await _get_import_or_404(import_id, session)
    result = await session.execute(
        select(ImportStagingAsset)
        .where(ImportStagingAsset.job_id == import_id, ImportStagingAsset.deleted_at.is_(None))
        .order_by(ImportStagingAsset.row_number)
        .limit(limit)
    )
    items = list(result.scalars())
    return ImportPreview(
        job=job,
        columns=list(job.report.get("columns", [])),
        detected_mapping=dict(job.report.get("detected_mapping", {})),
        items=items,
    )


@router.get("/{import_id}/staging", response_model=Page[ImportStagingAssetRead])
async def get_import_staging(
    import_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    decision: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> Page[ImportStagingAssetRead]:
    params = PageParams(page=page, page_size=page_size)
    filters = [ImportStagingAsset.job_id == import_id, ImportStagingAsset.deleted_at.is_(None)]
    if decision:
        filters.append(ImportStagingAsset.decision == decision)
    total = await session.scalar(select(func.count()).select_from(ImportStagingAsset).where(*filters))
    result = await session.execute(
        select(ImportStagingAsset)
        .where(*filters)
        .order_by(ImportStagingAsset.row_number)
        .offset(params.offset)
        .limit(params.page_size)
    )
    items = [ImportStagingAssetRead.model_validate(row) for row in result.scalars()]
    return Page(items=items, total=total or 0, page=page, page_size=page_size)


@router.get("/{import_id}/conflicts", response_model=list[ImportConflictRead])
async def get_import_conflicts(import_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> list[ImportConflict]:
    result = await session.execute(
        select(ImportConflict)
        .where(ImportConflict.job_id == import_id, ImportConflict.deleted_at.is_(None))
        .order_by(ImportConflict.created_at.desc())
    )
    return list(result.scalars())


@router.get("/{import_id}/validation-errors", response_model=list[ImportValidationErrorRead])
async def get_import_validation_errors(
    import_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[ImportValidationError]:
    result = await session.execute(
        select(ImportValidationError)
        .where(ImportValidationError.job_id == import_id, ImportValidationError.deleted_at.is_(None))
        .order_by(ImportValidationError.row_number)
    )
    return list(result.scalars())


@router.post("/{import_id}/mapping", response_model=ImportJobRead)
async def update_import_mapping(
    import_id: UUID,
    payload: ImportMappingUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportJob:
    job = await _get_import_or_404(import_id, session)

    async def operation() -> ImportJob:
        return await ImportService(session).update_mapping(job, payload.mapping, current_user.id, build_audit_context(request, current_user.id), payload.import_mode)

    return await commit_or_rollback(session, operation)


@router.post("/{import_id}/apply", response_model=ImportApplyResponse)
async def apply_import(
    import_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportApplyResponse:
    job = await _get_import_or_404(import_id, session)
    try:
        async def operation() -> ImportJob:
            return await ImportService(session).apply_import(job, current_user.id, build_audit_context(request, current_user.id))

        applied = await commit_or_rollback(session, operation)
        return ImportApplyResponse(job=applied, report=applied.report)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{import_id}/cancel", response_model=ImportJobRead)
async def cancel_import(
    import_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
) -> ImportJob:
    job = await _get_import_or_404(import_id, session)
    try:
        async def operation() -> ImportJob:
            return await ImportService(session).cancel_import(job, current_user.id, build_audit_context(request, current_user.id))

        return await commit_or_rollback(session, operation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{import_id}/report")
async def get_import_report(import_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> dict:
    job = await _get_import_or_404(import_id, session)
    return {"import_id": str(job.id), "status": job.status, "report": job.report}
