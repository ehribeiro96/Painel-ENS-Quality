# ENS Unified Migration M3 — RAG MCP External Service

## 1. Status
PARTIAL-GO

## 2. Objective
Define a safe backend-owned contract for RAG MCP integration in Painel ENS-Quality / Apoema without copying the external service into the current backend and without exposing MCP tools directly to the frontend.

## 3. Base M0/M1/M2
- Commit M0: af184b7
- Commit M1: e7841cb, eb71649
- Commit M2: 5df11cd, 44a94c1
- Artifact contract status: M1A_CONTRACT_ONLY
- Chat bridge contract status: M2A_CONTRACT_ONLY
- Runtime Apoema: port 5175 via scripts/dev-apoema-vite.sh with proxy http://[::1]:8080

## 4. External source analyzed
- RAG_MCP_EXTERNAL_ROOT: /tmp/ens-unificado-analysis/projeto-ens-unificado-main/services/rag-mcp
- Main files: README.md, package.json, .env.example, config/ens-rag-mcp.yaml, src/index.ts, src/mcp/createServer.ts, src/rag/ragRepository.ts, src/ingestion/ingestionService.ts, src/ingestion/sources/ens/ensInstitutionalManualSource.ts, src/policy/*.ts
- Tools found: ens_rag_search, ens_rag_get_document, ens_rag_get_course_context, ens_rag_ingest_courses, ens_rag_ingest_institutional, ens_rag_ingest_marketing, ens_rag_ingest_insights, ens_rag_save_insight, ens_rag_save_marketing_memory, ens_rag_list_collections, ens_rag_audit_recent
- Resources found: none

## 5. Phase decision
- Mode chosen: M3A_CONTRACT_ONLY
- Justification: the external MCP service depends on server-side secrets (Supabase service role, optional embedding keys), has no registered MCP resources, and already uses its own admin/profile guards. The current backend already has independent AI chat, auth/RBAC, audit, and rate-limit patterns; introducing a live RAG adapter now would be riskier than freezing the backend contract first.

## 6. External tools
See maps/rag-mcp-external-tools.tsv

## 7. External resources
See maps/rag-mcp-external-resources.tsv

## 8. Collections and data
See maps/rag-mcp-collections-map.tsv

## 9. Target contract
See maps/rag-mcp-target-contract.tsv and contracts/rag-mcp-api-contract.md

## 10. Tool allowlist
Yes. The allowlist is fixed to the 11 ENS-first tools listed above.

## 11. Collection allowlist / RBAC
Yes. Read paths are tenant-scoped and collection-allowlisted; ingest paths are admin-only; memory writes require explicit validation.

## 12. Ingestion and memory
Partially defined. The contract is documented and safe for future adapter work, but no live adapter was implemented in the current backend.

## 13. Chat Bridge M2 integration
Partial. The future bridge can depend on the RAG API contract, but the backend adapter is still blocked.

## 14. Security: auth / RBAC / audit / rate limit
Defined in the contract and maps, but not implemented in the current backend for M3.

## 15. Provider isolation
Yes. Provider keys remain server-side only; no frontend-facing provider exposure is introduced.

## 16. What was implemented
- M3 documentation bundle
- tool / resource / collection / env / security / target-contract maps
- chat bridge dependency map
- static contract test

## 17. What was NOT implemented
- backend RAG router
- backend RAG service adapter
- frontend changes
- Docker changes
- direct MCP runtime integration

## 18. Validations
- git diff --check: PASS
- PYTHONPATH=backend .venv/bin/python -m pytest: PASS (275 passed, 22 skipped)
- .venv/bin/python -m ruff check backend tests scripts: PASS
- .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts: PASS
- cd frontend/itam-platform && PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build: PASS
- Secret scan on M3 docs/test artifacts: PASS
- tests/test_m3_rag_mcp_contract_docs.py: PASS

## 19. Limitations
- External rag-mcp still depends on Supabase and optional embedding keys.
- No MCP resources are registered, so any future resource surface would be a new contract decision.
- Chat bridge integration remains downstream of the M1 artifact contract.

## 20. Next recommended phase
M4_DESIGNER_API_MODULE
