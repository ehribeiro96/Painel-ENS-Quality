
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.dependencies.auth import get_current_user  # noqa: E402
from app.api.v1.routes import rag  # noqa: E402
from app.core.config.settings import get_settings  # noqa: E402
from app.main import app  # noqa: E402


class RagMcpMockContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = get_settings()
        self.original_overrides = dict(app.dependency_overrides)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(app.dependency_overrides.update, self.original_overrides)
        self.admin_user = SimpleNamespace(id='00000000-0000-0000-0000-000000000001', role='ADMIN')
        self.viewer_user = SimpleNamespace(id='00000000-0000-0000-0000-000000000002', role='VIEWER')

    def _auth(self, user: SimpleNamespace):
        async def _override() -> SimpleNamespace:
            return user
        return _override

    def _call_app(self, path: str, method: str = 'GET', json: dict | None = None) -> tuple[int, str]:
        import asyncio

        async def _invoke() -> tuple[int, str]:
            headers = [(b'content-type', b'application/json')] if json is not None else []
            scope = {
                'type': 'http',
                'asgi': {'version': '3.0'},
                'http_version': '1.1',
                'method': method,
                'scheme': 'http',
                'path': path,
                'raw_path': path.encode('utf-8'),
                'query_string': b'',
                'headers': headers,
                'client': ('127.0.0.1', 12345),
                'server': ('testserver', 80),
            }
            body = b'' if json is None else __import__('json').dumps(json).encode('utf-8')
            messages: list[dict[str, object]] = []

            async def receive() -> dict[str, object]:
                nonlocal body
                if body is None:
                    return {'type': 'http.request', 'body': b'', 'more_body': False}
                chunk = body
                body = None
                return {'type': 'http.request', 'body': chunk, 'more_body': False}

            async def send(message: dict[str, object]) -> None:
                messages.append(message)

            await app(scope, receive, send)
            start = next(message for message in messages if message['type'] == 'http.response.start')
            body_parts = [message['body'] for message in messages if message['type'] == 'http.response.body' and isinstance(message.get('body'), bytes | bytearray)]
            return int(start['status']), b''.join(body_parts).decode('utf-8')

        return asyncio.run(_invoke())

    def test_router_is_registered_with_rag_paths(self) -> None:
        paths = {getattr(route, 'path', '') for route in app.routes}
        self.assertIn('/api/v1/rag/collections', paths)
        self.assertIn('/api/v1/rag/search', paths)
        self.assertIn('/api/v1/rag/documents/{document_id}', paths)
        self.assertIn('/api/v1/rag/course-context/{course_id}', paths)
        self.assertIn('/api/v1/rag/audit/recent', paths)

    def test_rag_routes_require_auth_dependency(self) -> None:
        protected_paths = {
            '/rag/collections',
            '/rag/search',
            '/rag/documents/{document_id}',
            '/rag/course-context/{course_id}',
            '/rag/audit/recent',
        }
        for route in rag.router.routes:
            if getattr(route, 'path', None) in protected_paths:
                dependencies = {dependency.call for dependency in route.dependant.dependencies}
                self.assertTrue(get_current_user in dependencies or any(getattr(call, '__closure__', None) for call in dependencies), route.path)

    def test_collections_without_token_returns_missing_token(self) -> None:
        status_code, body = self._call_app('/api/v1/rag/collections')
        self.assertEqual(401, status_code)
        self.assertEqual('{"detail":"missing_token"}', body)

    def test_collections_return_allowlisted_ids_only(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app('/api/v1/rag/collections')
        self.assertEqual(200, status_code)
        self.assertIn('courses', body)
        self.assertIn('institutional', body)
        self.assertIn('marketing', body)
        self.assertIn('insights', body)
        self.assertNotIn('provider_key', body)
        self.assertNotIn('internal_path', body)

    def test_search_rejects_non_allowlisted_collection(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app('/api/v1/rag/search', method='POST', json={'query': 'ens', 'collections': ['forbidden'], 'limit': 5})
        self.assertEqual(422, status_code)
        self.assertIn('rag_collection_not_allowed', body)

    def test_search_rejects_too_large_query_and_limit(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        too_large = 'x' * 1001
        status_code, body = self._call_app('/api/v1/rag/search', method='POST', json={'query': too_large, 'limit': 5})
        self.assertEqual(422, status_code)
        self.assertIn('rag_query_too_large', body)

        status_code, body = self._call_app('/api/v1/rag/search', method='POST', json={'query': 'ens', 'limit': 50})
        self.assertEqual(422, status_code)
        self.assertIn('rag_limit_too_large', body)

    def test_search_is_deterministic_and_returns_citations(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        first_status, first_body = self._call_app('/api/v1/rag/search', method='POST', json={'query': 'curso atendimento', 'collections': ['courses', 'institutional'], 'limit': 3})
        second_status, second_body = self._call_app('/api/v1/rag/search', method='POST', json={'query': 'curso atendimento', 'collections': ['courses', 'institutional'], 'limit': 3})
        self.assertEqual(200, first_status)
        self.assertEqual(first_body, second_body)
        self.assertIn('citation', first_body)
        self.assertIn('matched_terms', first_body)

    def test_document_lookup_is_controlled_and_not_found_is_404(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app('/api/v1/rag/documents/course-onboarding-01')
        self.assertEqual(200, status_code)
        self.assertIn('course-onboarding-01', body)
        self.assertNotIn('/private/', body)

        status_code, body = self._call_app('/api/v1/rag/documents/unknown-document')
        self.assertEqual(404, status_code)
        self.assertIn('rag_document_not_found', body)

    def test_course_context_lookup_is_controlled(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app('/api/v1/rag/course-context/itil-foundations')
        self.assertEqual(200, status_code)
        self.assertIn('itil-foundations', body)
        self.assertNotIn('provider_key', body)
        self.assertNotIn('internal_path', body)

    def test_audit_recent_requires_auth_and_is_admin_restricted(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app('/api/v1/rag/audit/recent')
        self.assertEqual(403, status_code)
        self.assertIn('permission_denied', body)

        app.dependency_overrides[get_current_user] = self._auth(self.admin_user)
        status_code, body = self._call_app('/api/v1/rag/audit/recent')
        self.assertEqual(200, status_code)
        self.assertIn('rag_search', body)

    def test_no_frontend_file_calls_mcp_or_provider_directly(self) -> None:
        chat_page = (ROOT / 'frontend/itam-platform/src/apoema/pages/ChatPage.tsx').read_text(encoding='utf-8')
        api_file = (ROOT / 'frontend/itam-platform/src/apoema/lib/apoemaChatApi.ts').read_text(encoding='utf-8')
        for term in ('rag-mcp', 'ens_rag_', '/mcp/', 'vector store', 'embeddings', 'localhost:11434', '127.0.0.1:11434'):
            self.assertNotIn(term, chat_page)
            self.assertNotIn(term, api_file)


if __name__ == '__main__':
    unittest.main()
