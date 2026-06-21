# RELEASE-H1 - Risk Register

## Open risks

### R1 - Authenticated UI smoke pending

Severity: High for production sign-off.

Evidence: API smoke passed, but browser smoke could not be completed because the in-app Browser failed resolving its client under `/mnt/c`.

Follow-up: `UI-UAT-H1 - authenticated browser smoke using bridge runtime`.

### R2 - Docker localhost port publishing broken in WSL

Severity: Medium for local UAT operations.

Evidence:

```text
127.0.0.1:5432 timeout
127.0.0.1:6379 timeout
bridge TCP OK
```

Follow-up: `WSL-DOCKER-NET-H1 - repair Docker port publishing for local UAT`.

### R3 - Bridge path is temporary

Severity: Medium.

Evidence: FastAPI can run with bridge override, but bridge IPs can change if Docker network/container state changes.

Control: bridge IP was not committed to code or config.

### R4 - Branch ahead of origin

Severity: Release coordination risk.

Evidence:

```text
main...origin/main [ahead 36]
```

Control: no push was executed in this boundary.

### R5 - Preexisting untracked files

Severity: Release hygiene risk.

Evidence: multiple untracked docs/assets/audit files remain outside the stage.

Control: staged files were selected explicitly; no `git add .` or `git add -A` was used.

## Accepted risks

- API-validated release candidate can proceed to release-readiness review while UI smoke is tracked separately.
- Bridge runtime path is acceptable for local UAT only.
- Windows npm wrapper failure is accepted when Linux Node is explicitly selected for frontend build.

## Blockers

Full production GO remains blocked by authenticated UI smoke.

No blocker was found for API-validated release candidate status.

## Follow-up boundaries

```text
UI-UAT-H1 - authenticated browser smoke using bridge runtime
WSL-DOCKER-NET-H1 - repair Docker port publishing for local UAT
RELEASE-H2 - final release sign-off after UI smoke
```
