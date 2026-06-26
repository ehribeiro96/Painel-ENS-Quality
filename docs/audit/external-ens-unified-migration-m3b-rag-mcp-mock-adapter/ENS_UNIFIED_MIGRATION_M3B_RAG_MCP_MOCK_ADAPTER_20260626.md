# ENS Unified Migration M3B — RAG MCP Mock Adapter

## 1. Status
GO

## 2. Objetivo
Implementar um adapter backend mock/determinístico para RAG MCP, com auth/RBAC preservados, allowlists explícitas e sem MCP real, sem vector store real, sem provider real e sem alterações no frontend.

## 3. Base M3A / M5 / M2B
- M3A contract: tools, collections, security and target endpoint map were already defined.
- M5 consolidation: first implementation lane is backend-owned mock adapters after Artifact and Chat Bridge foundations.
- M2B Chat Bridge mock: backend mock adapter pattern, auth gate, deterministic responses and honest frontend copy were preserved.

## 4. O que foi implementado
- backend-owned RAG router under /api/v1/rag
- deterministic mock service with allowlisted collections and tools
- contract DTOs for collections, search, documents, course context, audit and errors
- auth gate on read endpoints
- RBAC gate on audit recent
- contract and security tests
- backend API router registration

## 5. Endpoints criados
- GET /api/v1/rag/collections
- POST /api/v1/rag/search
- GET /api/v1/rag/documents/{document_id}
- GET /api/v1/rag/course-context/{course_id}
- GET /api/v1/rag/audit/recent

## 6. Tools allowlist
- ens_rag_search
- ens_rag_get_document
- ens_rag_get_course_context
- ens_rag_list_collections
- ens_rag_audit_recent

## 7. Collections allowlist
- courses
- institutional
- marketing
- insights

## 8. Mock determinístico
- sem network
- sem MCP runtime real
- sem provider real
- sem embeddings
- sem vector store
- dados pequenos e estáticos
- resultados ordenados de forma estável por score/título/id

## 9. Auth / RBAC / rate / audit
- auth preservada via get_current_user
- RBAC preservado via require_role no audit recent
- rate limiting herdado do middleware de API do backend
- audit surface preservada como endpoint admin-only mockado
- erros estruturados via códigos previsíveis

## 10. O que não foi implementado
- MCP runtime real
- provider real
- vector store real
- ingestões persistentes
- memory writes persistentes
- frontend changes
- Docker changes
- migrations changes

## 11. Riscos restantes
- contrato mock ainda não cobre o runtime real do serviço externo
- ingestão/memory continuam bloqueados nesta fase
- a próxima fase real pode exigir um backend adapter com persistência e timeouts mais rígidos

## 12. Próxima fase recomendada
M4B_DESIGNER_MOCK_ADAPTER
