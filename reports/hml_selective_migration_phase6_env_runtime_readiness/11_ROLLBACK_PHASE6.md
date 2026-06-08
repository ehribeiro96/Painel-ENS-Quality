# Phase 6 Rollback

Rollback da Fase 6:

1. Remover ou arquivar localmente:
   - `infra/hermesops/.env.hml`

2. Restaurar de:
   - `_backup/selective_migration_phase6_env_runtime_readiness_20260608-111741/`

3. Não tocar:
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
