# Phase 3 CLI Execution Report

## Summary
- Phase 3 added a controlled offline CLI layer named `hmlops`.
- The CLI is limited to local filesystem review and reporting.
- No backend or frontend HML code was modified.

## Delivered files
- `tools/hmlops_cli/hmlops_cli.py`
- `tools/hmlops_cli/README.md`
- `tools/hmlops_cli/command_allowlist.json`
- `tools/hmlops_cli/command_denylist.json`
- `tools/hmlops_cli/command_registry.json`
- `scripts/hmlops`

## Validation highlights
- Python compile check passed.
- JSON schema checks passed.
- CLI status, inventory, docs-status, offline-list, offline-validate, schemas-validate, python-validate, security-scan, phase2-summary, migration status, and reports list are available.
- All allowlisted dry-runs passed after the pt-BR sample directory was isolated.

## Operational notes
- `sanitize_document.py` returned a small number of findings in the prompt corpus, which is expected for a sanitizer dry-run.
- Phase 2 review-only tools remain excluded from the Phase 3 dry-run surface.
- The wrapper exports `PYTHONDONTWRITEBYTECODE=1` to avoid new bytecode churn.
