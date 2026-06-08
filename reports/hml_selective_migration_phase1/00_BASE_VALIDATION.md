# Base Validation

## Paths
- `HML_WORKSPACE=/home/estevaoqualityadm/projects/Painel-ENS-Quality`
- `IMPORT_CURRENT=/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/HermesOps-Final-Transfer/current`
- `IMPORTED_HERMESOPS=/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/HermesOps-Final-Transfer/current/HermesOps`
- `IMPORTED_DESKTOP=/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/HermesOps-Final-Transfer/current/hermes-agent-hermesops`
- `PHASE1_ROOT=/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/hermesops`
- `PHASE1_REPORTS=/home/estevaoqualityadm/projects/Painel-ENS-Quality/reports/hml_selective_migration_phase1`
- `PHASE1_BACKUP=/home/estevaoqualityadm/projects/Painel-ENS-Quality/_backup/selective_migration_phase1_20260608-094550`

## Existence
- OK `HML_WORKSPACE`
- OK `IMPORT_CURRENT`
- OK `IMPORTED_HERMESOPS`
- OK `IMPORTED_DESKTOP`

## Git
- No usable `git status` or `git rev-parse` output for this workspace.

## Existing destination
- `docs/hermesops` did not exist before this phase.

## Conclusion
- The required source and destination paths exist.
- The phase can proceed without touching runtime.

