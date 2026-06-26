# M2B Chat Bridge Mock Adapter Prompt

You are executing M2B_CHAT_BRIDGE_MOCK_ADAPTER in the Painel ENS-Quality repo.

Goal: implement a server-side mock Chat Bridge adapter that models run creation, event emission, cancellation, and attachment handling without calling any live provider.

Boundary:
- Allowed: backend-owned chat adapter files, DTOs, contract tests, and docs for the M2B mock adapter.
- Forbidden: frontend changes, provider keys in UI, direct Hermes/provider calls from frontend, Docker changes, auth changes, external vendoring, secrets, ZIPs.
- Do not start this before M1B is real.

Required behavior:
- backend auth and ownership checks
- run/create/list/detail/event/cancel contract only
- deterministic mocked SSE/event sequencing
- attachment references must depend on the Artifact contract, not public file paths
- no direct provider secrets in frontend or route payloads
- audit trail for run create/cancel/attachment minting if the project standard supports it
- conservative timeout and cancellation behavior in the adapter contract

Validation checklist:
- pytest
- ruff check backend tests scripts
- compileall backend/app backend/alembic tests scripts
- npm run build in frontend/itam-platform
- git diff --check
- secret scan over the docs/test artifacts you create

Commit guidance:
- selective commits only
- do not stage unrelated untracked files
- never push from this phase
