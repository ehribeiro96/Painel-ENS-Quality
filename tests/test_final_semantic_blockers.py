from __future__ import annotations

import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from app.api.v1.routes import ai_chat
from app.core.config.settings import Settings
from app.domains.ai_chat.apoema import build_apoema_provider_catalog, generate_apoema_message
from app.domains.ai_chat.providers import AiProviderConfigurationError
from app.domains.ai_chat.schemas import ApoemaChatMessageCreate
from app.domains.audit.ai import record_ai_audit
from app.domains.macros.service import MacroService
from app.shared.enums import Role
from fastapi import HTTPException
from pydantic import ValidationError

STRONG_JWT = "synthetic-release-test-key-with-more-than-32-characters"


class _Session:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.commits = 0

    def add(self, value: object) -> None:
        self.added.append(value)

    async def flush(self) -> None:
        return None

    async def commit(self) -> None:
        self.commits += 1


class MockProductionBlockerTest(unittest.IsolatedAsyncioTestCase):
    def test_production_rejects_mock_as_default_provider(self) -> None:
        with self.assertRaisesRegex(ValidationError, "ai_provider_not_allowed"):
            Settings(
                environment="production",
                jwt_secret_key=STRONG_JWT,
                ai_provider="hermes",
                ai_chat_default_provider="mock",
            )

    def test_production_catalog_omits_mock(self) -> None:
        settings = Settings(
            environment="production",
            jwt_secret_key=STRONG_JWT,
            ai_provider="hermes",
            ai_chat_default_provider="hermes",
        )

        catalog = build_apoema_provider_catalog(settings)

        self.assertNotIn("mock", [provider.id for provider in catalog.providers])

    def test_unknown_or_ambiguous_environment_is_rejected(self) -> None:
        for environment in ("", "test", " production ", "PRODUCTION"):
            with self.subTest(environment=environment):
                with self.assertRaises(ValidationError):
                    Settings(environment=environment)

    async def test_production_request_never_instantiates_mock(self) -> None:
        settings = Settings(
            environment="production",
            jwt_secret_key=STRONG_JWT,
            ai_provider="hermes",
            ai_chat_default_provider="hermes",
        )
        payload = ApoemaChatMessageCreate(
            provider="mock",
            model="fallback-local",
            message="synthetic",
        )

        with patch("app.domains.ai_chat.apoema.MockAiProvider") as mock_provider:
            with self.assertRaisesRegex(AiProviderConfigurationError, "ai_provider_not_allowed"):
                await generate_apoema_message(settings, payload)

        mock_provider.assert_not_called()

    async def test_local_mock_requires_explicit_enablement(self) -> None:
        disabled = Settings(
            environment="local",
            ai_provider="hermes",
            ai_chat_default_provider="hermes",
            ai_mock_enabled=False,
        )
        enabled = Settings(environment="local", ai_mock_enabled=True)
        payload = ApoemaChatMessageCreate(provider="mock", model="fallback-local", message="synthetic")

        with self.assertRaisesRegex(AiProviderConfigurationError, "ai_provider_not_allowed"):
            await generate_apoema_message(disabled, payload)
        response = await generate_apoema_message(enabled, payload)

        self.assertEqual("mock", response.provider)

    async def test_route_rejects_mock_with_denied_audit_before_provider(self) -> None:
        payload = ApoemaChatMessageCreate(provider="mock", model="fallback-local", message="synthetic")
        session = _Session()
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.TECHNICIAN)
        original = (ai_chat.settings.environment, ai_chat.settings.ai_mock_enabled, ai_chat.settings.enable_ai_chat)
        ai_chat.settings.environment = "production"
        ai_chat.settings.ai_mock_enabled = False
        ai_chat.settings.enable_ai_chat = True
        try:
            with patch.object(ai_chat, "generate_apoema_message") as generate:
                with self.assertRaises(HTTPException) as raised:
                    await ai_chat.send_apoema_message(payload, user, session)
        finally:
            ai_chat.settings.environment, ai_chat.settings.ai_mock_enabled, ai_chat.settings.enable_ai_chat = original

        self.assertEqual(403, raised.exception.status_code)
        self.assertEqual("ai_provider_not_allowed", raised.exception.detail)
        self.assertEqual(1, session.commits)
        self.assertEqual(["DENIED", "DENIED"], [item.after["status"] for item in session.added])
        generate.assert_not_called()


