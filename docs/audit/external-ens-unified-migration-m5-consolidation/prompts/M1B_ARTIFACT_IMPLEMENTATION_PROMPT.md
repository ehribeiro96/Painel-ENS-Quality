# M1B Artifact Implementation Prompt

You are executing M1B_ARTIFACT_IMPLEMENTATION in the Painel ENS-Quality repo.

Goal: implement the smallest secure backend-owned Artifact server surface needed to unblock Chat Bridge, Designer, and future RAG dependencies.

Scope boundary:
- Allowed: backend/app/routers/artifacts.py, backend/app/schemas/artifacts.py, backend/app/services/artifact_storage.py, backend/app/services/artifact_signing.py, backend/app/main.py include_router only, tests/test_artifacts_contract.py, docs/audit/external-ens-unified-migration-m1b-artifact-implementation/**.
- Forbidden: frontend changes, Docker changes, auth refactors, RBAC redesign, migration work without explicit authorization, importing/copying external code, public file exposure, ZIP artifacts, secrets.

Required behavior:
- auth required on every route
- preserve or define RBAC at the backend route/service layer
- upload via UploadFile or equivalent multipart handling
- enforce a conservative size limit before persistence
- allowlist file extensions and MIME types
- generate artifact_id server-side
- sanitize the display filename and derive a safe storage name
- store blobs privately outside the webroot
- never expose internal filesystem paths in metadata DTOs
- mint signed download URLs with explicit expiration
- verify HMAC with constant-time comparison
- set Content-Disposition safely
- no UI, no provider integration, no direct frontend storage access
- if persistence requires a database migration, stop and ask for authorization instead of guessing

Suggested file targets:
- backend/app/routers/artifacts.py
- backend/app/schemas/artifacts.py
- backend/app/services/artifact_storage.py
- backend/app/services/artifact_signing.py
- backend/app/main.py (include_router only)
- tests/test_artifacts_contract.py

Validation checklist:
- pytest
- ruff check backend tests scripts
- compileall backend/app backend/alembic tests scripts
- npm run build in frontend/itam-platform
- git diff --check
- secret scan over the docs/test artifacts you create

Commit guidance:
- make selective commits only
- commit tests first if they encode the contract
- commit backend docs second if needed
- never use git add . or force-push
