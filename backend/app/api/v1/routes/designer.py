from __future__ import annotations

from app.api.v1.dependencies.auth import get_current_user, require_role
from app.domains.designer.schemas import (
    DesignerAdjustItemRequest,
    DesignerBannerJsonRequest,
    DesignerCancelResponse,
    DesignerFormOptionsResponse,
    DesignerHealthDTO,
    DesignerJobDTO,
    DesignerRefreshUrlRequest,
    DesignerTemplatesResponse,
)
from app.domains.users.models import User
from app.services import designer_mock
from app.shared.enums import Role
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix='/designer', tags=['designer'])


def _raise_mock_error(exc: designer_mock.DesignerMockError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.error.model_dump()) from exc


@router.get('/health', response_model=DesignerHealthDTO)
async def health(current_user: User = Depends(get_current_user)) -> DesignerHealthDTO:  # noqa: ARG001
    return designer_mock.health()


@router.get('/templates', response_model=DesignerTemplatesResponse)
async def templates(current_user: User = Depends(get_current_user)) -> DesignerTemplatesResponse:  # noqa: ARG001
    return designer_mock.list_templates()


@router.get('/form-options', response_model=DesignerFormOptionsResponse)
async def form_options(current_user: User = Depends(get_current_user)) -> DesignerFormOptionsResponse:  # noqa: ARG001
    return designer_mock.form_options()


@router.post('/banners/json', response_model=DesignerJobDTO)
async def create_banner_json(
    payload: DesignerBannerJsonRequest,
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER)),
) -> DesignerJobDTO:
    try:
        return designer_mock.create_banner_job(payload, current_user.id)
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')


@router.get('/jobs/{job_id}', response_model=DesignerJobDTO)
async def get_job(job_id: str, current_user: User = Depends(get_current_user)) -> DesignerJobDTO:
    try:
        return designer_mock.get_job(job_id, current_user)
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')


@router.post('/jobs/{job_id}/items/{item_id}/adjust', response_model=DesignerJobDTO)
async def adjust_item(
    job_id: str,
    item_id: str,
    payload: DesignerAdjustItemRequest,
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER)),
) -> DesignerJobDTO:
    try:
        return designer_mock.adjust_item(job_id, item_id, payload, current_user)
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')


@router.post('/jobs/{job_id}/items/{item_id}/refresh-url', response_model=DesignerJobDTO)
async def refresh_item_url(
    job_id: str,
    item_id: str,
    payload: DesignerRefreshUrlRequest,
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER)),
) -> DesignerJobDTO:
    try:
        return designer_mock.refresh_item_url(job_id, item_id, payload, current_user)
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')


@router.post('/jobs/{job_id}/cancel', response_model=DesignerCancelResponse)
async def cancel_job(job_id: str, current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER))) -> DesignerCancelResponse:
    try:
        return designer_mock.cancel_job(job_id, current_user)
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')


@router.post('/banners')
async def blocked_banner_upload(current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER))) -> None:  # noqa: ARG001
    try:
        designer_mock.block_banner_upload()
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')


@router.get('/jobs/{job_id}/download-url')
async def blocked_download_url(job_id: str, current_user: User = Depends(get_current_user)) -> None:  # noqa: ARG001
    try:
        designer_mock.block_download_url(job_id)
    except designer_mock.DesignerMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError('unreachable')
