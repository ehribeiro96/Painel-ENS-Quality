from __future__ import annotations

from uuid import UUID

from app.api.v1.dependencies.auth import get_current_user, require_role
from app.core.database.session import get_session
from app.domains.macros.models import MacroGeneration
from app.domains.macros.renderer import MacroRenderError, render_macro
from app.domains.macros.schemas import (
    MacroAutocompleteHintRead,
    MacroGenerateRequest,
    MacroGenerationRead,
    MacroRenderRequest,
    MacroRenderResponse,
    MacroTemplateCreate,
    MacroTemplateRead,
    MacroTemplateUpdate,
    SuggestedMovementMacro,
)
from app.domains.macros.service import MacroService
from app.domains.users.models import User
from app.shared.audit_context import build_audit_context
from app.shared.enums import Role
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/macros", tags=["Macros"])
movements_router = APIRouter(prefix="/movements", tags=["Macros"])


@router.get("/templates", response_model=list[MacroTemplateRead])
async def list_templates(
    search: str | None = None,
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await MacroService(session).repository.list_templates(search, category)


@router.get("/templates/{template_id}", response_model=MacroTemplateRead)
async def get_template(template_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)):
    template = await MacroService(session).repository.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="macro_template_not_found")
    return template


@router.post("/templates", response_model=MacroTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: MacroTemplateCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
):
    service = MacroService(session)

    async def operation():
        return await service.create_template(payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.put("/templates/{template_id}", response_model=MacroTemplateRead)
async def update_template(
    template_id: UUID,
    payload: MacroTemplateUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
):
    service = MacroService(session)
    template = await service.repository.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="macro_template_not_found")

    async def operation():
        return await service.update_template(template, payload, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.post("/render", response_model=MacroRenderResponse)
async def render_template(
    payload: MacroRenderRequest,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    try:
        if payload.template_id:
            template = await MacroService(session).repository.get_template(payload.template_id)
            if template is None:
                raise HTTPException(status_code=404, detail="macro_template_not_found")
            rendered, pending = render_macro(template.template_text, payload.values, payload.required_fields or template.required_fields)
        elif payload.template_text:
            rendered, pending = render_macro(payload.template_text, payload.values, payload.required_fields)
        else:
            raise HTTPException(status_code=422, detail="template_id_or_template_text_required")
    except MacroRenderError as exc:
        raise HTTPException(status_code=422, detail={"code": str(exc), "missing_fields": exc.missing_fields}) from exc
    return MacroRenderResponse(rendered_text=rendered, pending_fields=pending)


@router.post("/generate", response_model=MacroGenerationRead, status_code=status.HTTP_201_CREATED)
async def generate_macro(
    payload: MacroGenerateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
):
    service = MacroService(session)
    template = await service.repository.get_template(payload.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="macro_template_not_found")

    async def operation():
        try:
            return await service.generate(
                template,
                payload.values,
                current_user.id,
                payload.context_type,
                payload.context_id,
                payload.ticket_number,
                build_audit_context(request, current_user.id),
            )
        except MacroRenderError as exc:
            raise HTTPException(status_code=422, detail={"code": str(exc), "missing_fields": exc.missing_fields}) from exc

    return await commit_or_rollback(session, operation)


@router.get("/generations", response_model=list[MacroGenerationRead])
async def list_generations(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    result = await session.execute(select(MacroGeneration).order_by(MacroGeneration.created_at.desc()).limit(50))
    return list(result.scalars())


@router.post("/generations/{generation_id}/copied", response_model=MacroGenerationRead)
async def mark_generation_copied(
    generation_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
):
    generation = await session.scalar(select(MacroGeneration).where(MacroGeneration.id == generation_id))
    if generation is None:
        raise HTTPException(status_code=404, detail="macro_generation_not_found")

    async def operation():
        return await MacroService(session).mark_copied(generation, current_user.id, build_audit_context(request, current_user.id))

    return await commit_or_rollback(session, operation)


@router.get("/autocomplete", response_model=list[MacroAutocompleteHintRead])
async def autocomplete(
    q: str = Query("", max_length=120),
    hint_type: str | None = Query(default=None, max_length=80),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await MacroService(session).repository.autocomplete(q, hint_type)


@movements_router.get("/{movement_id}/suggested-macro", response_model=SuggestedMovementMacro)
async def suggested_movement_macro(
    movement_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(Role.ADMIN, Role.TECHNICIAN)),
):
    async def operation():
        try:
            return await MacroService(session).generate_for_movement(
                movement_id,
                current_user.id,
                build_audit_context(request, current_user.id),
            )
        except LookupError as exc:
            raise HTTPException(status_code=404, detail="movement_not_found") from exc

    generation, template, values, pending = await commit_or_rollback(session, operation)
    return SuggestedMovementMacro(
        movement_id=movement_id,
        generation_id=generation.id if generation else None,
        template_id=template.id if template else None,
        template_name=template.name if template else None,
        rendered_text=generation.rendered_text if generation else "",
        pending_fields=pending,
        values=values,
    )
