from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import RLock
from uuid import NAMESPACE_URL, uuid5

from app.domains.designer.schemas import (
    ALLOWED_CHANNELS,
    ALLOWED_KVS,
    ALLOWED_MODES,
    ALLOWED_TEMPLATES,
    MAX_COPY_LENGTH,
    MAX_ITEMS_PER_JOB,
    MAX_PROMPT_LENGTH,
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

SERVICE_NAME = 'designer-mock-adapter'
SERVICE_MODE = 'M4B_MOCK_BACKEND_ADAPTER'
PROVIDER_REAL_ENABLED = False
DETERMINISTIC = True
DEFAULT_STATUS = 'completed'
DEFAULT_ITEM_STATUS = 'completed'
WRITE_ROLES = {'ADMIN', 'TECHNICIAN', 'MANAGER'}
BLOCKED_ERROR_CODE = 'designer_feature_blocked'
MAX_ALLOWED_ITEMS = MAX_ITEMS_PER_JOB
MAX_ALLOWED_PROMPT_LENGTH = MAX_PROMPT_LENGTH
MAX_ALLOWED_COPY_LENGTH = MAX_COPY_LENGTH
FIXED_NOW = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)


@dataclass(frozen=True)
class DesignerMockError(Exception):
    error: DesignerError
    status_code: int = 422

    def __post_init__(self) -> None:
        super().__init__(self.error.message)


