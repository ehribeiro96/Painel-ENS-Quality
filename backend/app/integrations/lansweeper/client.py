from __future__ import annotations

from typing import Protocol


class LansweeperClient(Protocol):
    async def full_sync(self) -> list[dict[str, object]]:
        raise NotImplementedError

    async def incremental_sync(self, since_token: str) -> list[dict[str, object]]:
        raise NotImplementedError
