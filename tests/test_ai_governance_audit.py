from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.api.v1.routes import ai_chat, imports
from app.core.database import base as _database_base  # noqa: F401
from app.domains.ai_chat.schemas import ApoemaChatMessageCreate, ApoemaChatMessageResponse
from app.domains.audit.ai import record_ai_audit, record_ai_operation_audits, sanitize_ai_error
from app.services.import_ai_analysis import ImportAiAnalysisError
from app.shared.enums import Role
from fastapi import HTTPException
from sqlalchemy.exc import MissingGreenlet


class _Session:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.commit_count = 0

    def add(self, value: object) -> None:
        self.added.append(value)

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        return None


class _ExpiredJob:
    def __init__(self) -> None:
        self._id = uuid.uuid4()
        self.expired = False

    @property
    def id(self):  # noqa: ANN201
        if self.expired:
            raise MissingGreenlet("ORM object accessed after rollback")
        return self._id


class _Scalars:
    def scalars(self):  # noqa: ANN201
        return []


class _ImportSession(_Session):
    def __init__(self, job: _ExpiredJob) -> None:
        super().__init__()
        self.job = job

    async def scalar(self, statement):  # noqa: ANN001, ANN201, ARG002
        return self.job

    async def execute(self, statement):  # noqa: ANN001, ANN201, ARG002
        return _Scalars()

    async def rollback(self) -> None:
        self.job.expired = True


class _SessionContext:
    def __init__(self, session: _Session) -> None:
        self.session = session

    async def __aenter__(self):  # noqa: ANN201
        return self.session

    async def __aexit__(self, exc_type, exc, traceback):  # noqa: ANN001, ANN201
        return False


