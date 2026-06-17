# UAT-H1 — End-to-End Operational Scenario Report

## Objective

Validate the operational path `Ativo -> Movimentação -> Macro -> Histórico -> Copiar macro -> Auditoria` using synthetic data only, with no code changes and no real data.

## Execution Context

- Date/time: `2026-06-16T16:49:47-03:00`
- Branch: `main`
- Environment: local backend on `127.0.0.1:8000` with synthetic admin, postgres and redis running locally
- Data scope: synthetic only, prefixed with `UAT-H1`

## Synthetic Entities

- Asset: `Notebook UAT-H1-20260616-163728`
- Asset patrimony: `UAT-H1-20260616-163728-001`
- Technician user: `Usuário Sintético UAT-H1-20260616-163728`
- Movement justification: `Validação UAT-H1 ponta a ponta UAT-H1-20260616-163728`

## What Was Validated

### Authentication

- Login succeeded with the synthetic admin account.
- Session access remained stable after redirect to the home page.

### Asset lifecycle

- Synthetic asset was created.
- Asset details page loaded normally.
- Asset history returned the previously recorded movement and then the newer UAT-H1 movement.

### Movement

- Movement creation succeeded through the UI.
- The asset transitioned from `IN_USE` to `STOCK` in the UI test flow.
- The movement was persisted and reflected in the asset detail timeline.

### Macro generation and copy

- `GET /api/v1/movements/{movement_id}/suggested-macro` returned a generated macro for the new movement.
- `POST /api/v1/macros/generations/{generation_id}/copied` returned `copied=true`.
- The backend path for macro generation and copy is working.

### Audit trail

- Audit logs contained records for asset creation, asset movement, macro generation and macro copy.

### AI Chat

- AI Chat accepted a synthetic support-style prompt and returned a normal answer without exposing hidden reasoning tags.

## UI Observation

The movement modal opens correctly, collects the required fields, and the movement submission succeeds. After submit, the modal closes immediately and the generated macro is not left visible in the same operational surface for copy/paste.

This is the main product gap exposed by UAT-H1.

## Conclusion

The end-to-end backend flow is functional and auditable with synthetic data. The operational gap is UX continuity after movement: the operator does not keep the macro visible in the move flow.

Recommended status: `GO COM RESSALVAS`.
