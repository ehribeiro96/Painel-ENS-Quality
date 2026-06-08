from __future__ import annotations

from typing import Protocol


class MicrosoftGraphClient(Protocol):
    async def list_users(self) -> list[dict[str, object]]:
        raise NotImplementedError
