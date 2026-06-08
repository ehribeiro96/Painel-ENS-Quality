from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


UNIQUE_CONSTRAINTS: dict[str, tuple[str, str]] = {
    "users_email_key": ("email", "Ja existe um usuario com este e-mail."),
    "assets_serial_key": ("serial_number", "Ja existe um ativo com este serial."),
    "assets_patrimony_key": ("patrimony_number", "Ja existe um ativo com este patrimonio."),
}


def integrity_error_to_http(exc: IntegrityError) -> HTTPException:
    message = str(getattr(exc, "orig", exc))
    field = "unknown"
    friendly_message = "Registro duplicado ou violacao de integridade."
    for constraint, (candidate_field, candidate_message) in UNIQUE_CONSTRAINTS.items():
        if constraint in message:
            field = candidate_field
            friendly_message = candidate_message
            break
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "unique_constraint_violation",
            "field": field,
            "message": friendly_message,
        },
    )


async def commit_or_rollback(session: AsyncSession, operation: Callable[[], Awaitable[T]]) -> T:
    try:
        result = await operation()
        await session.commit()
        return result
    except IntegrityError as exc:
        await session.rollback()
        raise integrity_error_to_http(exc) from exc
    except Exception:
        await session.rollback()
        raise
