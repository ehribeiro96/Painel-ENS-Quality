from __future__ import annotations

from uuid import UUID

import structlog
from app.core.database.session import get_session
from app.core.permissions.ai import has_ai_capability
from app.core.security.jwt import decode_access_token
from app.domains.users.models import User
from app.shared.enums import AiCapability, Role, UserStatus
from app.shared.models import utc_now
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

bearer = HTTPBearer(auto_error=False)
bearer_credentials = Depends(bearer)
database_session = Depends(get_session)
logger = structlog.get_logger()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = bearer_credentials,
    session: AsyncSession = database_session,
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token") from exc
    user = await session.scalar(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="inactive_user")
    request.state.user_id = str(user.id)
    request.state.user_role = user.role.value
    return user


async def get_optional_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = bearer_credentials,
    session: AsyncSession = database_session,
) -> User | None:
    if credentials is None:
        return None
    return await get_current_user(request, credentials, session)


def require_role(*roles: Role):
    current_user_dependency = Depends(get_current_user)

    async def dependency(current_user: User = current_user_dependency) -> User:
        if current_user.role not in set(roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission_denied")
        return current_user

    return dependency


def require_ai_capability(capability: AiCapability):
    current_user_dependency = Depends(get_current_user)

    async def dependency(current_user: User = current_user_dependency) -> User:
        allowed = has_ai_capability(current_user.role, capability)
        logger.info(
            "ai_authorization",
            user_id=str(current_user.id),
            action=capability.value,
            timestamp=utc_now().isoformat(),
            result="allowed" if allowed else "denied",
        )
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ai_capability_denied")
        return current_user

    return dependency
