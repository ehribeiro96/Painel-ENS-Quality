from __future__ import annotations

from app.shared.enums import Role
from fastapi import HTTPException, status


def require_roles(current_role: Role, allowed: set[Role]) -> None:
    if current_role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission_denied")
