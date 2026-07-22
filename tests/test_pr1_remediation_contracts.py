from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import uuid
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.api.v1.routes import ai_chat, macros
from app.domains.ai_chat.providers import AiProviderConfigurationError, AiProviderRequestError
from app.domains.macros.ai_service import calculate_itil_priority
from app.domains.macros.schemas import ItilMacroGenerateRequest
from app.shared.enums import Role
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]


class _Session:
    def __init__(self, expire: Callable[[], object] | None = None) -> None:
        self.added: list[object] = []
        self.commits = 0
        self.rollbacks = 0
        self.expire = expire

    def add(self, item: object) -> None:
        self.added.append(item)

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1
        if self.expire:
            self.expire()


class _ExpiringObject:
    def __init__(self, **values: object) -> None:
        self.values = values
        self.expired = False

    def __getattr__(self, name: str) -> object:
        if self.expired:
            raise RuntimeError("ORM object accessed after rollback")
        return self.values[name]


class ProviderHttpContractTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.user = SimpleNamespace(id=uuid.uuid4(), role=Role.TECHNICIAN)
        self.payload = ai_chat.ApoemaChatMessageCreate(provider="hermes", model="hermes-agent", message="segredo não persistir")
        self.original_enabled = ai_chat.settings.enable_ai_chat
        ai_chat.settings.enable_ai_chat = True

    async def asyncTearDown(self) -> None:
        ai_chat.settings.enable_ai_chat = self.original_enabled

    async def _assert_provider_failure(self, error: Exception, expected_status: int, expected_code: str) -> None:
        request_session = _Session()
        audit_session = _Session()

        class Context:
            async def __aenter__(self):
                return audit_session

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        with patch.object(ai_chat, "_apply_rate_limit", new=AsyncMock()), patch.object(
            ai_chat, "generate_apoema_message", new=AsyncMock(side_effect=error)
        ), patch("app.domains.audit.ai.AsyncSessionLocal", return_value=Context()):
            with self.assertRaises(HTTPException) as raised:
                await ai_chat.send_apoema_message(self.payload, self.user, request_session)

        self.assertEqual(expected_status, raised.exception.status_code)
        self.assertEqual(expected_code, raised.exception.detail)
        self.assertEqual(0, request_session.commits)
        self.assertEqual(1, audit_session.commits)
        serialized = json.dumps([item.after for item in audit_session.added])
        self.assertNotIn("segredo", serialized)
        self.assertEqual(["AI_PROVIDER_CALL", "CHAT_MESSAGE"], [item.after["event"] for item in audit_session.added])

    async def test_ephemeral_timeout_is_502_and_audited(self) -> None:
        await self._assert_provider_failure(AiProviderRequestError("hermes_timeout:token=secret"), 502, "ai_provider_timeout")

    async def test_ephemeral_offline_is_502_and_audited(self) -> None:
        await self._assert_provider_failure(AiProviderRequestError("hermes_request_failed"), 502, "ai_provider_unavailable")

    async def test_ephemeral_not_configured_is_503_and_audited(self) -> None:
        await self._assert_provider_failure(AiProviderConfigurationError("hermes_cli_not_configured"), 503, "ai_provider_not_configured")

    async def test_health_offloads_sync_probe(self) -> None:
        ai_chat._AI_HEALTH_CACHE = None
        with patch.object(ai_chat, "get_ai_provider_health", return_value={"provider": "mock", "configured": True, "status": "ok"}), patch(
            "app.api.v1.routes.ai_chat.asyncio.to_thread", new=AsyncMock(return_value={"provider": "mock", "configured": True, "status": "ok"})
        ) as offload:
            result = await ai_chat.health(self.user)
            cached = await ai_chat.health(self.user)
        self.assertEqual("ok", result["status"])
        self.assertEqual(result, cached)
        offload.assert_awaited_once()

    async def test_persistent_create_and_send_use_primitive_audit_snapshots(self) -> None:
        user = _ExpiringObject(id=uuid.uuid4(), role=Role.TECHNICIAN)
        conversation = _ExpiringObject(id=uuid.uuid4(), provider="hermes", model="hermes-agent")
        audit_session = _Session()

        class Context:
            async def __aenter__(self): return audit_session
            async def __aexit__(self, exc_type, exc, traceback): return False

        class BrokenService:
            def __init__(self, session): self.repository = SimpleNamespace()  # noqa: ANN001
            async def create_conversation(self, payload, user_id): raise AiProviderRequestError("hermes_timeout")  # noqa: ANN001
            async def get_conversation(self, conversation_id, user_id): return conversation  # noqa: ANN001
            async def send_message(self, conversation, payload, user_id): raise AiProviderRequestError("hermes_request_failed")  # noqa: ANN001

        create_session = _Session(lambda: setattr(user, "expired", True))
        with patch.object(ai_chat, "AiChatService", BrokenService), patch.object(ai_chat, "_apply_rate_limit", new=AsyncMock()), patch("app.domains.audit.ai.AsyncSessionLocal", return_value=Context()):
            with self.assertRaises(HTTPException) as created_error:
                await ai_chat.create_conversation(ai_chat.AiChatConversationCreate(message="teste"), create_session, user)
        self.assertEqual(502, created_error.exception.status_code)

        user.expired = False
        send_session = _Session(lambda: (setattr(user, "expired", True), setattr(conversation, "expired", True)))
        with patch.object(ai_chat, "AiChatService", BrokenService), patch.object(ai_chat, "_apply_rate_limit", new=AsyncMock()), patch("app.domains.audit.ai.AsyncSessionLocal", return_value=Context()):
            with self.assertRaises(HTTPException) as sent_error:
                await ai_chat.send_message(conversation.values["id"], ai_chat.AiChatMessageCreate(content="teste"), send_session, user)
        self.assertEqual(502, sent_error.exception.status_code)
        self.assertIn("CHAT_CONVERSATION", [item.after["event"] for item in audit_session.added])
        self.assertIn("CHAT_MESSAGE", [item.after["event"] for item in audit_session.added])

    async def test_macro_failure_survives_expired_user_and_failed_secondary_audit(self) -> None:
        user = _ExpiringObject(id=uuid.uuid4(), role=Role.TECHNICIAN)
        request_session = _Session(lambda: setattr(user, "expired", True))

        class FailingContext:
            async def __aenter__(self): raise RuntimeError("audit database unavailable")
            async def __aexit__(self, exc_type, exc, traceback): return False

        original_enabled = macros.settings.enable_ai_chat
        macros.settings.enable_ai_chat = True
        try:
            with patch.object(macros, "generate_itil_macro", new=AsyncMock(side_effect=AiProviderRequestError("hermes_timeout"))), patch("app.domains.audit.ai.AsyncSessionLocal", return_value=FailingContext()):
                with self.assertRaises(HTTPException) as raised:
                    await macros.generate_itil_macro_route(ItilMacroGenerateRequest(summary="falha controlada"), user, request_session)
        finally:
            macros.settings.enable_ai_chat = original_enabled
        self.assertEqual(502, raised.exception.status_code)
        self.assertEqual("hermes_timeout", raised.exception.detail)


