# UAT-H1 — Findings

## 1. Macro post-movement is not retained in the move flow

- Severity: High for operational usability
- Evidence: the movement modal closes immediately after submit; the generated macro is requested by the backend, but the copy surface is not kept visible in the same user journey.
- Impact: the technician cannot copy the generated macro without leaving the movement flow.
- Scope: UX/operational flow only; backend persistence and audit remain correct.

## 2. Backend operational chain is sound

- Severity: Informational
- Evidence: asset creation, movement persistence, macro generation, macro copy and audit logging all completed successfully with synthetic data.
- Impact: confirms the core backend contract is intact.

## 3. No evidence of auth or audit regression

- Severity: Informational
- Evidence: authenticated flow worked, and audit records were present for the full synthetic path.
- Impact: no additional security or RBAC regression surfaced in this boundary.

## Decision

The scenario is operationally usable only with a UX caveat. The boundary should not block release readiness on backend correctness, but it should prioritize a follow-up boundary for macro continuity.
