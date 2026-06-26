# ENS Unified Migration M3 — RAG MCP Ingestion Contract

## Status
M3A_CONTRACT_ONLY

## Ingestion sources
- ens_rag_ingest_courses
- ens_rag_ingest_institutional
- ens_rag_ingest_marketing
- ens_rag_ingest_insights

## Ingestion rules
1. Ingestion is admin-only.
2. Ingestion must remain server-side.
3. Provider keys stay in environment variables only.
4. Course ingestion depends on ENS_API_URL and ENS_API_KEY.
5. Markdown ingestion reads versioned repo content under data/institutional, data/marketing, and data/insights.
6. Refresh behavior is replace-then-add, not blind append.
7. Audit every successful write and every denied ingest attempt.

## Memory write rules
- ens_rag_save_insight is a structured write path for analytical memory.
- ens_rag_save_marketing_memory requires explicit user validation and a validation note.
- No frontend code may call these tools directly.

## Blocking conditions for M3 implementation
- Missing vector store or external DB configuration.
- Missing provider keys.
- Any need to expose raw MCP tools to the browser.