class AiGovernanceAuditTest(unittest.IsolatedAsyncioTestCase):
    async def test_success_event_records_correct_user_role_provider_and_resource(self) -> None:
        session = _Session()
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.TECHNICIAN)
        resource_id = uuid.uuid4()

        event = await record_ai_audit(
            session,
            event="MACRO_GENERATION",
            user=user,
            provider="hermes",
            model="hermes-agent",
            resource_type="ItilMacro",
            resource_id=resource_id,
            status="SUCCESS",
            duration_ms=31,
        )

        self.assertIs(event, session.added[-1])
        self.assertEqual(user.id, event.actor_id)
        self.assertEqual("MACRO_GENERATION", event.after["event"])
        self.assertEqual("TECHNICIAN", event.after["role"])
        self.assertEqual("hermes", event.after["provider"])
        self.assertEqual("hermes-agent", event.after["model"])
        self.assertEqual("ItilMacro", event.after["resource_type"])
        self.assertEqual(str(resource_id), event.after["resource_id"])
        self.assertEqual("SUCCESS", event.after["status"])
        self.assertEqual(31, event.after["duration_ms"])
        self.assertIsNone(event.after["error"])
        self.assertIn("timestamp", event.after)

    async def test_error_event_sanitizes_prompt_token_cookie_password_and_secret(self) -> None:
        session = _Session()
        user_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
        resource_id = uuid.UUID("22222222-2222-4222-8222-222222222222")
        user = SimpleNamespace(id=user_id, role=Role.ADMIN)
        sensitive_values = (
            "PROMPT_SENSITIVE_SENTINEL_9F8E7D6C",
            "TOKEN_SENSITIVE_SENTINEL_8E7D6C5B",
            "COOKIE_SENSITIVE_SENTINEL_7D6C5B4A",
            "PASSWORD_SENSITIVE_SENTINEL_6C5B4A39",
            "API_SECRET_SENTINEL_5B4A3928",
            "AUTHORIZATION_SENSITIVE_SENTINEL_4A392817",
            "TRACEBACK_SENSITIVE_SENTINEL_39281706",
        )
        sensitive = (
            "ai_provider_timeout: "
            f"prompt={sensitive_values[0]} token={sensitive_values[1]} cookie={sensitive_values[2]} "
            f"password={sensitive_values[3]} secret={sensitive_values[4]} "
            f"Authorization=Bearer {sensitive_values[5]} traceback={sensitive_values[6]}"
        )

        event = await record_ai_audit(
            session,
            event="AI_PROVIDER_CALL",
            user=user,
            provider="hermes",
            model="hermes-agent",
            resource_type="ChatConversation",
            resource_id=resource_id,
            status="FAILED",
            duration_ms=9,
            error=sensitive,
        )

        error_payload = event.after["error"]
        self.assertEqual("ai_provider_timeout", error_payload)
        for sensitive_value in sensitive_values:
            self.assertNotIn(sensitive_value, error_payload)
        for raw_field in ("prompt=", "token=", "cookie=", "password=", "secret=", "authorization=", "traceback="):
            self.assertNotIn(raw_field, error_payload.lower())

        self.assertEqual(user_id, event.actor_id)
        self.assertEqual(resource_id, event.entity_id)
        self.assertEqual(str(user_id), event.after["user_id"])
        self.assertEqual(str(resource_id), event.after["resource_id"])
        self.assertEqual("AI_PROVIDER_CALL", event.after["action"])
        self.assertEqual("FAILED", event.after["status"])
        self.assertEqual("hermes", event.after["provider"])

    def test_unknown_error_is_replaced_with_generic_code(self) -> None:
        self.assertEqual("ai_operation_failed", sanitize_ai_error("falha com senha supersecreta"))

    async def test_operation_records_provider_and_domain_events_for_failure(self) -> None:
        session = _Session()
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.ADMIN)

        await record_ai_operation_audits(
            session,
            event="IMPORT_ANALYSIS",
            user=user,
            provider="hermes",
            model="hermes-agent",
            resource_type="ImportJob",
            resource_id=uuid.uuid4(),
            status="FAILED",
            duration_ms=120,
            error="hermes_timeout",
        )

        self.assertEqual(["AI_PROVIDER_CALL", "IMPORT_ANALYSIS"], [item.after["event"] for item in session.added])
        self.assertEqual(["FAILED", "FAILED"], [item.after["status"] for item in session.added])

    async def test_apoema_route_persists_success_events_without_prompt(self) -> None:
        session = _Session()
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.TECHNICIAN)
        payload = ApoemaChatMessageCreate(provider="hermes", model="hermes-agent", message="prompt sigiloso")
        response = ApoemaChatMessageResponse(
            conversation_id=str(uuid.uuid4()),
            message_id=str(uuid.uuid4()),
            provider="hermes",
            model="hermes-agent",
            status="ok",
            content="resposta",
            created_at=datetime.now(UTC),
        )
        original_enabled = ai_chat.settings.enable_ai_chat
        ai_chat.settings.enable_ai_chat = True
        try:
            with patch.object(ai_chat, "_apply_rate_limit", new=AsyncMock()), patch.object(
                ai_chat, "generate_apoema_message", new=AsyncMock(return_value=response)
            ):
                result = await ai_chat.send_apoema_message(payload, user, session)
        finally:
            ai_chat.settings.enable_ai_chat = original_enabled

        self.assertIs(response, result)
        self.assertEqual(["AI_PROVIDER_CALL", "CHAT_MESSAGE"], [item.after["event"] for item in session.added])
        self.assertNotIn("prompt sigiloso", str([item.after for item in session.added]))

    async def test_import_ai_timeout_audit_failure(self) -> None:
        job = _ExpiredJob()
        request_session = _ImportSession(job)
        audit_session = _Session()
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.ADMIN)
        timeout = ImportAiAnalysisError("hermes_timeout: password=must-not-leak")

        with patch.object(imports, "ensure_ai_enabled"), patch.object(
            imports, "analyze_import", new=AsyncMock(side_effect=timeout)
        ), patch("app.domains.audit.ai.AsyncSessionLocal", return_value=_SessionContext(audit_session)):
            with self.assertRaises(HTTPException) as raised:
                await imports.analyze_import_with_hermes(job._id, request_session, user)

        self.assertEqual(502, raised.exception.status_code)
        self.assertEqual("hermes_timeout", raised.exception.detail)
        self.assertEqual(["AI_PROVIDER_CALL", "IMPORT_ANALYSIS"], [item.after["event"] for item in audit_session.added])
        self.assertEqual(["FAILED", "FAILED"], [item.after["status"] for item in audit_session.added])
        self.assertEqual(1, audit_session.commit_count)
        self.assertEqual(0, request_session.commit_count)
        self.assertEqual(1, len({item.entity_id for item in audit_session.added}))
        self.assertNotIn("must-not-leak", str([item.after for item in audit_session.added]))


if __name__ == "__main__":
    unittest.main()