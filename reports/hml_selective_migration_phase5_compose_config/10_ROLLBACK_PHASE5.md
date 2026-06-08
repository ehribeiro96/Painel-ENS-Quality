# Phase 5 Rollback

Rollback da Fase 5:

1. Remover ou arquivar:
   - `infra/hermesops/`
   - `reports/hml_selective_migration_phase5_compose_config/`

2. Restaurar de:
   - `_backup/selective_migration_phase5_compose_config_20260608-105912/`

3. Não tocar:
   - `imports/HermesOps-Final-Transfer/current`
   - `docs/hermesops/`
   - `tools/hermesops_offline/`
   - `tools/hmlops_cli/`
   - `scripts/hmlops`
   - `.git`

4. Não executar:
   - `git reset --hard`
   - `git clean`
   - `docker compose down -v`