_TEMPLATE_CATALOG: tuple[dict[str, object], ...] = (
    {
        'template_id': '01_feed_instagram',
        'canal': '01_feed_instagram',
        'kv': 'graduacao',
        'label': 'Feed Instagram · Graduação',
        'description': 'Mock determinístico de peça para feed do Instagram, sem provider real.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
    {
        'template_id': '02_story_instagram',
        'canal': '02_story_instagram',
        'kv': 'pos',
        'label': 'Story Instagram · Pós-graduação',
        'description': 'Mock determinístico para story vertical com catálogo backend-owned.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
    {
        'template_id': '03_banner_interno_desktop',
        'canal': '03_banner_interno_desktop',
        'kv': 'institucional',
        'label': 'Banner interno desktop',
        'description': 'Banner corporativo mockado para uso interno do painel.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
    {
        'template_id': '04_banner_interno_mobile',
        'canal': '04_banner_interno_mobile',
        'kv': 'institucional',
        'label': 'Banner interno mobile',
        'description': 'Variante mobile mockada, sem geração real de imagem.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
    {
        'template_id': '05_AIDA_whatsapp',
        'canal': '05_AIDA_whatsapp',
        'kv': 'qualificacoes',
        'label': 'AIDA WhatsApp',
        'description': 'Fluxo AIDA mockado para validação textual de campanhas.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
    {
        'template_id': '05_whatsapp',
        'canal': '05_whatsapp',
        'kv': 'tudo-sobre-seguros',
        'label': 'WhatsApp institucional',
        'description': 'Template de WhatsApp allowlisted para mock determinístico.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
    {
        'template_id': '08_topo_email',
        'canal': '08_topo_email',
        'kv': 'institucional',
        'label': 'Topo de e-mail',
        'description': 'Cabeçalho de e-mail mockado para testes de contrato.',
        'mode_options': ['peca_unica', 'enxoval'],
    },
)

_FORM_OPTIONS = DesignerFormOptionsResponse(
    channels=list(ALLOWED_CHANNELS),
    kvs=list(ALLOWED_KVS),
    modes=list(ALLOWED_MODES),
    template_ids=list(ALLOWED_TEMPLATES),
    supports_box2=True,
    supports_persona_image=True,
    max_prompt_length=MAX_ALLOWED_PROMPT_LENGTH,
    max_copy_length=MAX_ALLOWED_COPY_LENGTH,
    max_items_per_job=MAX_ALLOWED_ITEMS,
)


def _role_value(role: object) -> str:
    return str(getattr(role, 'value', role))


def _preview(text: str | None, *, limit: int = 120) -> str:
    if not text:
        return ''
    normalized = ' '.join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 1)].rstrip() + '…'


def _now_for_offset(offset_seconds: int) -> datetime:
    return FIXED_NOW + timedelta(seconds=offset_seconds)


def _raise(code: str, message: str, *, status_code: int = 422, details: dict[str, object] | None = None) -> None:
    raise DesignerMockError(error=DesignerError(code=code, message=message, details=details or {}), status_code=status_code)


def _ensure_allowed(value: str, allowed: Iterable[str], field_name: str) -> str:
    normalized = value.strip()
    if normalized not in set(allowed):
        _raise(
            code=f'designer_{field_name}_not_allowed',
            message=f'{field_name} not allowed',
            details={field_name: normalized},
        )
    return normalized


def _ensure_length(value: str | None, *, field_name: str, maximum: int, required: bool = False) -> str | None:
    if value is None:
        if required:
            _raise(code=f'designer_{field_name}_required', message=f'{field_name} is required')
        return None
    normalized = value.strip()
    if not normalized:
        if required:
            _raise(code=f'designer_{field_name}_required', message=f'{field_name} is required')
        return None
    if len(normalized) > maximum:
        _raise(
            code=f'designer_{field_name}_too_large',
            message=f'{field_name} exceeds maximum length',
            details={'field': field_name, 'maximum': maximum},
        )
    return normalized


class DesignerMockStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._jobs_by_id: dict[str, DesignerJobDTO] = {}
        self._jobs_by_fingerprint: dict[str, str] = {}
        self._event_log: list[dict[str, object]] = []
        self._mutation_sequence = 0

    def reset(self) -> None:
        with self._lock:
            self._jobs_by_id.clear()
            self._jobs_by_fingerprint.clear()
            self._event_log.clear()
            self._mutation_sequence = 0

    def health(self) -> DesignerHealthDTO:
        with self._lock:
            return DesignerHealthDTO(
                status='ok',
                service=SERVICE_NAME,
                mode=SERVICE_MODE,
                deterministic=DETERMINISTIC,
                provider_real_enabled=PROVIDER_REAL_ENABLED,
                template_count=len(_TEMPLATE_CATALOG),
                job_count=len(self._jobs_by_id),
                note='Mock backend deterministic adapter. No provider, image generation, or blob output is enabled.',
            )

    def list_templates(self) -> DesignerTemplatesResponse:
        return DesignerTemplatesResponse(
            items=[DesignerTemplateDTO.model_validate(item) for item in _TEMPLATE_CATALOG],
            total=len(_TEMPLATE_CATALOG),
        )

    def form_options(self) -> DesignerFormOptionsResponse:
        return _FORM_OPTIONS.model_copy(deep=True)

    def create_banner_job(self, request: DesignerBannerJsonRequest, owner_user_id: object) -> DesignerJobDTO:
        normalized_owner = str(owner_user_id)
        template_id = _ensure_allowed(request.template_id, ALLOWED_TEMPLATES, 'template_id')
        canal = _ensure_allowed(request.canal, ALLOWED_CHANNELS, 'canal')
        kv = _ensure_allowed(request.kv, ALLOWED_KVS, 'kv')
        modo_geracao = _ensure_allowed(request.modo_geracao, ALLOWED_MODES, 'modo_geracao')
        prompt = _ensure_length(request.prompt, field_name='prompt', maximum=MAX_ALLOWED_PROMPT_LENGTH, required=True) or ''
        copy_text = _ensure_length(request.copy_text, field_name='copy', maximum=MAX_ALLOWED_COPY_LENGTH)
        box2 = _ensure_length(request.box2, field_name='box2', maximum=MAX_ALLOWED_COPY_LENGTH)
        persona_image = _ensure_length(request.persona_image, field_name='persona_image', maximum=MAX_ALLOWED_COPY_LENGTH)
        item_count = int(request.item_count)
        if item_count > MAX_ALLOWED_ITEMS:
            _raise(
                code='designer_item_count_too_large',
                message='item_count exceeds maximum',
                details={'maximum': MAX_ALLOWED_ITEMS},
            )

        fingerprint_payload = {
            'owner_user_id': normalized_owner,
            'template_id': template_id,
            'canal': canal,
            'kv': kv,
            'modo_geracao': modo_geracao,
            'prompt': prompt,
            'copy': copy_text,
            'box2': box2,
            'persona_image': persona_image,
            'item_count': item_count,
        }
        fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
        with self._lock:
            existing_job_id = self._jobs_by_fingerprint.get(fingerprint)
            if existing_job_id is not None:
                return self._jobs_by_id[existing_job_id].model_copy(deep=True)

            job_id = str(uuid5(NAMESPACE_URL, f'designer-job:{fingerprint}'))
            created_at = _now_for_offset(int(fingerprint[:8], 16) % 7200)
            items = self._build_items(job_id=job_id, template_id=template_id, prompt=prompt, copy_text=copy_text, item_count=item_count, created_at=created_at)
            job = DesignerJobDTO(
                job_id=job_id,
                owner_user_id=normalized_owner,
                status=DEFAULT_STATUS,
                created_at=created_at,
                updated_at=created_at,
                template_id=template_id,
                canal=canal,
                kv=kv,
                modo_geracao=modo_geracao,  # type: ignore[arg-type]
                box2=box2,
                persona_image_present=bool(persona_image),
                prompt_preview=_preview(prompt, limit=160),
                copy_preview=_preview(copy_text or prompt, limit=160),
                progress=100.0,
                items=items,
                summary=self._summarize_job(template_id=template_id, canal=canal, kv=kv, item_count=item_count, prompt=prompt),
                error=None,
            )
            self._jobs_by_id[job_id] = job
            self._jobs_by_fingerprint[fingerprint] = job_id
            self._event_log.append({'event': 'create', 'job_id': job_id, 'owner_user_id': normalized_owner, 'template_id': template_id})
            return job.model_copy(deep=True)

    def get_job(self, job_id: object, current_user: object) -> DesignerJobDTO:
        job = self._lookup_job(job_id)
        self._ensure_access(job, current_user, action='read')
        return job.model_copy(deep=True)

    def adjust_item(self, job_id: object, item_id: object, request: DesignerAdjustItemRequest, current_user: object) -> DesignerJobDTO:
        job = self._lookup_job(job_id)
        self._ensure_access(job, current_user, action='adjust')
        item = self._lookup_item(job, item_id)
        adjustment_prompt = _ensure_length(request.adjustment_prompt, field_name='adjustment_prompt', maximum=MAX_ALLOWED_PROMPT_LENGTH, required=True) or ''
        copy_text = _ensure_length(request.copy_text, field_name='copy', maximum=MAX_ALLOWED_COPY_LENGTH)
        box2 = _ensure_length(request.box2, field_name='box2', maximum=MAX_ALLOWED_COPY_LENGTH)

        with self._lock:
            self._mutation_sequence += 1
            item.adjusted_count += 1
            item.updated_at = _now_for_offset(self._mutation_sequence)
            item.status = DEFAULT_ITEM_STATUS  # type: ignore[assignment]
            if copy_text is not None:
                item.copy_preview = _preview(copy_text, limit=160)
            if box2 is not None:
                item.result_note = f'Mock adjustment applied: {_preview(adjustment_prompt, limit=100)} | box2={_preview(box2, limit=60)}'
            else:
                item.result_note = f'Mock adjustment applied: {_preview(adjustment_prompt, limit=120)}'
            job.updated_at = item.updated_at
            job.summary = self._summarize_job(
                template_id=job.template_id,
                canal=job.canal,
                kv=job.kv,
                item_count=len(job.items),
                prompt=job.prompt_preview,
                suffix='adjusted',
            )
            self._event_log.append({'event': 'adjust', 'job_id': job.job_id, 'item_id': item.item_id})
            return job.model_copy(deep=True)

    def refresh_item_url(self, job_id: object, item_id: object, request: DesignerRefreshUrlRequest, current_user: object) -> DesignerJobDTO:
        job = self._lookup_job(job_id)
        self._ensure_access(job, current_user, action='refresh-url')
        item = self._lookup_item(job, item_id)
        reason = _ensure_length(request.reason, field_name='reason', maximum=MAX_ALLOWED_COPY_LENGTH)
        with self._lock:
            self._mutation_sequence += 1
            item.refresh_count += 1
            item.updated_at = _now_for_offset(self._mutation_sequence)
            item.result_note = f'Mock URL refresh acknowledged{f": {_preview(reason, limit=80)}" if reason else ""}. No artifact blob was generated.'
            job.updated_at = item.updated_at
            self._event_log.append({'event': 'refresh-url', 'job_id': job.job_id, 'item_id': item.item_id})
            return job.model_copy(deep=True)

    def cancel_job(self, job_id: object, current_user: object) -> DesignerCancelResponse:
        job = self._lookup_job(job_id)
        self._ensure_access(job, current_user, action='cancel')
        with self._lock:
            self._mutation_sequence += 1
            cancelled_at = _now_for_offset(self._mutation_sequence)
            for item in job.items:
                item.status = 'cancelled'
                item.updated_at = cancelled_at
                item.result_note = 'Job cancelled by backend mock adapter.'
            job.status = 'cancelled'
            job.updated_at = cancelled_at
            job.progress = 0.0
            job.summary = 'Mock job cancelled before any real provider or blob output was invoked.'
            self._event_log.append({'event': 'cancel', 'job_id': job.job_id, 'items_cancelled': len(job.items)})
            return DesignerCancelResponse(
                job_id=job.job_id,
                status=job.status,
                cancelled_at=cancelled_at,
                items_cancelled=len(job.items),
                message='Designer job cancelled in mock store.',
            )

    def blocked_banner_upload(self) -> None:
        _raise(
            code=BLOCKED_ERROR_CODE,
            message='Multipart banner creation is blocked in the mock adapter phase',
            status_code=501,
            details={'endpoint': '/api/v1/designer/banners'},
        )

    def blocked_download_url(self, job_id: object) -> None:
        _raise(
            code=BLOCKED_ERROR_CODE,
            message='Download URL requires artifact-backed output and is blocked in this phase',
            status_code=409,
            details={'job_id': str(job_id), 'endpoint': '/api/v1/designer/jobs/{job_id}/download-url'},
        )

    def _ensure_access(self, job: DesignerJobDTO, current_user: object, *, action: str) -> None:
        current_user_id = str(getattr(current_user, 'id', current_user))
        current_role = _role_value(getattr(current_user, 'role', ''))
        if current_user_id == job.owner_user_id:
            return
        if current_role == 'ADMIN':
            return
        _raise(
            code='designer_permission_denied',
            message=f'permission denied for {action}',
            status_code=403,
            details={'job_id': job.job_id, 'action': action},
        )

    def _lookup_job(self, job_id: object) -> DesignerJobDTO:
        normalized_job_id = str(job_id)
        with self._lock:
            job = self._jobs_by_id.get(normalized_job_id)
            if job is None:
                _raise(
                    code='designer_job_not_found',
                    message='designer job not found',
                    status_code=404,
                    details={'job_id': normalized_job_id},
                )
                raise AssertionError('unreachable')
            return job

    def _lookup_item(self, job: DesignerJobDTO, item_id: object) -> DesignerJobItemDTO:
        normalized_item_id = str(item_id)
        for item in job.items:
            if item.item_id == normalized_item_id:
                return item
        _raise(
            code='designer_item_not_found',
            message='designer item not found',
            status_code=404,
            details={'job_id': job.job_id, 'item_id': normalized_item_id},
        )
        raise AssertionError('unreachable')

    def _build_items(
        self,
        *,
        job_id: str,
        template_id: str,
        prompt: str,
        copy_text: str | None,
        item_count: int,
        created_at: datetime,
    ) -> list[DesignerJobItemDTO]:
        items: list[DesignerJobItemDTO] = []
        for index in range(1, item_count + 1):
            item_seed = f'{job_id}:{template_id}:{index}:{prompt}:{copy_text or ""}'
            item_id = str(uuid5(NAMESPACE_URL, f'designer-job-item:{item_seed}'))
            item_created_at = created_at + timedelta(seconds=index)
            items.append(
                DesignerJobItemDTO(
                    item_id=item_id,
                    template_id=template_id,
                    title=f'{template_id} · item {index}',
                    status=DEFAULT_ITEM_STATUS,  # type: ignore[arg-type]
                    copy_preview=_preview(copy_text or prompt, limit=160),
                    prompt_preview=_preview(prompt, limit=160),
                    result_note='Mock item completed deterministically. No provider, image, or blob output used.',
                    adjusted_count=0,
                    refresh_count=0,
                    created_at=item_created_at,
                    updated_at=item_created_at,
                    error=None,
                )
            )
        return items

    def _summarize_job(
        self,
        *,
        template_id: str,
        canal: str,
        kv: str,
        item_count: int,
        prompt: str,
        suffix: str | None = None,
    ) -> str:
        base = f'Mock job {template_id}/{canal}/{kv} with {item_count} item(s). Prompt preview: {_preview(prompt, limit=80)}.'
        if suffix:
            return f'{base} Status note: {suffix}.'
        return base + ' No real provider, image generation, or blob output was produced.'


STORE = DesignerMockStore()


def reset_designer_mock_store() -> None:
    STORE.reset()


def health() -> DesignerHealthDTO:
    return STORE.health()


def list_templates() -> DesignerTemplatesResponse:
    return STORE.list_templates()


def form_options() -> DesignerFormOptionsResponse:
    return STORE.form_options()


def create_banner_job(request: DesignerBannerJsonRequest, current_user: object) -> DesignerJobDTO:
    return STORE.create_banner_job(request, current_user)


def get_job(job_id: object, current_user: object) -> DesignerJobDTO:
    return STORE.get_job(job_id, current_user)


def adjust_item(job_id: object, item_id: object, request: DesignerAdjustItemRequest, current_user: object) -> DesignerJobDTO:
    return STORE.adjust_item(job_id, item_id, request, current_user)


def refresh_item_url(job_id: object, item_id: object, request: DesignerRefreshUrlRequest, current_user: object) -> DesignerJobDTO:
    return STORE.refresh_item_url(job_id, item_id, request, current_user)


def cancel_job(job_id: object, current_user: object) -> DesignerCancelResponse:
    return STORE.cancel_job(job_id, current_user)


def block_banner_upload() -> None:
    STORE.blocked_banner_upload()


def block_download_url(job_id: object) -> None:
    STORE.blocked_download_url(job_id)
