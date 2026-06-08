from __future__ import annotations

import re
import unicodedata
from uuid import UUID

from app.domains.macros.models import MacroAutocompleteHint, MacroTemplate
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


def normalize_query(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", normalized.lower()).strip()


class MacroRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_templates(self, search: str | None = None, category: str | None = None) -> list[MacroTemplate]:
        filters = [MacroTemplate.deleted_at.is_(None), MacroTemplate.is_active.is_(True)]
        if category:
            filters.append(MacroTemplate.category.ilike(f"%{category}%"))
        if search:
            term = f"%{search}%"
            filters.append(or_(MacroTemplate.name.ilike(term), MacroTemplate.category.ilike(term), MacroTemplate.slug.ilike(term)))
        result = await self.session.execute(select(MacroTemplate).where(*filters).order_by(MacroTemplate.category, MacroTemplate.name))
        return list(result.scalars())

    async def get_template(self, template_id: UUID) -> MacroTemplate | None:
        return await self.session.scalar(
            select(MacroTemplate).where(MacroTemplate.id == template_id, MacroTemplate.deleted_at.is_(None))
        )

    async def get_template_by_slug(self, slug: str) -> MacroTemplate | None:
        return await self.session.scalar(
            select(MacroTemplate).where(MacroTemplate.slug == slug, MacroTemplate.deleted_at.is_(None))
        )

    async def autocomplete(self, query: str, hint_type: str | None = None, limit: int = 20) -> list[MacroAutocompleteHint]:
        filters = [MacroAutocompleteHint.is_active.is_(True)]
        if hint_type:
            filters.append(MacroAutocompleteHint.hint_type == hint_type)
        if query:
            filters.append(MacroAutocompleteHint.normalized_label.ilike(f"%{normalize_query(query)}%"))
        result = await self.session.execute(
            select(MacroAutocompleteHint).where(*filters).order_by(MacroAutocompleteHint.label).limit(limit)
        )
        return list(result.scalars())
