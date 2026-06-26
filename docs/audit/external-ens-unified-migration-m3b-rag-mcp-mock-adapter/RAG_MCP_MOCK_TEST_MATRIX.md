# RAG MCP Mock Test Matrix

| Area | Test | Expected | Status |
| --- | --- | --- | --- |
| Router | API v1 includes rag router | /api/v1/rag routes registered | PASS |
| Auth | collections endpoint | 401 missing_token without token | PASS |
| Auth | search endpoint | 401 missing_token without token | PASS |
| Auth | document endpoint | 401 missing_token without token | PASS |
| Auth | course context endpoint | 401 missing_token without token | PASS |
| Auth | audit recent endpoint | auth gate + RBAC | PASS |
| Collections | allowlist | courses/institutional/marketing/insights only | PASS |
| Search | invalid collection | 422 rag_collection_not_allowed | PASS |
| Search | long query | 422 rag_query_too_large | PASS |
| Search | limit clamp | 422 rag_limit_too_large | PASS |
| Search | deterministic output | repeated call yields same payload | PASS |
| Document | missing document | 404 rag_document_not_found | PASS |
| Course context | missing course | 404 rag_course_context_not_found | PASS |
| Security | DTO redaction | no provider keys or internal paths | PASS |
| Frontend | direct MCP/provider calls | no direct frontend MCP/provider wiring found | PASS |
