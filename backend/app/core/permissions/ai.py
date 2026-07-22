from __future__ import annotations

from app.shared.enums import AiCapability, Role
from fastapi import HTTPException, status

AI_CAPABILITIES_BY_ROLE: dict[Role, frozenset[AiCapability]] = {
    Role.ADMIN: frozenset(AiCapability),
    Role.TECHNICIAN: frozenset(
        {
            AiCapability.AI_CHAT_ACCESS,
            AiCapability.AI_MACRO_GENERATION,
            AiCapability.AI_IMPORT_ANALYSIS,
        }
    ),
    Role.MANAGER: frozenset({AiCapability.AI_CHAT_ACCESS}),
    Role.VIEWER: frozenset(),
}


def has_ai_capability(role: Role, capability: AiCapability) -> bool:
    return capability in AI_CAPABILITIES_BY_ROLE.get(role, frozenset())


def ensure_ai_enabled(settings: object) -> None:
    if not bool(getattr(settings, "enable_ai_chat", False)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ai_chat_disabled")
