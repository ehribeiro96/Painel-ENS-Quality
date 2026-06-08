# Phase 6.1 Rollback

Rollback da Fase 6.1:

1. Remover ou arquivar:
   - `reports/hml_selective_migration_phase6_1_smoke_plan/`

2. Restaurar de:
   - `_backup/selective_migration_phase6_1_smoke_plan_20260608-112945/`

3. Não tocar:
   - `infra/hermesops/.env.hml`
   - `imports/`
   - `docs/hermesops/`
   - `tools/hermesops_offline/`
   - `tools/hmlops_cli/`
   - `scripts/hmlops`
   - `.git`

4. Não usar:
   - `git reset --hard`
   - `git clean`
   - `docker compose down -v`
