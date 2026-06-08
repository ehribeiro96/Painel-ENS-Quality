# Base Validation

## Paths
- `HML_WORKSPACE=/home/estevaoqualityadm/projects/Painel-ENS-Quality`
- `IMPORT_CURRENT=/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/HermesOps-Final-Transfer/current`
- `IMPORTED_HERMESOPS=/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/HermesOps-Final-Transfer/current/HermesOps`
- `IMPORTED_DESKTOP=/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/HermesOps-Final-Transfer/current/hermes-agent-hermesops`
- `PHASE2_ROOT=/home/estevaoqualityadm/projects/Painel-ENS-Quality/tools/hermesops_offline`
- `PHASE2_REPORTS=/home/estevaoqualityadm/projects/Painel-ENS-Quality/reports/hml_selective_migration_phase2`
- `PHASE2_BACKUP=/home/estevaoqualityadm/projects/Painel-ENS-Quality/_backup/selective_migration_phase2_20260608-100151`

## Existence
- OK `HML_WORKSPACE`
- OK `IMPORT_CURRENT`
- OK `IMPORTED_HERMESOPS`
- OK `PHASE1_DOCS`

## Git
- No reliable `git status` or `git rev-parse` output for provenance.

## Existing destination
- `tools/hermesops_offline` existed as an empty destination before this phase.

## Conclusion
- The required source and destination paths exist.
- Phase 2 can proceed as an offline-only migration.

