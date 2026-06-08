from __future__ import annotations

from uuid import UUID

from app.api.v1.dependencies.auth import get_current_user
from app.core.database.session import get_session
from app.domains.audit.service import AuditService
from app.domains.signatures.service import SignatureService
from app.domains.users.models import User
from app.domains.users.service import UserService
from app.shared.audit_context import build_audit_context
from app.shared.enums import AuditAction
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/signatures", tags=["Signatures"])


@router.get("/{user_id}", response_class=HTMLResponse)
async def preview_signature(user_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> str:
    user = await UserService(session).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return SignatureService().render_html(user)


@router.post("/generate/{user_id}", response_class=HTMLResponse)
async def generate_signature(
    user_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> str:
    user = await UserService(session).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    html = SignatureService().render_html(user)
    async def operation() -> None:
        await AuditService(session).record(
            action=AuditAction.SIGNATURE_GENERATE,
            entity="User",
            entity_id=user.id,
            actor_id=current_user.id,
            after={"generated_for": str(user.id), "email": user.email},
            context=build_audit_context(request, current_user.id),
        )

    await commit_or_rollback(session, operation)
    return html


@router.get("/{user_id}/download-html", response_class=HTMLResponse)
async def download_signature(user_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> HTMLResponse:
    user = await UserService(session).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return HTMLResponse(
        SignatureService().render_html(user),
        headers={"Content-Disposition": f'attachment; filename="assinatura-{user.email}.html"'},
    )
