from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta
from uuid import UUID

from app.core.config.settings import settings
from app.domains.auth.models import AuthSession
from app.shared.models import utc_now
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthSessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self,
        *,
        user_id: UUID,
        user_agent: str | None,
        ip_address: str | None,
        actor_id: UUID | None = None,
    ) -> tuple[AuthSession, str]:
        refresh_token = create_refresh_token()
        now = utc_now()
        auth_session = AuthSession(
            user_id=user_id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            expires_at=now + timedelta(days=settings.refresh_token_days),
            user_agent=user_agent[:500] if user_agent else None,
            ip_address=ip_address,
            last_used_at=now,
            created_by=actor_id or user_id,
            updated_by=actor_id or user_id,
        )
        self.session.add(auth_session)
        await self.session.flush()
        return auth_session, refresh_token

    async def get_active_by_refresh_token(self, refresh_token: str) -> AuthSession | None:
        now = utc_now()
        return await self.session.scalar(
            select(AuthSession).where(
                AuthSession.refresh_token_hash == hash_refresh_token(refresh_token),
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > now,
                AuthSession.deleted_at.is_(None),
            )
        )

    async def rotate(
        self,
        *,
        auth_session: AuthSession,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[AuthSession, str]:
        now = utc_now()
        new_session, refresh_token = await self.create_session(
            user_id=auth_session.user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            actor_id=auth_session.user_id,
        )
        auth_session.revoked_at = now
        auth_session.last_used_at = now
        auth_session.replaced_by_session_id = new_session.id
        auth_session.updated_by = auth_session.user_id
        await self.session.flush()
        return new_session, refresh_token

    async def revoke_refresh_token(self, refresh_token: str | None) -> AuthSession | None:
        if not refresh_token:
            return None
        auth_session = await self.get_active_by_refresh_token(refresh_token)
        if auth_session is None:
            return None
        auth_session.revoked_at = utc_now()
        auth_session.updated_by = auth_session.user_id
        await self.session.flush()
        return auth_session
