from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.api.v1.dependencies.auth import get_current_user, get_optional_current_user
from app.core.config.settings import settings
from app.core.database.session import get_session
from app.domains.artifacts.schemas import (
    ArtifactCreateResponse,
    ArtifactDeleteResponse,
    ArtifactDownloadUrlResponse,
    ArtifactListResponse,
)
from app.domains.audit.service import AuditService
from app.domains.users.models import User
from app.services.artifact_signing import ArtifactSigner, ArtifactTokenError
from app.services.artifact_storage import (
    ArtifactForbiddenError,
    ArtifactNotFoundError,
    ArtifactStorage,
    ArtifactStorageError,
)
from app.shared.audit_context import build_audit_context
from app.shared.enums import AuditAction, Role
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/artifacts', tags=['Artifacts'])


def get_artifact_storage() -> ArtifactStorage:
    return ArtifactStorage()


def get_artifact_signer() -> ArtifactSigner:
    return ArtifactSigner(settings.jwt_secret_key, api_prefix=settings.api_prefix)


def _raise_storage_error(exc: ArtifactStorageError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.code) from exc


def _artifact_read(record) -> ArtifactCreateResponse:
    return ArtifactCreateResponse.model_validate(record.to_read().model_dump())


def _is_admin(user: User) -> bool:
    return user.role == Role.ADMIN


def _artifact_headers(filename: str) -> dict[str, str]:
    safe_ascii = ArtifactStorage.default_display_name(filename)
    return {
        'Content-Disposition': f'attachment; filename="{safe_ascii}"',
        'Cache-Control': 'private, no-store',
    }


@router.post('', response_model=ArtifactCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    storage: ArtifactStorage = Depends(get_artifact_storage),
) -> ArtifactCreateResponse:
    created_record = None
    try:
        async def operation() -> ArtifactCreateResponse:
            nonlocal created_record
            created_record = await storage.save_artifact(file, current_user.id)
            await AuditService(session).record(
                action=AuditAction.CREATE,
                entity='Artifact',
                entity_id=created_record.id,
                actor_id=current_user.id,
                after=created_record.model_dump(mode='json'),
                context=build_audit_context(request, current_user.id),
            )
            return _artifact_read(created_record)

        return await commit_or_rollback(session, operation)
    except ArtifactStorageError as exc:
        await session.rollback()
        if created_record is not None:
            try:
                await storage.delete_artifact(created_record.id, current_user.id, allow_all=True)
            except Exception:
                pass
        _raise_storage_error(exc)
    except Exception:
        await session.rollback()
        if created_record is not None:
            try:
                await storage.delete_artifact(created_record.id, current_user.id, allow_all=True)
            except Exception:
                pass
        raise

@router.get('', response_model=ArtifactListResponse)
async def list_artifacts(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    storage: ArtifactStorage = Depends(get_artifact_storage),
) -> ArtifactListResponse:
    records = await storage.list_artifacts(current_user.id, allow_all=_is_admin(current_user))
    items = [record.to_read() for record in records]
    return ArtifactListResponse(items=items, total=len(items))

@router.get('/download/{signed_token}')
async def download_artifact(
    signed_token: str,
    storage: ArtifactStorage = Depends(get_artifact_storage),
    signer: ArtifactSigner = Depends(get_artifact_signer),
    current_user: User | None = Depends(get_optional_current_user),
) -> StreamingResponse:
    try:
        claims = signer.verify_download_token(signed_token)
        record = await storage.get_artifact_for_token(claims.artifact_id)
        if record.owner_user_id != claims.owner_user_id:
            raise ArtifactForbiddenError()
        if current_user is not None and not _is_admin(current_user) and current_user.id != record.owner_user_id:
            raise ArtifactForbiddenError()
        blob_path = storage.private_root / record.storage_name
        if not blob_path.is_file():
            raise ArtifactNotFoundError('artifact_blob_missing', 'artifact_blob_missing')
        await storage.mark_downloaded(record.id)
        response = StreamingResponse(blob_path.open('rb'), media_type=record.content_type)
        response.headers.update(_artifact_headers(record.filename))
        return response
    except ArtifactStorageError as exc:
        _raise_storage_error(exc)
    except ArtifactTokenError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.code) from exc

@router.get('/{artifact_id}', response_model=ArtifactCreateResponse)
async def get_artifact(
    artifact_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    storage: ArtifactStorage = Depends(get_artifact_storage),
) -> ArtifactCreateResponse:
    try:
        record = await storage.get_artifact(artifact_id, current_user.id, allow_all=_is_admin(current_user))
        return _artifact_read(record)
    except ArtifactStorageError as exc:
        _raise_storage_error(exc)

@router.get('/{artifact_id}/download-url', response_model=ArtifactDownloadUrlResponse)
async def get_download_url(
    artifact_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    storage: ArtifactStorage = Depends(get_artifact_storage),
    signer: ArtifactSigner = Depends(get_artifact_signer),
) -> ArtifactDownloadUrlResponse:
    try:
        record = await storage.get_artifact(artifact_id, current_user.id, allow_all=_is_admin(current_user))
        expires_at = datetime.now(UTC) + timedelta(seconds=300)
        token = signer.sign_download_token(record.id, record.owner_user_id, expires_at)
        await AuditService(session).record(
            action=AuditAction.SIGNATURE_GENERATE,
            entity='Artifact',
            entity_id=record.id,
            actor_id=current_user.id,
            after={'artifact_id': str(record.id), 'expires_at': expires_at.isoformat()},
            context=build_audit_context(request, current_user.id),
        )
        await session.commit()
        return ArtifactDownloadUrlResponse(artifact_id=record.id, url=signer.build_download_url(token), expires_at=expires_at)
    except ArtifactStorageError as exc:
        await session.rollback()
        _raise_storage_error(exc)
    except Exception:
        await session.rollback()
        raise

@router.delete('/{artifact_id}', response_model=ArtifactDeleteResponse)
async def delete_artifact(
    artifact_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    storage: ArtifactStorage = Depends(get_artifact_storage),
) -> ArtifactDeleteResponse:
    try:
        async def operation() -> ArtifactDeleteResponse:
            record = await storage.delete_artifact(artifact_id, current_user.id, allow_all=_is_admin(current_user))
            await AuditService(session).record(
                action=AuditAction.DELETE,
                entity='Artifact',
                entity_id=record.id,
                actor_id=current_user.id,
                before={'deleted_at': None},
                after={'deleted_at': record.deleted_at.isoformat() if record.deleted_at else None},
                context=build_audit_context(request, current_user.id),
            )
            return ArtifactDeleteResponse(artifact_id=record.id, deleted_at=record.deleted_at or datetime.now(UTC))

        return await commit_or_rollback(session, operation)
    except ArtifactStorageError as exc:
        await session.rollback()
        _raise_storage_error(exc)
