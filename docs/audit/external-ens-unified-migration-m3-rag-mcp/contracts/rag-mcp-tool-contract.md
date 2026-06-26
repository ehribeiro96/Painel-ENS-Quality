# ENS Unified Migration M3 — RAG MCP Tool Contract

## Status
M3A_CONTRACT_ONLY

## Tool allowlist
- ens_rag_search
- ens_rag_get_document
- ens_rag_get_course_context
- ens_rag_ingest_courses
- ens_rag_ingest_institutional
- ens_rag_ingest_marketing
- ens_rag_ingest_insights
- ens_rag_save_insight
- ens_rag_save_marketing_memory
- ens_rag_list_collections
- ens_rag_audit_recent

## Tool ownership
- Search/read tools are read-only and should remain server-side only.
- Ingestion tools are admin-only.
- Save-memory tools are write paths and must be approval-gated.
- Audit tool is admin-only.

## Mapping rules
- search -> POST /api/v1/rag/search
- get document -> GET /api/v1/rag/documents/{document_id}
- course context -> GET /api/v1/rag/course-context/{course_id}
- list collections -> GET /api/v1/rag/collections
- ingest tools -> POST /api/v1/rag/ingestions/*
- save insight -> POST /api/v1/rag/insights
- save marketing memory -> POST /api/v1/rag/marketing-memory
- audit recent -> GET /api/v1/rag/audit/recent

## Safety notes
- No direct frontend tool invocation.
- No provider keys in client-visible payloads.
- No unbounded result dumps; cap responses server-side.
- Preserve tenant isolation and document ownership checks.
