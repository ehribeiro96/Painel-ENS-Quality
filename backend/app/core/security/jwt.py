from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.config.settings import settings
from jose import JWTError, jwt


def create_access_token(subject: UUID, role: str) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": str(subject),
        "role": role,
        "typ": "access",
        "jti": str(uuid.uuid4()),
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("invalid_token") from exc
    if payload.get("typ") != "access":
        raise ValueError("invalid_token_type")
    return payload
