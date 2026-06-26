from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
FRONTEND = ROOT / 'frontend' / 'itam-platform' / 'src'
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.domains.designer import (  # noqa: E402
    ALLOWED_CHANNELS,
    ALLOWED_KVS,
    ALLOWED_MODES,
    ALLOWED_TEMPLATES,
    DesignerAdjustItemRequest,
    DesignerBannerJsonRequest,
    DesignerCancelResponse,
    DesignerError,
    DesignerFormOptionsResponse,
    DesignerHealthDTO,
    DesignerJobDTO,
    DesignerJobItemDTO,
    DesignerRefreshUrlRequest,
    DesignerTemplateDTO,
    DesignerTemplatesResponse,
)
from app.services import designer_mock  # noqa: E402


class DesignerMockSecurityTest(unittest.TestCase):
    def test_dtos_do_not_expose_provider_keys_or_internal_paths(self) -> None:
        self.assertNotIn('provider_key', DesignerBannerJsonRequest.model_fields)
        self.assertNotIn('provider_key', DesignerAdjustItemRequest.model_fields)
        self.assertNotIn('provider_key', DesignerRefreshUrlRequest.model_fields)
        self.assertNotIn('provider_key', DesignerJobDTO.model_fields)
        self.assertNotIn('provider_key', DesignerJobItemDTO.model_fields)
        self.assertNotIn('provider_key', DesignerTemplatesResponse.model_fields)
        self.assertNotIn('provider_key', DesignerFormOptionsResponse.model_fields)
        self.assertNotIn('provider_key', DesignerHealthDTO.model_fields)
        self.assertNotIn('provider_key', DesignerError.model_fields)
        self.assertNotIn('internal_path', DesignerBannerJsonRequest.model_fields)
        self.assertNotIn('internal_path', DesignerJobDTO.model_fields)
        self.assertNotIn('internal_path', DesignerJobItemDTO.model_fields)

        payloads = [
            DesignerError.model_construct(code='designer_error', message='safe', details={}),
            DesignerHealthDTO.model_construct(
                status='ok',
                service='designer-mock-adapter',
                mode='M4B_MOCK_BACKEND_ADAPTER',
                deterministic=True,
                provider_real_enabled=False,
                template_count=7,
                job_count=0,
                note='Mock adapter.',
            ),
            DesignerTemplateDTO.model_construct(
                template_id='01_feed_instagram',
                canal='01_feed_instagram',
                kv='graduacao',
                label='Feed Instagram · Graduação',
                description='Mock template',
                mode_options=['peca_unica', 'enxoval'],
                box2_allowed=True,
                persona_image_allowed=True,
                prompt_budget=2000,
                copy_budget=2000,
            ),
            DesignerTemplatesResponse.model_construct(items=[], total=0),
            DesignerFormOptionsResponse.model_construct(
                channels=list(ALLOWED_CHANNELS),
                kvs=list(ALLOWED_KVS),
                modes=list(ALLOWED_MODES),
                template_ids=list(ALLOWED_TEMPLATES),
                supports_box2=True,
                supports_persona_image=True,
                max_prompt_length=2000,
                max_copy_length=2000,
                max_items_per_job=12,
            ),
            DesignerJobItemDTO.model_construct(
                item_id='00000000-0000-0000-0000-000000000001',
                template_id='01_feed_instagram',
                title='01_feed_instagram · item 1',
                status='completed',
                copy_preview='copy',
                prompt_preview='prompt',
                result_note='safe',
                adjusted_count=0,
                refresh_count=0,
                created_at=datetime(2026, 6, 26, tzinfo=UTC),
                updated_at=datetime(2026, 6, 26, tzinfo=UTC),
                error=None,
            ),
            DesignerJobDTO.model_construct(
                job_id='00000000-0000-0000-0000-000000000100',
                owner_user_id='00000000-0000-0000-0000-000000000101',
                status='completed',
                created_at=datetime(2026, 6, 26, tzinfo=UTC),
                updated_at=datetime(2026, 6, 26, tzinfo=UTC),
                template_id='01_feed_instagram',
                canal='01_feed_instagram',
                kv='graduacao',
                modo_geracao='peca_unica',
                box2=None,
                persona_image_present=False,
                prompt_preview='prompt',
                copy_preview='copy',
                progress=100.0,
                items=[],
                summary='safe',
                error=None,
            ),
            DesignerCancelResponse.model_construct(
                job_id='00000000-0000-0000-0000-000000000102',
                status='cancelled',
                cancelled_at=datetime(2026, 6, 26, tzinfo=UTC),
                items_cancelled=1,
                message='safe',
            ),
        ]
        for payload in payloads:
            text = payload.model_dump_json()
            for term in (
                'provider_key',
                'model_secret',
                'internal_path',
                'storage_path',
                'private/',
                '/tmp/',
                'secret',
                'token',
            ):
                self.assertNotIn(term.lower(), text.lower())

    def test_service_allowlists_and_limits_are_defined(self) -> None:
        self.assertEqual(2000, designer_mock.MAX_ALLOWED_PROMPT_LENGTH)
        self.assertEqual(2000, designer_mock.MAX_ALLOWED_COPY_LENGTH)
        self.assertEqual(12, designer_mock.MAX_ALLOWED_ITEMS)
        self.assertEqual(set(ALLOWED_TEMPLATES), set(designer_mock.ALLOWED_TEMPLATES))
        self.assertEqual(set(ALLOWED_CHANNELS), set(designer_mock.ALLOWED_CHANNELS))
        self.assertEqual(set(ALLOWED_KVS), set(designer_mock.ALLOWED_KVS))
        self.assertEqual(set(ALLOWED_MODES), set(designer_mock.ALLOWED_MODES))

    def test_service_is_deterministic_without_network_or_storage(self) -> None:
        designer_mock.reset_designer_mock_store()
        request = DesignerBannerJsonRequest.model_validate(
            {
                'template_id': '01_feed_instagram',
                'canal': '01_feed_instagram',
                'kv': 'graduacao',
                'modo_geracao': 'peca_unica',
                'prompt': 'Campanha institucional',
                'copy': 'Texto base',
                'item_count': 2,
            }
        )
        first = designer_mock.create_banner_job(request, 'user-1')
        second = designer_mock.create_banner_job(request, 'user-1')
        self.assertEqual(first.model_dump(), second.model_dump())
        self.assertEqual('completed', first.status)
        self.assertTrue(first.persona_image_present is False)
        self.assertEqual(2, len(first.items))
        self.assertTrue(all(item.status == 'completed' for item in first.items))

    def test_frontend_does_not_call_provider_directly(self) -> None:
        api_file = (FRONTEND / 'lib' / 'api.ts').read_text(encoding='utf-8')
        apoema_api_file = (FRONTEND / 'apoema' / 'lib' / 'apoemaChatApi.ts').read_text(encoding='utf-8')
        for text in (api_file, apoema_api_file):
            for term in (
                'api.openai.com',
                'generativelanguage.googleapis.com',
                'localhost:11434',
                '127.0.0.1:11434',
                '/v1beta/models/',
                'imagen',
                'vertex',
            ):
                self.assertNotIn(term, text.lower())
            self.assertIn('fetch(`${API_BASE}${path}`', text)


if __name__ == '__main__':
    unittest.main()