class ItilPriorityContractTest(unittest.TestCase):
    def test_complete_matrix_and_unknown_contract(self) -> None:
        expected = {
            ("high", "high"): "P1", ("high", "medium"): "P2", ("high", "low"): "P3",
            ("medium", "high"): "P2", ("medium", "medium"): "P3", ("medium", "low"): "P4",
            ("low", "high"): "P3", ("low", "medium"): "P4", ("low", "low"): "P4",
        }
        for pair, priority in expected.items():
            self.assertEqual(priority, calculate_itil_priority(*pair))
        for pair in (("unknown", "unknown"), ("unknown", "high"), ("high", "unknown")):
            self.assertEqual("unknown", calculate_itil_priority(*pair))

    def test_preview_request_has_no_official_generation_contract(self) -> None:
        self.assertNotIn("movement_id", ItilMacroGenerateRequest.model_fields)


class FrontendOperationalContractTest(unittest.TestCase):
    def test_macros_are_explicit_preview_only(self) -> None:
        page = (ROOT / "frontend/itam-platform/src/apoema/pages/MacrosPage.tsx").read_text(encoding="utf-8")
        api = (ROOT / "frontend/itam-platform/src/lib/api.ts").read_text(encoding="utf-8")
        self.assertIn("Rascunho não oficial", page)
        self.assertIn("Copiar rascunho", page)
        self.assertIn("/macros/itil/preview", api)
        self.assertNotIn("/macros/itil/generate", api)
        self.assertNotIn("macroMarkCopied", page)

    def test_imports_manual_flow_does_not_require_ai(self) -> None:
        page = (ROOT / "frontend/itam-platform/src/apoema/pages/ImportsPage.tsx").read_text(encoding="utf-8")
        upload_body = page.split("async function upload", 1)[1].split("async function", 1)[0]
        self.assertNotIn("analyze(", upload_body)
        for term in ("Analisar com Hermes", "importStaging", "importConflicts", "importValidationErrors", "cancelImport", "Limpar tela", "Tentar novamente"):
            self.assertIn(term, page)


class CiAndMigrationContractTest(unittest.TestCase):
    def test_junit_parser_rejects_skip_invalid_and_zero_tests(self) -> None:
        path = ROOT / "scripts/assert_pytest_report.py"
        spec = importlib.util.spec_from_file_location("assert_pytest_report", path)
        self.assertIsNotNone(spec and spec.loader)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.xml"
            report.write_text('<testsuites tests="2" failures="0" errors="0" skipped="0"><testsuite tests="2" failures="0" errors="0" skipped="0"/></testsuites>', encoding="utf-8")
            self.assertEqual(0, module.main([str(report)]))
            self.assertEqual(0, module.main([str(report), "--exact-tests", "2"]))
            self.assertNotEqual(0, module.main([str(report), "--exact-tests", "3"]))
            report.write_text('<testsuites><testsuite tests="1" failures="0" errors="0" skipped="1"/></testsuites>', encoding="utf-8")
            self.assertNotEqual(0, module.main([str(report)]))
            report.write_text('<testsuites><testsuite tests="0" failures="0" errors="0" skipped="0"/></testsuites>', encoding="utf-8")
            self.assertNotEqual(0, module.main([str(report)]))
            report.write_text('<bad', encoding="utf-8")
            self.assertNotEqual(0, module.main([str(report)]))

    def test_migration_precheck_is_read_only_and_documented(self) -> None:
        sql_path = ROOT / "docs/operations/sql/precheck-0007-macro-movement-unique.sql"
        sql = sql_path.read_text(encoding="utf-8").upper()
        self.assertIn("FROM MACRO_GENERATIONS", sql)
        self.assertIn("CONTEXT_TYPE = 'ASSET_MOVEMENT'", sql)
        self.assertIn("CONTEXT_ID IS NOT NULL", sql)
        self.assertIn("GROUP BY CONTEXT_TYPE, CONTEXT_ID", " ".join(sql.split()))
        self.assertIn("HAVING COUNT(*) > 1", " ".join(sql.split()))
        for forbidden in ("DELETE", "UPDATE", "INSERT"):
            self.assertNotIn(forbidden, sql)
        for doc in ("docs/operations/deployment.md", "docs/releases/v1.0.0-rc1.md"):
            self.assertIn(str(sql_path.relative_to(ROOT)), (ROOT / doc).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
