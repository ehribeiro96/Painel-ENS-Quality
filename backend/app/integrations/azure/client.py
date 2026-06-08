from __future__ import annotations

from typing import Protocol


class AzureIdentityClient(Protocol):
    async def resolve_user(self, email: str) -> dict[str, object] | None:
        raise NotImplementedError
