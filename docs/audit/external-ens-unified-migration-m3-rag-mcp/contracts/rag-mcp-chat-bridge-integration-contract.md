# ENS Unified Migration M3 — RAG MCP Chat Bridge Integration Contract

## Status
M3A_CONTRACT_ONLY

## Goal
Define how the future Chat Bridge M2 can consume RAG without any frontend-to-MCP calls.

## Required dependencies
- context retrieval for runs -> POST /api/v1/rag/search
- course context lookup -> GET /api/v1/rag/course-context/{course_id}
- document citation retrieval -> GET /api/v1/rag/documents/{document_id}
- collection listing -> GET /api/v1/rag/collections
- audit trace for RAG calls -> GET /api/v1/rag/audit/recent
- artifact link handoff if generated output creates files -> M1 artifact endpoints

## Integration rules
- The chat bridge must call backend-owned HTTP endpoints only.
- The chat bridge must never call the external rag-mcp service directly from the frontend.
- The adapter must inject collection allowlists, tenant scope, and audit context.
- Any citations returned to chat should already be sanitized and backend-approved.
- Artifact handoff remains blocked until M1 is fully implemented.

## Status of current dependencies
- RAG adapter: blocked
- Artifact handoff: blocked by M1
- Frontend integration: not in scope
