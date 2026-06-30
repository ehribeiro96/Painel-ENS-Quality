from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]


class ArtifactContractTest(unittest.TestCase):
    def _call_app(self, path: str, method: str = 'GET', headers: dict[str, str] | None = None) -> tuple[int, str]:
        import sys

        backend_path = str(ROOT / 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.main import app

        async def _invoke() -> tuple[int, str]:
            raw_headers = [(key.lower().encode('latin-1'), value.encode('latin-1')) for key, value in (headers or {}).items()]
            scope = {
                'type': 'http',
                'asgi': {'version': '3.0'},
                'http_version': '1.1',
                'method': method,
                'scheme': 'http',
                'path': path,
                'raw_path': path.encode('utf-8'),
                'query_string': b'',
                'headers': raw_headers,
                'client': ('127.0.0.1', 12345),
                'server': ('testserver', 80),
            }
            messages: list[dict[str, object]] = []

            async def receive() -> dict[str, object]:
                return {'type': 'http.request', 'body': b'', 'more_body': False}

            async def send(message: dict[str, object]) -> None:
                messages.append(message)

            await app(scope, receive, send)
            start = next(message for message in messages if message['type'] == 'http.response.start')
            body_parts = [cast(bytes, message['body']) for message in messages if message['type'] == 'http.response.body' and isinstance(message.get('body'), bytes | bytearray)]
            return int(cast(int, start['status'])), b''.join(body_parts).decode('utf-8')

        return asyncio.run(_invoke())

    def test_artifact_router_is_registered_and_auth_protected(self) -> None:
        import sys

        backend_path = str(ROOT / 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.api.v1.dependencies.auth import get_current_user, get_optional_current_user
        from app.main import app

        routes = {getattr(route, 'path', ''): route for route in app.routes}
        self.assertIn('/api/v1/artifacts', routes)
        self.assertIn('/api/v1/artifacts/{artifact_id}', routes)
        self.assertIn('/api/v1/artifacts/{artifact_id}/download-url', routes)
        self.assertIn('/api/v1/artifacts/download/{signed_token}', routes)

        def dependency_calls(path: str, method: str) -> set[object]:
            route = next(r for r in app.routes if getattr(r, 'path', '') == path and method in getattr(r, 'methods', set()))
            return {dep.call for dep in route.dependant.dependencies}

        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts', 'POST'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts', 'GET'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts/{artifact_id}', 'GET'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts/{artifact_id}/download-url', 'GET'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts/{artifact_id}', 'DELETE'))
        self.assertIn(get_optional_current_user, dependency_calls('/api/v1/artifacts/download/{signed_token}', 'GET'))

    def test_artifact_list_without_token_returns_unauthorized(self) -> None:
        status_code, body = self._call_app('/api/v1/artifacts')

        self.assertEqual(401, status_code)
        self.assertEqual('{"detail":"missing_token"}', body)

    def test_artifact_storage_is_not_public_static(self) -> None:
        import sys

        backend_path = str(ROOT / 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.main import app

        route_paths = {getattr(route, 'path', '') for route in app.routes}
        self.assertNotIn('/data/artifacts/private', route_paths)
        self.assertNotIn('/data/artifacts/metadata.json', route_paths)
        self.assertNotIn('/files', route_paths)


if __name__ == '__main__':
    unittest.main()
