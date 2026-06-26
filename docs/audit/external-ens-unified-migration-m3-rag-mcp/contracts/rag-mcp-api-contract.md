# ENS Unified Migration M3 — RAG MCP API Contract

## Status
M3A_CONTRACT_ONLY

## Scope
Define a backend-owned RAG surface for ENS/Apoema. The frontend must call only /api/v1/rag or /api/v1/ai-chat. The frontend must never talk to MCP directly.

## Required security boundaries
- AUTH_REQUIRED
- RBAC_REQUIRED
- AUDIT_LOG_REQUIRED
- RATE_LIMIT_REQUIRED
- TOOL_ALLOWLIST
- COLLECTION_ALLOWLIST
- NO_DIRECT_FRONTEND_MCP_CALL
- SERVER_SIDE_PROVIDER_KEYS_ONLY

## Target endpoints
- GET /api/v1/rag/collections
- POST /api/v1/rag/search
- GET /api/v1/rag/documents/{document_id}
- GET /api/v1/rag/course-context/{course_id}
- POST /api/v1/rag/ingestions/courses
- POST /api/v1/rag/ingestions/institutional
- POST /api/v1/rag/ingestions/marketing
- POST /api/v1/rag/ingestions/insights
- POST /api/v1/rag/insights
- POST /api/v1/rag/marketing-memory
- GET /api/v1/rag/audit/recent

## Contract rules
1. Search, document fetch, and course context are read paths and must be tenant-scoped.
2. Ingestion paths are admin-only.
3. Memory writes require explicit approval, validation notes, and server-side audit logging.
4. The backend adapter must own the mapping from HTTP route to MCP tool.
5. The backend must sanitize errors and never expose provider keys or raw MCP credentials to the frontend.
6. The contract is intentionally backend-owned; no UI changes are part of M3.

## Evidence from the external service
- Tools exist in the MCP server, but resources are not exposed.
- The external service uses zod input schemas and JSON tool results.
- The external service already records query and audit events, but it still relies on server-side env secrets and optional embedding providers.
