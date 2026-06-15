from __future__ import annotations

import asyncio
import hashlib
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Protocol
from uuid import UUID

import structlog
from app.core.config.settings import Settings, settings
from fastapi import HTTPException, status
from redis import asyncio as redis

logger = structlog.get_logger()

AI_CHAT_RATE_LIMIT_TTL_SECONDS = 60
_AI_CHAT_RATE_LIMIT: dict[str, deque[float]] = defaultdict(deque)


class RateLimitStore(Protocol):
    async def increment(self, key: str, ttl_seconds: int) -> int:
        ...


class MemoryRateLimitStore:
    def __init__(self, buckets: dict[str, deque[float]] | None = None, now: Callable[[], float] | None = None) -> None:
        self._buckets = buckets if buckets is not None else _AI_CHAT_RATE_LIMIT
        self._now = now or time.time
        self._lock = asyncio.Lock()

    async def increment(self, key: str, ttl_seconds: int) -> int:
        now = self._now()
        window_start = now - ttl_seconds
        async with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < window_start:
                bucket.popleft()
            bucket.append(now)
            return len(bucket)

    def clear(self) -> None:
        self._buckets.clear()


class RedisRateLimitStore:
    def __init__(self, client: object) -> None:
        self._client = client

    async def increment(self, key: str, ttl_seconds: int) -> int:
        created = await self._client.set(key, 1, ex=ttl_seconds, nx=True)
        if created:
            return 1
        result = await self._client.incr(key)
        return int(result)


class AiChatRateLimiter:
    def __init__(self, settings_obj: Settings) -> None:
        self.settings = settings_obj
        self._memory_store = MemoryRateLimitStore()
        self._redis_store: RedisRateLimitStore | None = None
        self._redis_client: object | None = None

    @staticmethod
    def build_key(user_id: UUID, *, now: float | None = None) -> str:
        window_epoch = int((now or time.time()) // AI_CHAT_RATE_LIMIT_TTL_SECONDS)
        user_hash = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()
        return f"ai_chat:rate_limit:{user_hash}:{window_epoch}"

    async def check(self, user_id: UUID) -> None:
        limit = int(self.settings.ai_chat_rate_limit_per_minute or 0)
        if limit <= 0:
            return
        key = self.build_key(user_id)
        store = self._select_store()
        try:
            current = await store.increment(key, AI_CHAT_RATE_LIMIT_TTL_SECONDS)
        except Exception as exc:  # noqa: BLE001 - operational failures must be handled explicitly
            if self._allows_local_fallback():
                logger.warning(
                    "ai_chat_rate_limit_redis_fallback",
                    environment=self.settings.environment,
                    fallback_store="memory",
                    error_type=type(exc).__name__,
                )
                current = await self._memory_store.increment(key, AI_CHAT_RATE_LIMIT_TTL_SECONDS)
            else:
                logger.error(
                    "ai_chat_rate_limit_store_unavailable",
                    environment=self.settings.environment,
                    error_type=type(exc).__name__,
                )
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="ai_chat_rate_limit_unavailable") from exc

        if current > limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="ai_chat_rate_limit_exceeded")

    def clear_memory(self) -> None:
        self._memory_store.clear()

    def _select_store(self) -> RateLimitStore:
        if self._uses_redis_store():
            return self._redis_store or self._get_redis_store()
        return self._memory_store

    def _get_redis_store(self) -> RedisRateLimitStore:
        if self._redis_store is None:
            if self._redis_client is None:
                self._redis_client = redis.from_url(self.settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
            self._redis_store = RedisRateLimitStore(self._redis_client)
        return self._redis_store

    def _uses_redis_store(self) -> bool:
        return self.settings.environment in {"staging", "production"}

    def _allows_local_fallback(self) -> bool:
        return self.settings.environment == "local"


_RATE_LIMITER = AiChatRateLimiter(settings)


def get_ai_chat_rate_limiter() -> AiChatRateLimiter:
    return _RATE_LIMITER


def reset_ai_chat_rate_limit_memory() -> None:
    _RATE_LIMITER.clear_memory()
