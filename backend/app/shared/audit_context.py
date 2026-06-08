from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Request


@dataclass(frozen=True)
class AuditContext:
    actor_id: UUID | None
    ip_address: str | None
    request_id: str | None
    correlation_id: str | None
    source: str


def build_audit_context(request: Request, actor_id: UUID | None = None) -> AuditContext:
    forwarded_for = request.headers.get("x-forwarded-for")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else None
    if client_ip is None and request.client:
        client_ip = request.client.host

    return AuditContext(
        actor_id=actor_id,
        ip_address=client_ip,
        request_id=getattr(request.state, "request_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        source=request.headers.get("x-audit-source", "api"),
    )
