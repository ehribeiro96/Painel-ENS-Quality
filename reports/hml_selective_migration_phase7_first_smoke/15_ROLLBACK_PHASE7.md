# Rollback da Fase 7

## Rollback leve

cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml stop

## Rollback de containers sem apagar volumes

cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml down

## Proibido sem aprovação

docker compose down -v
docker volume rm
docker system prune

## Preservar

- volumes
- .env.hml
- reports
- backups
- Git baseline
- imports
