from __future__ import annotations

from app.api.v1.dependencies.auth import get_current_user, get_optional_current_user
from app.core.config.settings import settings
from app.core.database.session import get_session
from app.core.observability.metrics import metrics
from app.core.security.jwt import create_access_token
from app.core.security.passwords import verify_password
from app.domains.audit.service import AuditService
from app.domains.auth.schemas import LoginRequest, TokenResponse
from app.domains.auth.service import AuthSessionService
from app.domains.users.models import User
from app.domains.users.schemas import UserRead
from app.shared.audit_context import build_audit_context
from app.shared.enums import AuditAction, UserStatus
from app.shared.transactions import commit_or_rollback
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_token,
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
        path=f"{settings.api_prefix}/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        settings.refresh_cookie_name,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
        path=f"{settings.api_prefix}/auth",
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await session.scalar(select(User).where(User.email == payload.email, User.deleted_at.is_(None)))
    if (
        user is None
        or user.status != UserStatus.ACTIVE
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        metrics.increment("auth_failures_total", {"reason": "invalid_credentials"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    token = create_access_token(user.id, user.role.value)
    async def operation() -> None:
        _, refresh_token = await AuthSessionService(session).create_session(
            user_id=user.id,
            user_agent=request.headers.get("user-agent"),
            ip_address=_client_ip(request),
            actor_id=user.id,
        )
        _set_refresh_cookie(response, refresh_token)
        await AuditService(session).record(
            action=AuditAction.LOGIN,
            entity="User",
            entity_id=user.id,
            actor_id=user.id,
            context=build_audit_context(request, user.id),
        )

    await commit_or_rollback(session, operation)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        metrics.increment("auth_failures_total", {"reason": "missing_refresh_token"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_refresh_token")

    auth_session = await AuthSessionService(session).get_active_by_refresh_token(refresh_token)
    if auth_session is None:
        _clear_refresh_cookie(response)
        metrics.increment("auth_failures_total", {"reason": "invalid_refresh_token"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token")

    user = await session.scalar(select(User).where(User.id == auth_session.user_id, User.deleted_at.is_(None)))
    if user is None or user.status != UserStatus.ACTIVE:
        _clear_refresh_cookie(response)
        metrics.increment("auth_failures_total", {"reason": "inactive_refresh_user"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="inactive_user")

    async def operation() -> None:
        _, new_refresh_token = await AuthSessionService(session).rotate(
            auth_session=auth_session,
            user_agent=request.headers.get("user-agent"),
            ip_address=_client_ip(request),
        )
        _set_refresh_cookie(response, new_refresh_token)

    await commit_or_rollback(session, operation)
    return TokenResponse(access_token=create_access_token(user.id, user.role.value), user=UserRead.model_validate(user))


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    async def operation() -> None:
        revoked_session = await AuthSessionService(session).revoke_refresh_token(refresh_token)
        actor_id = current_user.id if current_user else revoked_session.user_id if revoked_session else None
        if actor_id is None:
            return
        await AuditService(session).record(
            action=AuditAction.LOGOUT,
            entity="User",
            entity_id=actor_id,
            actor_id=actor_id,
            context=build_audit_context(request, actor_id),
        )

    await commit_or_rollback(session, operation)
    _clear_refresh_cookie(response)
    return {"status": "ok"}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
