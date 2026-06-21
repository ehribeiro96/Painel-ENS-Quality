# RELEASE-H1 - Production Readiness

## Status

```text
GO_RELEASE_CANDIDATE_API_VALIDATED
PARTIAL_UI_SMOKE_PENDING
PARTIAL_DOCKER_PORT_PUBLISHING_BROKEN
```

This is an API-validated release candidate, not a full production GO. The remaining production blocker is authenticated UI smoke coverage.

## Scope

This boundary consolidated readiness after:

- dashboard post-login correction;
- users API serialization fix;
- asset history traceability;
- audit log filters;
- FastAPI startup timeout diagnostics;
- Docker bridge runtime path validation;
- authenticated API UAT smoke.

No deploy, push, merge, backend change, frontend change, migration, Docker change, package change or asset change was performed in this boundary.

## Commits included

```text
0e70dd1 fix(frontend): handle dashboard status response shape
6c18975 fix(users): serialize legacy email values
1cce914 feat(history): enrich asset history traceability
110f22d feat(audit): add log filters and traceability
454af0b fix(runtime): prevent FastAPI startup readiness hang
65974a4 docs(runtime): diagnose local dependency connectivity
cb97f63 docs(runtime): validate authenticated UAT bridge path
```

## Backend validation

Executed:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
```

Result:

```text
159 tests OK
8 skipped
compileall OK
```

## Frontend validation

Initial attempt used the Windows npm wrapper and failed due WSL/UNC execution:

```text
node: command not found
npm resolved to Windows wrapper
tsc not recognized under UNC path
```

Re-run with Linux Node:

```text
linux x64 /home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node
npm 10.9.8
npm run build -> OK
```

Build output:

```text
vite build OK
1818 modules transformed
dist generated
```

Separate `typecheck`, `lint` and `test` scripts were not present in `frontend/itam-platform/package.json`. The build script includes `tsc --noEmit`.

## API UAT validation

Authenticated API smoke was reexecuted in this boundary using the local bridge runtime path.

Result:

```text
GET /health -> 200
GET /login -> 200
POST /api/v1/auth/login -> 200
GET /api/v1/users?page_size=100 -> 200
GET /api/v1/assets?page_size=20 -> 200
GET /api/v1/dashboard/summary -> 200
GET /api/v1/dashboard/assets-by-status -> 200
GET /api/v1/audit-logs?page_size=20 -> 200
GET /api/v1/assets/{id}/history -> 200
```

Audit filters validated:

```text
action
entity_type
entity_id
source
correlation_id
request_id
```

## Security review

Scanner was executed over backend, frontend source, tests and documentation. Findings were classified as:

- code field names such as `token`, `password`, `Authorization`;
- test sentinel values;
- documentation terms describing redaction rules;
- no real secret value found in this boundary.

The smoke did not print DB URL, Redis URL, password, token, cookie, Authorization header or storage state.

## Runtime notes

The validated runtime path uses:

- FastAPI local `.venv`;
- Postgres/Redis Docker containers;
- temporary bridge host override in process memory;
- no bridge IP persisted to repo or `.env`.

Docker localhost port publishing remains broken in this WSL session:

```text
127.0.0.1:5432 timeout
127.0.0.1:6379 timeout
bridge TCP OK
```

## Known limitations

- Authenticated UI smoke is pending.
- Browser in-app failed previously due permission resolving the client under `/mnt/c`.
- Docker localhost port publishing must be repaired separately.
- Branch is ahead of `origin/main`; push was not executed.
- Preexisting untracked files remain outside the stage.

## Release decision

Decision: `GO_RELEASE_CANDIDATE_API_VALIDATED`.

This release candidate is acceptable for API-validated readiness and controlled next-step review, with UI smoke and WSL/Docker networking tracked as explicit follow-up boundaries. It is not a full production GO until authenticated UI smoke is completed.
