# Rollback da Fase 7.1C

Nenhuma mudança de runtime foi executada.

Para desfazer esta fase:

- remover ou arquivar `reports/hml_selective_migration_phase7_1c_native_docker_migration_plan/`
- preservar containers atuais
- preservar volumes
- preservar `.env.hml`
- preservar Git baseline
- não executar `docker compose down -v`
- não executar `docker volume rm`
