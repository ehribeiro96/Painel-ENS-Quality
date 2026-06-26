
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.domains.rag.schemas import (
    RagAuditEntryDTO,
    RagAuditRecentResponse,
    RagCollectionDTO,
    RagCourseContextDTO,
    RagDocumentDTO,
    RagSearchResponse,
    RagSearchResultDTO,
)

MAX_QUERY_LENGTH = 1000
MAX_RESULTS = 10
MAX_AUDIT_ENTRIES = 50

ALLOWED_COLLECTIONS = ('courses', 'institutional', 'marketing', 'insights')
ALLOWED_TOOLS = (
    'ens_rag_search',
    'ens_rag_get_document',
    'ens_rag_get_course_context',
    'ens_rag_list_collections',
    'ens_rag_audit_recent',
)

_NOW = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)


@dataclass(frozen=True)
class RagMockError(Exception):
    code: str
    message: str
    status_code: int = 422
    details: dict[str, object] | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)


_COLLECTIONS: dict[str, dict[str, object]] = {
    'courses': {
        'id': 'courses',
        'label': 'Cursos',
        'description': 'Trilhas e materiais operacionais aprovados para o mock ENS.',
        'document_count': 2,
        'updated_at': datetime(2026, 6, 26, 9, 0, tzinfo=UTC),
        'tool_names': ['ens_rag_search', 'ens_rag_get_document', 'ens_rag_get_course_context', 'ens_rag_list_collections'],
    },
    'institutional': {
        'id': 'institutional',
        'label': 'Institucional',
        'description': 'Políticas e conteúdo institucional mockados para validação.',
        'document_count': 1,
        'updated_at': datetime(2026, 6, 26, 9, 5, tzinfo=UTC),
        'tool_names': ['ens_rag_search', 'ens_rag_get_document', 'ens_rag_list_collections'],
    },
    'marketing': {
        'id': 'marketing',
        'label': 'Marketing',
        'description': 'Materiais de comunicação mockados sem dados sensíveis.',
        'document_count': 1,
        'updated_at': datetime(2026, 6, 26, 9, 10, tzinfo=UTC),
        'tool_names': ['ens_rag_search', 'ens_rag_get_document', 'ens_rag_list_collections'],
    },
    'insights': {
        'id': 'insights',
        'label': 'Insights',
        'description': 'Observações operacionais redigidas e determinísticas.',
        'document_count': 1,
        'updated_at': datetime(2026, 6, 26, 9, 15, tzinfo=UTC),
        'tool_names': ['ens_rag_search', 'ens_rag_get_document', 'ens_rag_list_collections', 'ens_rag_audit_recent'],
    },
}

_DOCUMENTS: dict[str, dict[str, object]] = {
    'course-onboarding-01': {
        'document_id': 'course-onboarding-01',
        'collection': 'courses',
        'title': 'Onboarding operacional ENS',
        'summary': 'Visão geral do fluxo de atendimento, inventário e movimentação.',
        'citation': 'Mock citation: ENS Cursos > Onboarding operacional.',
        'content': 'Este conteúdo de teste descreve inventário, movimentação e macro oficial após o salvamento da movimentação.',
        'tags': ['curso', 'onboarding', 'movimentacao', 'macro'],
        'updated_at': datetime(2026, 6, 26, 10, 0, tzinfo=UTC),
        'keywords': {'curso', 'onboarding', 'atendimento', 'movimentacao', 'macro', 'ens'},
    },
    'course-itil-02': {
        'document_id': 'course-itil-02',
        'collection': 'courses',
        'title': 'Base ITIL para suporte',
        'summary': 'Resumo determinístico sobre categorização e registros de chamados.',
        'citation': 'Mock citation: ENS Cursos > ITIL básico.',
        'content': 'O material destaca classificação, priorização e documentação para KCS.',
        'tags': ['itil', 'kcs', 'chamados'],
        'updated_at': datetime(2026, 6, 26, 10, 5, tzinfo=UTC),
        'keywords': {'itil', 'kcs', 'chamado', 'curso', 'suporte'},
    },
    'institutional-guideline-01': {
        'document_id': 'institutional-guideline-01',
        'collection': 'institutional',
        'title': 'Guia institucional ENS',
        'summary': 'Regras de uso interno e resposta padronizada.',
        'citation': 'Mock citation: ENS Institucional > Guia.',
        'content': 'Conteúdo mockado para orientar respostas e manter consistência sem expor segredos.',
        'tags': ['guia', 'institucional', 'resposta'],
        'updated_at': datetime(2026, 6, 26, 10, 10, tzinfo=UTC),
        'keywords': {'institucional', 'guia', 'resposta', 'ens'},
    },
    'marketing-playbook-01': {
        'document_id': 'marketing-playbook-01',
        'collection': 'marketing',
        'title': 'Playbook de comunicação ENS',
        'summary': 'Mensagem curta e segura para materiais de divulgação.',
        'citation': 'Mock citation: ENS Marketing > Playbook.',
        'content': 'Este documento simula um playbook sem segredos e sem chamadas diretas a provider.',
        'tags': ['marketing', 'playbook'],
        'updated_at': datetime(2026, 6, 26, 10, 15, tzinfo=UTC),
        'keywords': {'marketing', 'comunicacao', 'playbook', 'ens'},
    },
    'insight-rag-01': {
        'document_id': 'insight-rag-01',
        'collection': 'insights',
        'title': 'Insight sobre busca determinística',
        'summary': 'Observação sobre contrato mock, allowlist e redaction.',
        'citation': 'Mock citation: ENS Insights > Busca determinística.',
        'content': 'Quando o contrato é mock, a resposta deve ser reprodutível, explícita e sem acesso de rede.',
        'tags': ['insight', 'mock', 'allowlist'],
        'updated_at': datetime(2026, 6, 26, 10, 20, tzinfo=UTC),
        'keywords': {'insight', 'mock', 'allowlist', 'busca', 'deterministica'},
    },
}

