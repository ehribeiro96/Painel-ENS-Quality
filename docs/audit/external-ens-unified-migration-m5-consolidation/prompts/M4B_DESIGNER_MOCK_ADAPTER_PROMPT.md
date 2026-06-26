# M4B Designer Mock Adapter Prompt

You are executing M4B_DESIGNER_MOCK_ADAPTER in the Painel ENS-Quality repo.

Goal: implement a backend-owned mock Designer adapter that preserves job/template/form-option contracts, owner checks, and artifact handoff semantics without enabling live provider generation yet.

Boundary:
- Allowed: backend-owned designer adapter files, DTOs, contract tests, and docs for the M4B mock adapter.
- Forbidden: frontend changes, Docker changes, auth refactors, public /files behavior, direct provider calls from the UI, secrets, external vendoring, ZIPs.
- Do not start this before M1B is real; M2/M3 mock adapters may remain downstream.

Required behavior:
- auth required and owner checks on every read/mutation path
- template and form-option allowlists are server-owned
- prompt validation and redaction for unsafe content
- job lifecycle states remain explicit and testable
- any output download must be artifact-backed, never public-path based
- no provider keys visible to the frontend
- server-side budgets/timeouts/cost controls only

Validation checklist:
- pytest
- ruff check backend tests scripts
- compileall backend/app backend/alembic tests scripts
- npm run build in frontend/itam-platform
- git diff --check
- secret scan over the docs/test artifacts you create

Commit guidance:
- selective commits only
- never push from this phase
