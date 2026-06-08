# HermesOps HML Future Runtime Rollback Plan

## Status

Plano para uso futuro. Nenhum runtime foi iniciado nesta fase.

## Rollback leve futuro

docker compose -f docker-compose.hml.yml --env-file .env.hml stop

## Rollback de remoção de containers, sem apagar volumes

docker compose -f docker-compose.hml.yml --env-file .env.hml down

## Proibido sem aprovação explícita

docker compose down -v
docker volume rm
docker system prune

## Preservar

- `.env.hml`
- backups
- reports
- imports
- Git baseline
- volumes de banco até revisão humana
