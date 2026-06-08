# Phase 2 Tool Denylist

## Blocked groups
- `tools/hermesops_cli/` from the imported baseline.
- `tools/composio_plugin/` from the imported baseline.
- `tools/desktop_cli/` from the imported baseline.
- `tools/rag/` from the imported baseline.
- `imports/HermesOps-Final-Transfer/current/hermes-agent-hermesops/apps/desktop/electron/`.

## Reasons
- These surfaces are runtime-adjacent or external-action-adjacent.
- They are not part of the offline-only phase.
- They are not allowed to execute network or external actions in this migration step.

## Re-evaluation condition
- Only after a separate security review, explicit dry-run gating, and a future phase plan.