_COURSE_CONTEXTS: dict[str, dict[str, object]] = {
    'itil-foundations': {
        'course_id': 'itil-foundations',
        'collection': 'courses',
        'title': 'ITIL Foundations ENS',
        'summary': 'Mock de contexto para orientar atendimento e priorização no padrão ENS.',
        'audience': 'Analistas de suporte e atendimento N1/N2.',
        'key_documents': ['course-itil-02', 'course-onboarding-01'],
        'recommendations': [
            'Consultar a base de chamados antes de responder.',
            'Preferir a macro oficial após a movimentação salva.',
            'Registrar exceções em histórico redigido.',
        ],
        'updated_at': datetime(2026, 6, 26, 11, 0, tzinfo=UTC),
    },
    'apoema-onboarding': {
        'course_id': 'apoema-onboarding',
        'collection': 'courses',
        'title': 'Onboarding Apoema',
        'summary': 'Guia mock para verificar o fluxo backend-owned sem frontend chamando provider.',
        'audience': 'Equipe interna ENS-Quality.',
        'key_documents': ['course-onboarding-01', 'institutional-guideline-01'],
        'recommendations': [
            'Validar auth/RBAC antes de expor dados.',
            'Manter a origem das respostas no backend.',
        ],
        'updated_at': datetime(2026, 6, 26, 11, 5, tzinfo=UTC),
    },
}

_AUDIT_LOG: list[dict[str, object]] = [
    {
        'event_id': 'rag-audit-001',
        'event_type': 'rag_search',
        'actor_role': 'VIEWER',
        'collection': 'courses',
        'document_id': 'course-onboarding-01',
        'course_id': None,
        'result': 'ok',
        'occurred_at': datetime(2026, 6, 26, 11, 10, tzinfo=UTC),
        'details': {'query': 'curso atendimento', 'source': 'mock'},
    },
    {
        'event_id': 'rag-audit-002',
        'event_type': 'rag_document_lookup',
        'actor_role': 'VIEWER',
        'collection': 'institutional',
        'document_id': 'institutional-guideline-01',
        'course_id': None,
        'result': 'ok',
        'occurred_at': datetime(2026, 6, 26, 11, 11, tzinfo=UTC),
        'details': {'source': 'mock'},
    },
    {
        'event_id': 'rag-audit-003',
        'event_type': 'rag_course_context',
        'actor_role': 'ADMIN',
        'collection': 'courses',
        'document_id': None,
        'course_id': 'itil-foundations',
        'result': 'ok',
        'occurred_at': datetime(2026, 6, 26, 11, 12, tzinfo=UTC),
        'details': {'source': 'mock'},
    },
]


