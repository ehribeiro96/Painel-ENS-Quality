# Phase 5.1 Rollback

Rollback da Fase 5.1:

1. Restaurar de:
   - `_backup/selective_migration_phase5_1_compose_promotion_20260608-110648/`

2. Remover, se necessário:
   - `infra/hermesops/COMPOSE_USAGE_POLICY.md`
   - `infra/hermesops/ENV_HML_POLICY.md`
   - `reports/hml_selective_migration_phase5_1_compose_promotion/`

3. Não tocar:
   - `imports/HermesOps-Final-Transfer/current`
   - `docs/hermesops/`
   - `tools/hermesops_offline/`
   - `tools/hmlops_cli/`
   - `scripts/hmlops`
   - `.git`

4. Não usar:
   - `git reset --hard`
   - `git clean`
   - `docker compose down -v`
