from __future__ import annotations

from app.api.v1.dependencies.auth import get_current_user, require_role
from app.domains.rag.schemas import (
    RagAuditRecentResponse,
    RagCollectionDTO,
    RagCourseContextDTO,
    RagDocumentDTO,
    RagSearchRequest,
    RagSearchResponse,
)
from app.domains.users.models import User
from app.services import rag_mcp_mock
from app.shared.enums import Role
from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(prefix="/rag", tags=["RAG"])


def _raise_mock_error(exc: rag_mcp_mock.RagMockError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.code) from exc


@router.get("/collections", response_model=list[RagCollectionDTO])
async def list_collections(current_user: User = Depends(get_current_user)) -> list[RagCollectionDTO]:  # noqa: ARG001
    return rag_mcp_mock.list_collections()


@router.post("/search", response_model=RagSearchResponse)
async def search(payload: RagSearchRequest, current_user: User = Depends(get_current_user)) -> RagSearchResponse:  # noqa: ARG001
    try:
        return rag_mcp_mock.search(payload.query, payload.collections, payload.limit)
    except rag_mcp_mock.RagMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError("unreachable")


@router.get("/documents/{document_id}", response_model=RagDocumentDTO)
async def get_document(document_id: str, current_user: User = Depends(get_current_user)) -> RagDocumentDTO:  # noqa: ARG001
    try:
        return rag_mcp_mock.get_document(document_id)
    except rag_mcp_mock.RagMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError("unreachable")


@router.get("/course-context/{course_id}", response_model=RagCourseContextDTO)
async def get_course_context(course_id: str, current_user: User = Depends(get_current_user)) -> RagCourseContextDTO:  # noqa: ARG001
    try:
        return rag_mcp_mock.get_course_context(course_id)
    except rag_mcp_mock.RagMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError("unreachable")


@router.get("/audit/recent", response_model=RagAuditRecentResponse)
async def audit_recent(
    limit: int = Query(default=50, ge=1, le=50),
    current_user: User = Depends(require_role(Role.ADMIN, Role.MANAGER)),
) -> RagAuditRecentResponse:
    try:
        return rag_mcp_mock.audit_recent(limit)
    except rag_mcp_mock.RagMockError as exc:
        _raise_mock_error(exc)
    raise AssertionError("unreachable")
