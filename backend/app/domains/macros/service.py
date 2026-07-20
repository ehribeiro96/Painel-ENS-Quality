from __future__ import annotations

import re
import unicodedata
from uuid import UUID

from app.domains.assets.models import Asset
from app.domains.audit.service import AuditService
from app.domains.macros.models import MacroGeneration, MacroTemplate
from app.domains.macros.renderer import MacroRenderError, extract_placeholders, render_macro
from app.domains.macros.repository import MacroRepository
from app.domains.macros.schemas import MacroTemplateCreate, MacroTemplateUpdate
from app.domains.movements.models import AssetMovement
from app.domains.users.models import User
from app.shared.audit_context import AuditContext
from app.shared.enums import AuditAction
from app.shared.models import utc_now
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


def normalize_label(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", normalized.lower()).strip()


def slugify(value: str) -> str:
    text = normalize_label(value)
    text = re.sub(r"^\[(.*?)\]\s*", r"\1-", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "macro"


def category_from_name(value: str) -> str:
    match = re.match(r"^\[(?P<category>[^\]]+)\]", value.strip())
    return match.group("category") if match else "Geral"


class MacroService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = MacroRepository(session)

    async def create_template(
        self,
        payload: MacroTemplateCreate,
        actor_id: UUID | None,
        audit_context: AuditContext | None = None,
    ) -> MacroTemplate:
        slug = payload.slug or slugify(payload.name)
        template = MacroTemplate(**payload.model_dump(exclude={"slug"}), slug=slug, created_by=actor_id, updated_by=actor_id)
        if not template.required_fields:
            template.required_fields = extract_placeholders(template.template_text)
        self.session.add(template)
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.CREATE,
            entity="MacroTemplate",
            entity_id=template.id,
            actor_id=actor_id,
            after={"slug": template.slug, "source": template.source},
            context=audit_context,
        )
        return template

    async def update_template(
        self,
        template: MacroTemplate,
        payload: MacroTemplateUpdate,
        actor_id: UUID | None,
        audit_context: AuditContext | None = None,
    ) -> MacroTemplate:
        before = {"slug": template.slug, "version": template.version, "is_active": template.is_active}
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(template, key, value)
        if payload.template_text is not None and payload.required_fields is None:
            template.required_fields = extract_placeholders(template.template_text)
        template.updated_by = actor_id
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.UPDATE,
            entity="MacroTemplate",
            entity_id=template.id,
            actor_id=actor_id,
            before=before,
            after={"slug": template.slug, "version": template.version, "is_active": template.is_active},
            context=audit_context,
        )
        return template

    async def render_template(self, template: MacroTemplate, values: dict[str, object]) -> tuple[str, list[str]]:
        return render_macro(template.template_text, values, template.required_fields)

    async def generate(
        self,
        template: MacroTemplate,
        values: dict[str, object],
        actor_id: UUID | None,
        context_type: str | None = None,
        context_id: UUID | None = None,
        ticket_number: str | None = None,
        audit_context: AuditContext | None = None,
        allow_pending: bool = False,
        required_fields: list[str] | None = None,
        audit_event: str = "macro_generated",
    ) -> MacroGeneration:
        rendered, pending = render_macro(template.template_text, values, required_fields if required_fields is not None else template.required_fields)
        if pending and not allow_pending:
            raise MacroRenderError("missing_optional_fields", pending)
        stored_values = dict(values)
        if pending:
            stored_values["_metadata"] = {"pending_fields": pending}
        generation = MacroGeneration(
            template_id=template.id,
            context_type=context_type,
            context_id=context_id,
            rendered_text=rendered,
            input_values=stored_values,
            generated_by=actor_id,
            ticket_number=ticket_number,
            created_by=actor_id,
            updated_by=actor_id,
        )
        self.session.add(generation)
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.CREATE,
            entity="MacroGeneration",
            entity_id=generation.id,
            actor_id=actor_id,
            after={
                "event": audit_event,
                "template_id": str(template.id),
                "context_type": context_type,
                "context_id": str(context_id) if context_id else None,
                "pending_fields": pending,
            },
            source="macros",
            context=audit_context,
        )
        return generation

    async def mark_copied(
        self,
        generation: MacroGeneration,
        actor_id: UUID | None = None,
        audit_context: AuditContext | None = None,
    ) -> MacroGeneration:
        generation.copied = True
        generation.copied_at = utc_now()
        await self.session.flush()
        await AuditService(self.session).record(
            action=AuditAction.UPDATE,
            entity="MacroGeneration",
            entity_id=generation.id,
            actor_id=actor_id,
            after={
                "event": "macro_copied",
                "template_id": str(generation.template_id),
                "context_type": generation.context_type,
                "context_id": str(generation.context_id) if generation.context_id else None,
                "copied": True,
            },
            source="macros",
            context=audit_context,
        )
        return generation

    async def suggested_for_movement(self, movement_id: UUID) -> tuple[MacroTemplate | None, dict[str, object], str, list[str]]:
        movement = await self.session.scalar(select(AssetMovement).where(AssetMovement.id == movement_id))
        if movement is None:
            raise LookupError("movement_not_found")
        asset = await self.session.scalar(select(Asset).where(Asset.id == movement.asset_id))
        previous_user = await self.session.scalar(select(User).where(User.id == movement.previous_user_id)) if movement.previous_user_id else None
        new_user = await self.session.scalar(select(User).where(User.id == movement.new_user_id)) if movement.new_user_id else None
        template = await self.repository.get_template_by_slug("ativos-atualizar-inventario")
        values = {
            "Patrimônio": asset.patrimony if asset else None,
            "Unidade": asset.location if asset else None,
            "Equipamento": " ".join(
                item
                for item in [
                    asset.hostname if asset else None,
                    asset.asset_type.value if asset else None,
                    asset.manufacturer if asset else None,
                    asset.model if asset else None,
                ]
                if item
            ),
            "Usuário Anterior": previous_user.name if previous_user else None,
            "Local de": movement.previous_location,
            "Usuário Atual": new_user.name if new_user else None,
            "Local para": movement.new_location,
            "Status": movement.new_status.value,
        }
        if template is None:
            return None, values, "", sorted(key for key, value in values.items() if not value)
        rendered, pending = render_macro(template.template_text, values, [])
        return template, values, rendered, pending

    async def generate_for_movement(
        self,
        movement_id: UUID,
        actor_id: UUID | None,
        audit_context: AuditContext | None = None,
    ) -> tuple[MacroGeneration | None, MacroTemplate | None, dict[str, object], list[str]]:
        existing = await self.session.scalar(
            select(MacroGeneration).where(
                MacroGeneration.context_type == "asset_movement",
                MacroGeneration.context_id == movement_id,
            )
        )
        if existing:
            template = await self.repository.get_template(existing.template_id)
            return existing, template, existing.input_values, []

        template, values, _rendered, pending = await self.suggested_for_movement(movement_id)
        if template is None:
            return None, None, values, pending
        try:
            async with self.session.begin_nested():
                generation = await self.generate(
                    template,
                    values,
                    actor_id,
                    context_type="asset_movement",
                    context_id=movement_id,
                    audit_context=audit_context,
                    allow_pending=True,
                    required_fields=[],
                    audit_event="asset_movement_macro_generated",
                )
        except IntegrityError:
            generation = await self.session.scalar(
                select(MacroGeneration).where(
                    MacroGeneration.context_type == "asset_movement",
                    MacroGeneration.context_id == movement_id,
                )
            )
            if generation is None:
                raise
            existing_template = await self.repository.get_template(generation.template_id)
            return generation, existing_template, generation.input_values, []
        await AuditService(self.session).record(
            action=AuditAction.CREATE,
            entity="AssetMovement",
            entity_id=movement_id,
            actor_id=actor_id,
            after={
                "event": "asset_movement_macro_generated",
                "macro_generation_id": str(generation.id),
                "template_id": str(template.id),
                "pending_fields": pending,
            },
            source="macros",
            context=audit_context,
        )
        return generation, template, values, pending
