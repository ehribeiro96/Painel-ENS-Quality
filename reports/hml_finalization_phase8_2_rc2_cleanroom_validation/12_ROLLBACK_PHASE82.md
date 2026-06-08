# Rollback da Fase 8.2

Nenhum runtime foi alterado nesta fase.

Para desfazer apenas a validação clean-room:

- remover ou arquivar `_validation/rc2_cleanroom_20260608`
- remover ou arquivar `reports/hml_finalization_phase8_2_rc2_cleanroom_validation`

Não tocar:

- RC2 original
- exports/
- infra/hermesops/.env.hml
- containers
- volumes
- Git baseline
- imports
- backups

Proibido:

- docker compose down -v
- docker volume rm
- git reset --hard
- git clean
