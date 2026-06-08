# Rollback da Fase 7.2

## Restaurar Compose anterior

Arquivo salvo em:

`_backup/selective_migration_phase7_2_healthchecks_20260608-124430/docker-compose.hml.yml.before-healthchecks`

## Aplicar rollback sem apagar volumes

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
cp <backup>/docker-compose.hml.yml.before-healthchecks docker-compose.hml.yml
docker compose -f docker-compose.hml.yml --env-file .env.hml up -d postgres redis qdrant
```

## Proibido

`docker compose down -v`

`docker volume rm`

`docker system prune`

## Preservar

- volumes
- `.env.hml`
- reports
- backups
- Git baseline
- imports

