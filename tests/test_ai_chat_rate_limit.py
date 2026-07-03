from __future__ import annotations

import sys
import unittest
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config.settings import Settings  # noqa: E402
from app.domains.ai_chat.rate_limit import AiChatRateLimiter, MemoryRateLimitStore, RedisRateLimitStore  # noqa: E402
from fastapi import HTTPException  # noqa: E402


class FakeRedisClient:
    def __init__(self, clock):
        self._clock = clock
        self._state: dict[str, dict[str, float | int]] = {}
        self.set_calls: list[tuple[str, int, int | None, bool | None]] = []
        self.incr_calls: list[str] = []

    async def set(self, key: str, value: int, ex: int | None = None, nx: bool | None = None) -> bool:
        self.set_calls.append((key, value, ex, nx))
        now = self._clock()
        entry = self._state.get(key)
        if nx and entry is not None and float(entry["expires_at"]) > now:
            return False
        self._state[key] = {"count": int(value), "expires_at": now + float(ex or 0)}
        return True

    async def incr(self, key: str) -> int:
        self.incr_calls.append(key)
        now = self._clock()
        entry = self._state.get(key)
        if entry is None or float(entry["expires_at"]) <= now:
            count = 1
            expires_at = now
        else:
            count = int(entry["count"]) + 1
            expires_at = float(entry["expires_at"])
        self._state[key] = {"count": count, "expires_at": expires_at}
        return count

    async def aclose(self) -> None:
        return None


class AiChatRateLimitStoreTest(unittest.IsolatedAsyncioTestCase):
    async def test_memory_store_expires_keys(self) -> None:
        clock = [1000.0]
        store = MemoryRateLimitStore(now=lambda: clock[0])
        key = "ai_chat:rate_limit:test:1"

        self.assertEqual(1, await store.increment(key, 60))
        self.assertEqual(2, await store.increment(key, 60))
        clock[0] += 61
        self.assertEqual(1, await store.increment(key, 60))

    async def test_redis_store_fake_works_without_eval_and_sets_ttl(self) -> None:
        clock = [2000.0]
        fake_client = FakeRedisClient(lambda: clock[0])
        store = RedisRateLimitStore(fake_client)
        key = "ai_chat:rate_limit:test:2"

        self.assertEqual(1, await store.increment(key, 60))
        self.assertEqual(2, await store.increment(key, 60))
        clock[0] += 61
        self.assertEqual(1, await store.increment(key, 60))
        self.assertEqual(3, len(fake_client.set_calls))
        self.assertEqual(1, len(fake_client.incr_calls))
        self.assertEqual(60, fake_client.set_calls[0][2])

    async def test_limiter_is_per_user_and_enforces_limit(self) -> None:
        settings = Settings(environment="local", ai_chat_rate_limit_per_minute=1)
        limiter = AiChatRateLimiter(settings)

        user_a = UUID("00000000-0000-0000-0000-00000000000a")
        user_b = UUID("00000000-0000-0000-0000-00000000000b")

        await limiter.check(user_a)
        with self.assertRaises(HTTPException) as ctx:
            await limiter.check(user_a)
        self.assertEqual("ai_chat_rate_limit_exceeded", getattr(ctx.exception, "detail", None))

        await limiter.check(user_b)

    async def test_production_redis_failure_returns_503(self) -> None:
        settings = Settings(
            environment="production",
            ai_chat_rate_limit_per_minute=1,
            jwt_secret_key="production-secret-key-with-enough-length-123",
        )
        limiter = AiChatRateLimiter(settings)

        class ExplodingStore:
            async def increment(self, key: str, ttl_seconds: int) -> int:  # noqa: ARG002
                raise RuntimeError("redis unavailable")

        limiter._redis_store = ExplodingStore()  # type: ignore[assignment]
        user = UUID("00000000-0000-0000-0000-00000000000d")

        with self.assertRaises(HTTPException) as ctx:
            await limiter.check(user)

        self.assertEqual(503, ctx.exception.status_code)
        self.assertEqual("ai_chat_rate_limit_unavailable", getattr(ctx.exception, "detail", None))

    def test_build_key_hashes_user_id_and_uses_window_epoch(self) -> None:
        user_id = UUID("00000000-0000-0000-0000-00000000000c")
        key = AiChatRateLimiter.build_key(user_id, now=120.0)
        self.assertTrue(key.startswith("ai_chat:rate_limit:"))
        self.assertIn(":2", key)
        self.assertNotIn(str(user_id), key)
