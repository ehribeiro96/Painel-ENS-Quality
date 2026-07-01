# FRONTEND M9B RAG UI

## Status

GO local, pendente apenas de push em fase posterior.

## Escopo

Implementacao da UI Apoema para RAG Institucional read-only usando somente endpoints backend `/api/v1/rag/*`.

## Arquivos alterados

- `frontend/itam-platform/src/apoema/ApoemaApp.tsx`
- `frontend/itam-platform/src/apoema/lib/apoemaRagApi.ts`
- `frontend/itam-platform/src/apoema/types.ts`
- `frontend/itam-platform/src/apoema/pages/RagPage.tsx`
- `frontend/itam-platform/src/apoema/pages/RagDocumentPage.tsx`
- `frontend/itam-platform/src/apoema/pages/RagCourseContextPage.tsx`
- `frontend/itam-platform/src/apoema/components/RagCollectionFilter.tsx`
- `frontend/itam-platform/src/apoema/components/RagSearchResults.tsx`
- `frontend/itam-platform/src/apoema/components/RagDocumentCard.tsx`
- `frontend/itam-platform/src/apoema/styles/apoema.css`
- `tests/test_apoema_rag_ui_contract.py`

## Rotas

- `/apoema/rag`
- `/apoema/rag/documents/:documentId`
- `/apoema/rag/courses/:courseId`
- `/apoema-preview/rag`
- `/apoema-preview/rag/documents/:documentId`
- `/apoema-preview/rag/courses/:courseId`

Nenhum alias legacy `/rag`, `/knowledge` ou `/mcp` foi criado fora do shell Apoema.

## Endpoints consumidos

- `GET /api/v1/rag/collections`
- `POST /api/v1/rag/search`
- `GET /api/v1/rag/documents/{document_id}`
- `GET /api/v1/rag/course-context/{course_id}`
- `GET /api/v1/rag/audit/recent`

## Collections consumidas

- `courses`
- `institutional`
- `marketing`
- `insights`

## Gaps fechados

- Client RAG alinhado a `/api/v1/rag/*`.
- Busca read-only com filtro de collections.
- Detalhe de documento seguro.
- Contexto de curso seguro.
- Painel de auditoria recente backend-backed.
- Tratamento explicito de 401, 403, 404, 410, 429, 5xx e rede.
- Teste de contrato frontend M9B.

## Gaps nao implementados

- Ingestao: nao implementada.
- Escrita de memoria: nao implementada.
- Integracao Chat-RAG: nao implementada.

## Seguranca

- Sem chamada direta a MCP.
- Sem chamada direta a vector DB.
- Sem chamada direta a provider LLM.
- Sem provider/vector key no frontend.
- Sem path interno ou storage path renderizado.
- Sem fallback mock para 401/403/429.

## Gates

Resultados registrados em `frontend-m9b-rag-ui-gates.log`.

Smoke HTTP local em `127.0.0.1:5175`: skipped, runtime nao disponivel no momento da verificacao. Build e testes de contrato passaram.

## Push

Nao executado nesta fase.

## Proxima fase

`FRONTEND_M9C_RAG_UI_UAT`.
