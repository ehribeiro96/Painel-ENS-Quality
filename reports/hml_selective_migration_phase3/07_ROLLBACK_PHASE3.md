# Phase 3 Rollback Plan

## Rollback path
- `_backup/selective_migration_phase3_20260608-103244`

## To revert Phase 3 only
- Remove `tools/hmlops_cli/`
- Remove `scripts/hmlops`
- Remove `reports/hml_selective_migration_phase3/`

## Do not touch
- `docs/hermesops/`
- `tools/hermesops_offline/`
- `imports/HermesOps-Final-Transfer/current`

## Recovery intent
- Roll back only the CLI layer and its reports.
- Keep the Phase 1 and Phase 2 migration work intact.
