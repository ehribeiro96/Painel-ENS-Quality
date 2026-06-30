from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.v1.dependencies.auth import get_current_user  # noqa: E402
from app.api.v1.routes import designer as designer_routes  # noqa: E402
from app.main import app  # noqa: E402
from app.services.designer_mock import reset_designer_mock_store  # noqa: E402
from app.shared.enums import Role  # noqa: E402


class DesignerMockContractTest(unittest.TestCase):
    def setUp(self) -> None:
        reset_designer_mock_store()
        self.original_overrides = dict(app.dependency_overrides)
        self.addCleanup(app.dependency_overrides.clear)
        self.addCleanup(app.dependency_overrides.update, self.original_overrides)
        self.admin_user = SimpleNamespace(id='00000000-0000-0000-0000-000000000010', role=Role.ADMIN)
        self.viewer_user = SimpleNamespace(id='00000000-0000-0000-0000-000000000020', role=Role.VIEWER)
        self.technician_user = SimpleNamespace(id='00000000-0000-0000-0000-000000000030', role=Role.TECHNICIAN)

    def _auth(self, user: SimpleNamespace):
        async def _override() -> SimpleNamespace:
            return user

        return _override

    def _call_app(self, path: str, method: str = 'GET', json_body: dict | None = None) -> tuple[int, dict[str, object] | str]:
        import asyncio

        async def _invoke() -> tuple[int, dict[str, object] | str]:
            headers = [(b'content-type', b'application/json')] if json_body is not None else []
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
            body = b'' if json_body is None else json.dumps(json_body).encode('utf-8')
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
            raw = b''.join(body_parts).decode('utf-8')
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = raw
            return int(start['status']), parsed

        return asyncio.run(_invoke())

    def test_router_is_registered_with_designer_paths(self) -> None:
        paths = {getattr(route, 'path', '') for route in app.routes}
        self.assertIn('/api/v1/designer/health', paths)
        self.assertIn('/api/v1/designer/templates', paths)
        self.assertIn('/api/v1/designer/form-options', paths)
        self.assertIn('/api/v1/designer/banners/json', paths)
        self.assertIn('/api/v1/designer/jobs/{job_id}', paths)
        self.assertIn('/api/v1/designer/jobs/{job_id}/items/{item_id}/adjust', paths)
        self.assertIn('/api/v1/designer/jobs/{job_id}/items/{item_id}/refresh-url', paths)
        self.assertIn('/api/v1/designer/jobs/{job_id}/cancel', paths)

    def test_routes_require_auth_dependency(self) -> None:
        protected_paths = {
            '/designer/health',
            '/designer/templates',
            '/designer/form-options',
            '/designer/banners/json',
            '/designer/jobs/{job_id}',
            '/designer/jobs/{job_id}/items/{item_id}/adjust',
            '/designer/jobs/{job_id}/items/{item_id}/refresh-url',
            '/designer/jobs/{job_id}/cancel',
            '/designer/banners',
            '/designer/jobs/{job_id}/download-url',
        }
        for route in designer_routes.router.routes:
            if getattr(route, 'path', None) in protected_paths:
                dependencies = {dependency.call for dependency in route.dependant.dependencies}
                self.assertTrue(get_current_user in dependencies or any(getattr(call, '__closure__', None) for call in dependencies), route.path)

    def test_auth_gate_returns_missing_token_for_publicly_accessible_paths(self) -> None:
        for path in ('/api/v1/designer/health', '/api/v1/designer/templates', '/api/v1/designer/form-options'):
            status_code, body = self._call_app(path)
            self.assertEqual(401, status_code)
            self.assertEqual({'detail': 'missing_token'}, body)

    def test_create_job_deterministic_and_server_generated(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.admin_user)
        payload = {
            'template_id': '01_feed_instagram',
            'canal': '01_feed_instagram',
            'kv': 'graduacao',
            'modo_geracao': 'peca_unica',
            'prompt': 'Campanha de matrícula com tom institucional',
            'copy': 'Inscreva-se agora',
            'box2': 'Selo mockado',
            'persona_image': 'persona.png',
            'item_count': 2,
        }
        first_status, first_body = self._call_app('/api/v1/designer/banners/json', method='POST', json_body=payload)
        second_status, second_body = self._call_app('/api/v1/designer/banners/json', method='POST', json_body=payload)
        self.assertEqual(200, first_status)
        self.assertEqual(first_body, second_body)
        self.assertEqual('completed', first_body['status'])
        self.assertEqual(self.admin_user.id, first_body['owner_user_id'])
        self.assertEqual(2, len(first_body['items']))
        self.assertEqual(100.0, first_body['progress'])
        job_id = first_body['job_id']
        self.assertIsInstance(UUID(job_id), UUID)
        self.assertNotEqual(payload['template_id'], job_id)
        for item in first_body['items']:
            self.assertIsInstance(UUID(item['item_id']), UUID)
            self.assertEqual('completed', item['status'])
            self.assertNotIn('provider_key', json.dumps(item).lower())
            self.assertNotIn('internal_path', json.dumps(item).lower())

    def test_get_job_enforces_ownership(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.admin_user)
        create_status, create_body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '02_story_instagram',
                'canal': '02_story_instagram',
                'kv': 'pos',
                'modo_geracao': 'enxoval',
                'prompt': 'Job para garantir ownership',
                'item_count': 1,
            },
        )
        self.assertEqual(200, create_status)
        job_id = create_body['job_id']

        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app(f'/api/v1/designer/jobs/{job_id}')
        self.assertEqual(403, status_code)
        self.assertEqual('designer_permission_denied', body['detail']['code'])

        app.dependency_overrides[get_current_user] = self._auth(self.admin_user)
        status_code, body = self._call_app(f'/api/v1/designer/jobs/{job_id}')
        self.assertEqual(200, status_code)
        self.assertEqual(job_id, body['job_id'])

    def test_template_and_form_options_are_allowlisted(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.viewer_user)
        status_code, body = self._call_app('/api/v1/designer/templates')
        self.assertEqual(200, status_code)
        template_ids = {item['template_id'] for item in body['items']}
        self.assertEqual({
            '01_feed_instagram',
            '02_story_instagram',
            '03_banner_interno_desktop',
            '04_banner_interno_mobile',
            '05_AIDA_whatsapp',
            '05_whatsapp',
            '08_topo_email',
        }, template_ids)
        self.assertNotIn('provider_key', json.dumps(body).lower())
        self.assertNotIn('internal_path', json.dumps(body).lower())

        status_code, body = self._call_app('/api/v1/designer/form-options')
        self.assertEqual(200, status_code)
        self.assertEqual({
            'graduacao',
            'imersoes',
            'institucional',
            'pos',
            'qualificacoes',
            'tudo-sobre-seguros',
        }, set(body['kvs']))
        self.assertEqual({'peca_unica', 'enxoval'}, set(body['modes']))
        self.assertEqual(12, body['max_items_per_job'])
        self.assertNotIn('provider_key', json.dumps(body).lower())

    def test_invalid_allowlists_and_size_limits_are_rejected(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.admin_user)

        status_code, body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': 'forbidden-template',
                'canal': '01_feed_instagram',
                'kv': 'graduacao',
                'modo_geracao': 'peca_unica',
                'prompt': 'ok',
            },
        )
        self.assertEqual(422, status_code)
        self.assertEqual('designer_template_id_not_allowed', body['detail']['code'])

        status_code, body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '01_feed_instagram',
                'canal': 'forbidden-channel',
                'kv': 'graduacao',
                'modo_geracao': 'peca_unica',
                'prompt': 'ok',
            },
        )
        self.assertEqual(422, status_code)
        self.assertEqual('designer_canal_not_allowed', body['detail']['code'])

        status_code, body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '01_feed_instagram',
                'canal': '01_feed_instagram',
                'kv': 'forbidden-kv',
                'modo_geracao': 'peca_unica',
                'prompt': 'ok',
            },
        )
        self.assertEqual(422, status_code)
        self.assertEqual('designer_kv_not_allowed', body['detail']['code'])

        status_code, body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '01_feed_instagram',
                'canal': '01_feed_instagram',
                'kv': 'graduacao',
                'modo_geracao': 'forbidden-mode',
                'prompt': 'ok',
            },
        )
        self.assertEqual(422, status_code)

        status_code, body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '01_feed_instagram',
                'canal': '01_feed_instagram',
                'kv': 'graduacao',
                'modo_geracao': 'peca_unica',
                'prompt': 'x' * 2001,
            },
        )
        self.assertEqual(422, status_code)
        self.assertEqual('designer_prompt_too_large', body['detail']['code'])

        status_code, body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '01_feed_instagram',
                'canal': '01_feed_instagram',
                'kv': 'graduacao',
                'modo_geracao': 'peca_unica',
                'prompt': 'ok',
                'copy': 'x' * 2001,
            },
        )
        self.assertEqual(422, status_code)
        self.assertEqual('designer_copy_too_large', body['detail']['code'])

    def test_adjust_refresh_and_cancel_update_mock_job(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.admin_user)
        create_status, create_body = self._call_app(
            '/api/v1/designer/banners/json',
            method='POST',
            json_body={
                'template_id': '03_banner_interno_desktop',
                'canal': '03_banner_interno_desktop',
                'kv': 'institucional',
                'modo_geracao': 'peca_unica',
                'prompt': 'Criar peça mock',
                'item_count': 1,
            },
        )
        self.assertEqual(200, create_status)
        job_id = create_body['job_id']
        item_id = create_body['items'][0]['item_id']

        status_code, body = self._call_app(
            f'/api/v1/designer/jobs/{job_id}/items/{item_id}/adjust',
            method='POST',
            json_body={'adjustment_prompt': 'Deixar o título mais curto', 'copy': 'Versão ajustada'},
        )
        self.assertEqual(200, status_code)
        self.assertEqual(1, body['items'][0]['adjusted_count'])
        self.assertIn('Mock adjustment applied', body['items'][0]['result_note'])
        self.assertEqual('Versão ajustada', body['items'][0]['copy_preview'])

        status_code, body = self._call_app(
            f'/api/v1/designer/jobs/{job_id}/items/{item_id}/refresh-url',
            method='POST',
            json_body={'reason': 'TTL expirado'},
        )
        self.assertEqual(200, status_code)
        self.assertEqual(1, body['items'][0]['refresh_count'])
        self.assertIn('Mock URL refresh acknowledged', body['items'][0]['result_note'])

        status_code, body = self._call_app(f'/api/v1/designer/jobs/{job_id}/cancel', method='POST')
        self.assertEqual(200, status_code)
        self.assertEqual('cancelled', body['status'])
        self.assertEqual(1, body['items_cancelled'])

    def test_blocked_endpoints_return_structured_blocked_errors(self) -> None:
        app.dependency_overrides[get_current_user] = self._auth(self.technician_user)
        status_code, body = self._call_app('/api/v1/designer/banners', method='POST')
        self.assertEqual(501, status_code)
        self.assertEqual('designer_feature_blocked', body['detail']['code'])

        status_code, body = self._call_app('/api/v1/designer/jobs/00000000-0000-0000-0000-000000000999/download-url')
        self.assertEqual(409, status_code)
        self.assertEqual('designer_feature_blocked', body['detail']['code'])


if __name__ == '__main__':
    unittest.main()