def _ensure_allowed_collection(collection: str) -> str:
    normalized = collection.strip()
    if normalized not in ALLOWED_COLLECTIONS:
        raise RagMockError(
            code='rag_collection_not_allowed',
            message=f'Collection not allowed: {collection}',
            details={'collection': collection},
        )
    return normalized


def _ensure_limit(limit: int, *, maximum: int = MAX_RESULTS) -> int:
    if limit < 1:
        raise RagMockError(code='rag_limit_invalid', message='limit must be positive', details={'limit': limit})
    if limit > maximum:
        raise RagMockError(
            code='rag_limit_too_large',
            message=f'limit exceeds maximum {maximum}',
            details={'limit': limit, 'maximum': maximum},
        )
    return limit


def _ensure_query(query: str) -> str:
    normalized = query.strip()
    if not normalized:
        raise RagMockError(code='rag_query_empty', message='query cannot be empty')
    if len(normalized) > MAX_QUERY_LENGTH:
        raise RagMockError(
            code='rag_query_too_large',
            message=f'query exceeds maximum length {MAX_QUERY_LENGTH}',
            details={'length': len(normalized), 'maximum': MAX_QUERY_LENGTH},
        )
    return normalized


def _normalize_terms(text: str) -> list[str]:
    terms = [term for term in re.findall(r'[a-z0-9]+', text.lower()) if term]
    return list(dict.fromkeys(terms))


def _build_document(raw: dict[str, object]) -> RagDocumentDTO:
    return RagDocumentDTO.model_validate(raw)


def list_collections() -> list[RagCollectionDTO]:
    return [RagCollectionDTO.model_validate(_COLLECTIONS[key]) for key in ALLOWED_COLLECTIONS]


def search(query: str, collections: Iterable[str] | None = None, limit: int = MAX_RESULTS) -> RagSearchResponse:
    normalized_query = _ensure_query(query)
    normalized_limit = _ensure_limit(limit)
    requested_collections = tuple(_ensure_allowed_collection(collection) for collection in (collections or ALLOWED_COLLECTIONS))
    terms = _normalize_terms(normalized_query)
    documents: list[tuple[int, str, str, dict[str, object], list[str]]] = []
    for document in _DOCUMENTS.values():
        collection = str(document['collection'])
        if collection not in requested_collections:
            continue
        searchable = ' '.join(
            [
                str(document['title']),
                str(document['summary']),
                str(document['content']),
                ' '.join(str(tag) for tag in document['tags']),
                ' '.join(str(keyword) for keyword in document['keywords']),
            ]
        ).lower()
        matched_terms = [term for term in terms if term in searchable]
        score = len(matched_terms)
        if score <= 0:
            continue
        documents.append((score, str(document['title']), str(document['document_id']), document, matched_terms))
    documents.sort(key=lambda item: (-item[0], item[1].lower(), item[2]))
    selected = documents[:normalized_limit]
    return RagSearchResponse(
        query=normalized_query,
        collections=list(requested_collections),
        limit=normalized_limit,
        total=len(selected),
        items=[
            RagSearchResultDTO(
                document=_build_document(document),
                score=score,
                matched_terms=matched_terms,
            )
            for score, _title, _doc_id, document, matched_terms in selected
        ],
    )


def get_document(document_id: str) -> RagDocumentDTO:
    normalized = document_id.strip()
    document = _DOCUMENTS.get(normalized)
    if document is None:
        raise RagMockError(
            code='rag_document_not_found',
            message=f'Document not found: {document_id}',
            status_code=404,
            details={'document_id': document_id},
        )
    return _build_document(document)


def get_course_context(course_id: str) -> RagCourseContextDTO:
    normalized = course_id.strip()
    course = _COURSE_CONTEXTS.get(normalized)
    if course is None:
        raise RagMockError(
            code='rag_course_context_not_found',
            message=f'Course context not found: {course_id}',
            status_code=404,
            details={'course_id': course_id},
        )
    return RagCourseContextDTO.model_validate(course)


def audit_recent(limit: int = MAX_AUDIT_ENTRIES) -> RagAuditRecentResponse:
    normalized_limit = _ensure_limit(limit, maximum=MAX_AUDIT_ENTRIES)
    items = [RagAuditEntryDTO.model_validate(entry) for entry in _AUDIT_LOG[:normalized_limit]]
    return RagAuditRecentResponse(items=items, total=min(len(_AUDIT_LOG), normalized_limit))
