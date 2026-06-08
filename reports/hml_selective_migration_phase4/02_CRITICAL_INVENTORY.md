# Phase 4 Critical Inventory

## Critical directories observed
- `docs/hermesops/`
- `tools/hermesops_offline/`
- `tools/hmlops_cli/`
- `scripts/`
- `reports/hml_selective_migration_phase1/`
- `reports/hml_selective_migration_phase2/`
- `reports/hml_selective_migration_phase3/`
- `reports/hml_selective_migration_phase4/`
- `_backup/`
- `imports/HermesOps-Final-Transfer/current`

## Critical files observed
- `docs/hermesops/README.md`
- `docs/hermesops/INDEX.md`
- `docs/hermesops/MIGRATION_SOURCE.md`
- `tools/hmlops_cli/hmlops_cli.py`
- `tools/hmlops_cli/command_allowlist.json`
- `tools/hmlops_cli/command_denylist.json`
- `tools/hmlops_cli/command_registry.json`
- `scripts/hmlops`
- `reports/hml_selective_migration_phase1/04_PHASE1_MIGRATION_EXECUTION_REPORT.md`
- `reports/hml_selective_migration_phase2/09_PHASE2_MIGRATION_EXECUTION_REPORT.md`
- `reports/hml_selective_migration_phase3/09_PHASE3_CLI_EXECUTION_REPORT.md`

## Top-level observations
- The workspace also contains local-only files outside the migration set, including `.env`, `.venv`, and `data/ens.db`.
- Those files were not copied into the Phase 4 backup.

## Status
- Inventory completed without touching runtime or imports.
