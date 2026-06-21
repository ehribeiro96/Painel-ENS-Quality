from __future__ import annotations

import asyncio
import sys
import unittest

from tests.operational_http import ROOT

sys.path.insert(0, str(ROOT / "backend"))

from app.core import startup  # noqa: E402


class FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def info(self, event: str, **kwargs) -> None:
        self.events.append((event, kwargs))

    def error(self, event: str, **kwargs) -> None:
        self.events.append((event, kwargs))

    def warning(self, event: str, **kwargs) -> None:
        self.events.append((event, kwargs))


class StartupDiagnosticsTest(unittest.IsolatedAsyncioTestCase):
    async def test_failed_startup_step_logs_structured_diagnostic_without_secret(self) -> None:
        fake_logger = FakeLogger()
        original_logger = startup.logger
        startup.logger = fake_logger
        try:
            async def failing_operation() -> None:
                raise RuntimeError("controlled startup failure")

            with self.assertRaises(RuntimeError):
                await startup._run_startup_step("bootstrap_admin", "bootstrap_admin_begin", "bootstrap_admin_ok", failing_operation)
        finally:
            startup.logger = original_logger

        events = {event: payload for event, payload in fake_logger.events}
        self.assertIn("bootstrap_admin_begin", events)
        self.assertIn("startup_failed", events)
        failure = events["startup_failed"]
        self.assertEqual(failure["failed_step"], "bootstrap_admin")
        self.assertEqual(failure["exception_type"], "RuntimeError")
        self.assertIn("controlled startup failure", failure["exception_message"])
        self.assertIn("Traceback", failure["traceback"])
        serialized = repr(failure)
        self.assertNotIn("ADMIN_PASSWORD=", serialized)
        self.assertNotIn("JWT_SECRET_KEY=", serialized)
        self.assertNotIn("DATABASE_URL=", serialized)

    async def test_startup_step_timeout_fails_fast_with_clear_reason(self) -> None:
        fake_logger = FakeLogger()
        original_logger = startup.logger
        startup.logger = fake_logger
        try:
            async def slow_operation() -> None:
                await asyncio.sleep(1)

            with self.assertRaises(TimeoutError) as raised:
                await startup._run_startup_step(
                    "postgres",
                    "database_wait_begin",
                    "database_wait_ok",
                    slow_operation,
                    timeout_seconds=0.01,
                )
        finally:
            startup.logger = original_logger

        self.assertIn("postgres_timeout_after_0.01s", str(raised.exception))
        events = {event: payload for event, payload in fake_logger.events}
        self.assertIn("startup_step_begin", events)
        self.assertIn("database_wait_begin", events)
        self.assertIn("startup_step_timeout", events)
        self.assertIn("startup_failed", events)
        self.assertEqual("postgres", events["startup_step_timeout"]["step"])
        self.assertEqual("TimeoutError", events["startup_failed"]["exception_type"])

    def test_redacts_sensitive_urls_and_fields_from_startup_errors(self) -> None:
        text = (
            "database postgresql+asyncpg://user:pass@localhost:5432/db "
            "cache redis://:pass@localhost:6379/0 password=abc token=def"
        )

        redacted = startup._redact_sensitive_text(text)

        self.assertNotIn("user:pass", redacted)
        self.assertNotIn(":pass@", redacted)
        self.assertNotIn("password=abc", redacted)
        self.assertNotIn("token=def", redacted)
        self.assertIn("<REDACTED", redacted)

    def test_safe_startup_snapshot_uses_presence_flags_for_sensitive_values(self) -> None:
        snapshot = startup.safe_startup_config_snapshot()
        self.assertIn("admin_email_set", snapshot)
        self.assertIn("admin_name_set", snapshot)
        self.assertIn("admin_password_set", snapshot)
        self.assertIn("jwt_secret_key_set", snapshot)
        self.assertIn("database_url_set", snapshot)
        self.assertIn("redis_url_set", snapshot)
        self.assertNotIn("admin_email", snapshot)
        self.assertNotIn("admin_name", snapshot)
        self.assertNotIn("admin_password", snapshot)
        self.assertNotIn("jwt_secret_key", snapshot)
        self.assertNotIn("database_url", snapshot)
        self.assertNotIn("redis_url", snapshot)
