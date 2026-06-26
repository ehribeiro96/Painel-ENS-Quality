# M3B RAG MCP Mock Adapter Prompt

You are executing M3B_RAG_MCP_MOCK_ADAPTER in the Painel ENS-Quality repo.

Goal: implement a backend-owned mock RAG adapter that preserves the allowlisted tool contract, collections, audit trace, and ownership checks without enabling live provider/vector-store access yet.

Boundary:
- Allowed: backend-owned RAG adapter files, DTOs, contract tests, and docs for the M3B mock adapter.
- Forbidden: frontend changes, raw MCP exposure to the UI, Docker changes, auth refactors, secrets, external vendoring, ZIPs.
- Do not start this before M1B is real.

Required behavior:
- auth required
- collection allowlist enforced server-side
- tool allowlist enforced server-side
- explicit user/session ownership checks
- bounded query/result sizes and timeouts
- audit trail for search, reads, ingests, and denials where supported by project standards
- sanitized, structured errors
- no direct provider/vector-store secrets in frontend code

Validation checklist:
- pytest
- ruff check backend tests scripts
- compileall backend/app backend/alembic tests scripts
- npm run build in frontend/itam-platform
- git diff --check
- secret scan over the docs/test artifacts you create

Commit guidance:
- selective commits only
- keep the mock adapter server-side
- never push from this phase
