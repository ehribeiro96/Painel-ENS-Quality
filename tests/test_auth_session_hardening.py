from __future__ import annotations

import unittest
import uuid

from app.api.v1.routes import auth
from app.core.database import base as _database_base  # noqa: F401
from app.domains.auth.models import AuthSession
from app.domains.auth.service import AuthSessionService, hash_refresh_token
from app.shared.models import utc_now
from fastapi import Response


class _Session:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.last_statement = None

    def add(self, entity: object) -> None:
        if getattr(entity, "id", None) is None:
            entity.id = uuid.uuid4()
        self.added.append(entity)

    async def flush(self) -> None:
        return None

    async def scalar(self, statement):  # noqa: ANN001
        self.last_statement = statement
        return None


class AuthSessionHardeningTest(unittest.IsolatedAsyncioTestCase):
    def test_refresh_cookie_is_http_only_secure_and_scoped(self) -> None:
        original_secure = auth.settings.refresh_cookie_secure
        original_samesite = auth.settings.refresh_cookie_samesite
        auth.settings.refresh_cookie_secure = True
        auth.settings.refresh_cookie_samesite = "strict"
        try:
            response = Response()
            auth._set_refresh_cookie(response, "test-only-refresh-token")
        finally:
            auth.settings.refresh_cookie_secure = original_secure
            auth.settings.refresh_cookie_samesite = original_samesite

        cookie = response.headers["set-cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Secure", cookie)
        self.assertIn("SameSite=strict", cookie)
        self.assertIn("Path=/api/v1/auth", cookie)

    async def test_refresh_lookup_enforces_not_revoked_and_not_expired(self) -> None:
        session = _Session()

        await AuthSessionService(session).get_active_by_refresh_token("test-token")

        statement = str(session.last_statement)
        self.assertIn("auth_sessions.revoked_at IS NULL", statement)
        self.assertIn("auth_sessions.expires_at >", statement)
        self.assertNotIn("test-token", statement)

    async def test_refresh_rotation_revokes_old_session_and_hashes_new_token(self) -> None:
        session = _Session()
        user_id = uuid.uuid4()
        old_session = AuthSession(
            id=uuid.uuid4(),
            user_id=user_id,
            refresh_token_hash=hash_refresh_token("old-token"),
            expires_at=utc_now(),
        )

        new_session, new_token = await AuthSessionService(session).rotate(
            auth_session=old_session,
            user_agent="test",
            ip_address="127.0.0.1",
        )

        self.assertIsNotNone(old_session.revoked_at)
        self.assertEqual(new_session.id, old_session.replaced_by_session_id)
        self.assertNotEqual(new_token, new_session.refresh_token_hash)
        self.assertEqual(hash_refresh_token(new_token), new_session.refresh_token_hash)


if __name__ == "__main__":
    unittest.main()
