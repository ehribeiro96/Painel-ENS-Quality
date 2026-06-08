# Tooling Classification

| Class | What it contains | Status |
| --- | --- | --- |
| `ENTRA_OFFLINE` | `validators/memory`, `validators/coderos`, `validators/office`, `validators/localization`, `validators/ingest`, plus the equivalent `auditors/*` groups | Active |
| `ENTRA_SCHEMA` | JSON schema files under `schemas/` and domain docs that are schema-like catalogs | Active |
| `ENTRA_PROMPT` | Prompt files under `prompts/` | Active |
| `ENTRA_PLAYBOOK` | Playbook files under `playbooks/` | Active |
| `REFERENCIA_APENAS` | Static risk-review items that should stay offline but were not promoted as runtime tools | Review-only |
| `BLOQUEADO` | Runtime-adjacent, external-action-adjacent, or non-self-contained surfaces | Blocked / rejected |

## Review-required tools
- `auditors/localization/ptbr_localization_audit.py`
- `validators/coderos/powershell_static_checker.py`
- `validators/coderos/stack_detector.py`

## Blocked or rejected tools
- `rejected/plugins/*`
- `tools/hermesops_cli/` from the imported baseline
- `tools/composio_plugin/` from the imported baseline
- `tools/desktop_cli/` from the imported baseline
- `tools/rag/` from the imported baseline
- imported Desktop Electron runtime

## Decision
- Everything in the active offline tree stays offline-first and dry-run-first.
- Anything that depends on the source package layout, runtime CLI wiring, or external action capability stays out of the active tree.

