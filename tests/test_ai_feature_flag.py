from __future__ import annotations

import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.api.v1.dependencies import auth
from app.api.v1.dependencies.auth import require_ai_capability
from app.api.v1.routes import ai_chat, imports, macros
from app.core.config.settings import Settings
from app.domains.ai_chat import providers
from app.domains.ai_chat.schemas import ApoemaChatMessageCreate
from app.domains.macros.schemas import ItilMacroGenerateRequest
from app.shared.enums import AiCapability, Role
from fastapi import HTTPException


class AiAuthorizationAndFeatureFlagTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.original_enabled = ai_chat.settings.enable_ai_chat

    def tearDown(self) -> None:
        ai_chat.settings.enable_ai_chat = self.original_enabled

    def test_local_runtime_honors_explicit_feature_flag_disable(self) -> None:
        self.assertTrue(Settings(environment="local").enable_ai_chat)
        self.assertFalse(Settings(environment="local", enable_ai_chat=False).enable_ai_chat)
        self.assertTrue(Settings(environment="local", enable_ai_chat=True).enable_ai_chat)

    def test_hermes_subprocess_uses_restricted_non_operational_toolset(self) -> None:
        completed = SimpleNamespace(returncode=0, stdout="resposta segura", stderr="")

        with patch.object(providers.subprocess, "run", return_value=completed) as run:
            content, _metadata = providers._run_hermes_chat("consulta", 5, "apoema-test")

        command = run.call_args.args[0]
        self.assertEqual("resposta segura", content)
        self.assertIn("--ignore-rules", command)
        self.assertIn("--max-turns", command)
        self.assertEqual("todo", command[command.index("-t") + 1])
        self.assertNotIn("--yolo", command)
        for forbidden_toolset in ("terminal", "file", "code_execution", "browser", "cronjob", "memory"):
            self.assertNotIn(forbidden_toolset, command)

    async def test_viewer_has_no_ai_chat_capability(self) -> None:
        dependency = require_ai_capability(AiCapability.AI_CHAT_ACCESS)
        viewer = SimpleNamespace(id=uuid.uuid4(), role=Role.VIEWER)

        with self.assertRaises(HTTPException) as raised:
            await dependency(viewer)

        self.assertEqual(403, raised.exception.status_code)
        self.assertEqual("ai_capability_denied", raised.exception.detail)

    async def test_admin_and_technician_have_explicit_authorized_capabilities(self) -> None:
        admin = SimpleNamespace(id=uuid.uuid4(), role=Role.ADMIN)
        technician = SimpleNamespace(id=uuid.uuid4(), role=Role.TECHNICIAN)

        for capability in AiCapability:
            self.assertIs(admin, await require_ai_capability(capability)(admin))
        for capability in (
            AiCapability.AI_CHAT_ACCESS,
            AiCapability.AI_MACRO_GENERATION,
            AiCapability.AI_IMPORT_ANALYSIS,
        ):
            self.assertIs(technician, await require_ai_capability(capability)(technician))

        with self.assertRaises(HTTPException):
            await require_ai_capability(AiCapability.AI_PROVIDER_CONFIGURATION)(technician)

    async def test_ai_authorization_audit_records_required_fields(self) -> None:
        events: list[tuple[str, dict[str, object]]] = []
        original_logger = auth.logger
        auth.logger = SimpleNamespace(info=lambda event, **values: events.append((event, values)))
        try:
            viewer = SimpleNamespace(id=uuid.uuid4(), role=Role.VIEWER)
            with self.assertRaises(HTTPException):
                await require_ai_capability(AiCapability.AI_CHAT_ACCESS)(viewer)
        finally:
            auth.logger = original_logger

        event, values = events[0]
        self.assertEqual("ai_authorization", event)
        self.assertEqual(str(viewer.id), values["user_id"])
        self.assertEqual(AiCapability.AI_CHAT_ACCESS.value, values["action"])
        self.assertEqual("denied", values["result"])
        self.assertTrue(values["timestamp"])

    async def test_disabled_flag_blocks_message_before_provider_call(self) -> None:
        ai_chat.settings.enable_ai_chat = False
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.ADMIN)
        payload = ApoemaChatMessageCreate(message="não executar", provider="hermes", model="hermes-agent")

        with patch.object(ai_chat, "generate_apoema_message", new=AsyncMock()) as provider_call:
            with self.assertRaises(HTTPException) as raised:
                await ai_chat.send_apoema_message(payload, user)

        self.assertEqual(403, raised.exception.status_code)
        self.assertEqual("ai_chat_disabled", raised.exception.detail)
        provider_call.assert_not_awaited()

    async def test_disabled_flag_blocks_provider_catalog_and_health_probe(self) -> None:
        ai_chat.settings.enable_ai_chat = False

        with patch.object(ai_chat, "build_apoema_provider_catalog") as catalog:
            with self.assertRaises(HTTPException) as providers_error:
                await ai_chat.list_apoema_providers()
        with patch.object(ai_chat, "get_ai_provider_health") as health_probe:
            with self.assertRaises(HTTPException) as health_error:
                await ai_chat.health()

        self.assertEqual(403, providers_error.exception.status_code)
        self.assertEqual(403, health_error.exception.status_code)
        catalog.assert_not_called()
        health_probe.assert_not_called()

    async def test_disabled_flag_blocks_macro_and_import_ai_before_execution(self) -> None:
        ai_chat.settings.enable_ai_chat = False
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.ADMIN)
        payload = ItilMacroGenerateRequest(summary="não executar")
        session = SimpleNamespace(
            scalar=AsyncMock(side_effect=AssertionError("database must not be reached")),
            execute=AsyncMock(side_effect=AssertionError("database must not be reached")),
        )

        with patch.object(macros, "generate_itil_macro", new=AsyncMock()) as macro_provider:
            with self.assertRaises(HTTPException) as macro_error:
                await macros.generate_itil_macro_route(payload, user)
        with patch.object(imports, "analyze_import", new=AsyncMock()) as import_provider:
            with self.assertRaises(HTTPException) as import_error:
                await imports.analyze_import_with_hermes(uuid.uuid4(), session, user)

        self.assertEqual(403, macro_error.exception.status_code)
        self.assertEqual(403, import_error.exception.status_code)
        macro_provider.assert_not_awaited()
        import_provider.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
