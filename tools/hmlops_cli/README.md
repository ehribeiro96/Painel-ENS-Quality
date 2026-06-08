# HMLOps CLI

`hmlops` is the local offline review CLI for Phase 3.

## Scope
- Local filesystem only.
- No network.
- No Docker runtime.
- No Composio execution.
- No Desktop launch.
- No shell passthrough.

## Entry points
- `scripts/hmlops`
- `python3 tools/hmlops_cli/hmlops_cli.py <command>`

## Commands
- `status`
- `inventory`
- `docs-status`
- `offline-list`
- `offline-validate`
- `offline-dry-run --tool <relative-tool-path>`
- `schemas-validate`
- `python-validate`
- `security-scan`
- `phase2-summary`
- `migration status`
- `reports list`

## Allowlisted dry-run tools
- `validators/coderos/validation_runner.py`
- `validators/office/office_safety_validator.py`
- `validators/ingest/sanitize_document.py`
- `auditors/localization/ptbr_prompt_audit.py`
- `auditors/coderos/code_review_checker.py`
- `validators/memory/memory_conflict_check.py`

## Policy files
- `command_allowlist.json`
- `command_denylist.json`
- `command_registry.json`

## Notes
- Tool paths are validated against `tools/hermesops_offline/`.
- Absolute paths and `..` traversal are rejected.
- Report output is written to `reports/hml_selective_migration_phase3/`.
