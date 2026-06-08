# Phase 4 Backup Report

## Backup path
- `_backup/selective_migration_phase4_20260608-103657`

## Scope copied
- `docs/hermesops/`
- `tools/hermesops_offline/`
- `tools/hmlops_cli/`
- `scripts/hmlops`
- `reports/hml_selective_migration_phase1/`
- `reports/hml_selective_migration_phase2/`
- `reports/hml_selective_migration_phase3/`

## Notes
- The backup intentionally excludes `node_modules`, `venv`, `.env`, `.env.*`, logs, `.jsonl`, and imports.
- The backup is a cold snapshot for selective migration state only.

## Status
- Backup created successfully.