class AiAuditInputBlockerTest(unittest.IsolatedAsyncioTestCase):
    def test_hostile_model_and_conversation_identifiers_are_rejected_by_schema(self) -> None:
        hostile_models = ("model\r\nforged", "model;forged", "x" * 129)
        for model in hostile_models:
            with self.subTest(model=model[:20]):
                with self.assertRaises(ValidationError):
                    ApoemaChatMessageCreate(provider="hermes", model=model, message="synthetic")

        for conversation_id in ("not-a-uuid", "id\r\nforged", "x" * 200):
            with self.subTest(conversation_id=conversation_id[:20]):
                with self.assertRaises(ValidationError):
                    ApoemaChatMessageCreate(
                        conversation_id=conversation_id,
                        provider="hermes",
                        model="hermes-agent",
                        message="synthetic",
                    )

    async def test_unknown_model_is_rejected_before_provider_execution(self) -> None:
        settings = Settings(environment="local", ai_provider="hermes", ai_chat_default_provider="hermes")
        payload = ApoemaChatMessageCreate(provider="hermes", model="unknown-model", message="synthetic")

        with patch("app.domains.ai_chat.apoema.HermesTerminalProvider") as provider:
            with self.assertRaisesRegex(AiProviderConfigurationError, "ai_model_not_allowed"):
                await generate_apoema_message(settings, payload)

        provider.assert_not_called()

    async def test_audit_rejects_noncanonical_identifiers_defense_in_depth(self) -> None:
        session = _Session()
        user = SimpleNamespace(id=uuid.uuid4(), role=Role.TECHNICIAN)

        with self.assertRaisesRegex(ValueError, "invalid_ai_audit_identifier"):
            await record_ai_audit(
                session,
                event="CHAT_MESSAGE",
                user=user,
                provider="hermes\r\nforged",
                model="model;forged",
                resource_type="ChatConversation",
                resource_id=uuid.uuid4(),
                status="FAILED",
                duration_ms=1,
            )

        self.assertEqual([], session.added)

    def test_valid_uuid_conversation_identifier_is_canonical(self) -> None:
        conversation_id = uuid.uuid4()
        payload = ApoemaChatMessageCreate(
            conversation_id=conversation_id,
            provider="hermes",
            model="hermes-agent",
            message="synthetic",
        )

        self.assertEqual(conversation_id, payload.conversation_id)


class ReservedMovementMacroBlockerTest(unittest.IsolatedAsyncioTestCase):
    def test_generic_schema_rejects_reserved_movement_context(self) -> None:
        from app.domains.macros.schemas import MacroGenerateRequest

        with self.assertRaisesRegex(ValidationError, "reserved_context_requires_official_endpoint"):
            MacroGenerateRequest(
                template_id=uuid.uuid4(),
                values={},
                context_type="asset_movement",
                context_id=uuid.uuid4(),
            )

    async def test_service_rejects_reserved_movement_context_before_persistence(self) -> None:
        session = _Session()
        template = SimpleNamespace(
            id=uuid.uuid4(),
            template_text="Patrimônio: {Patrimônio}",
            required_fields=[],
        )

        with self.assertRaisesRegex(ValueError, "reserved_context_requires_official_endpoint"):
            await MacroService(session).generate(
                template,
                {"Patrimônio": "SYNTHETIC-001"},
                uuid.uuid4(),
                context_type="asset_movement",
                context_id=uuid.uuid4(),
            )

        self.assertEqual([], session.added)

    async def test_nonexistent_movement_never_creates_generation(self) -> None:
        class MissingMovementSession(_Session):
            async def scalar(self, statement):  # noqa: ANN001, ANN201, ARG002
                return None

        session = MissingMovementSession()
        with self.assertRaisesRegex(LookupError, "movement_not_found"):
            await MacroService(session).generate_for_movement(uuid.uuid4(), uuid.uuid4())
        self.assertEqual([], session.added)


if __name__ == "__main__":
    unittest.main()
