from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from app import main
from app.core.health import readiness_health


class SafeHealthEndpointTest(unittest.IsolatedAsyncioTestCase):
    async def test_liveness_exposes_only_status(self) -> None:
        self.assertEqual({"status": "ok"}, await main.health_live())
        self.assertEqual({"status": "ok"}, await main.health())

    async def test_readiness_returns_only_boolean_dependency_state(self) -> None:
        raw = {
            "status": "degraded",
            "postgres": {"status": "error", "error": "select * from secret_table"},
            "redis": {"status": "ok", "url": "redis://internal"},
            "migration": {"status": "up_to_date", "current_revision": "0006"},
            "bootstrap_admin": {"email": "internal@example.test"},
        }
        with patch("app.core.health.dependency_health", new=AsyncMock(return_value=raw)):
            payload = await readiness_health()

        self.assertEqual({"database": False, "redis": True, "migrations": True}, payload)
        serialized = repr(payload)
        self.assertNotIn("secret_table", serialized)
        self.assertNotIn("internal@example.test", serialized)
        self.assertNotIn("current_revision", serialized)

    async def test_ready_and_compatibility_endpoint_never_return_internal_details(self) -> None:
        safe = {"database": True, "redis": True, "migrations": True}
        with patch.object(main, "readiness_health", new=AsyncMock(return_value=safe)):
            ready_response = await main.health_ready()
            dependencies = await main.health_dependencies()

        self.assertEqual(safe, dependencies)
        self.assertEqual(safe, ready_response.body and __import__("json").loads(ready_response.body))


if __name__ == "__main__":
    unittest.main()
