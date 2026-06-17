# UAT-H1 — Next Feature Boundary

## Recommended next boundary

`MACRO-H1 — preserve post-movement macro visibility and copy flow`

## Why this is next

- UAT-H1 confirmed the backend can generate, persist and copy the macro.
- The remaining issue is the operator experience immediately after movement.
- The macro is not held open in the same flow where the movement is confirmed.

## Scope for the next boundary

- Keep the generated macro visible after movement succeeds.
- Preserve the ability to copy the macro from the operational flow.
- Avoid changing business rules, asset movement semantics or audit behavior.
- Keep the fix narrow to the move/macro user journey.

## Out of scope

- ImportService refactor work.
- New business rules for movement.
- Migrations.
- AI Chat changes.
- Legacy `/assinaturas/` and `/admin/` behavior changes.

## Acceptance signal

- An operator can complete a synthetic movement, see the generated macro, copy it, and return to the asset flow without losing the evidence.
