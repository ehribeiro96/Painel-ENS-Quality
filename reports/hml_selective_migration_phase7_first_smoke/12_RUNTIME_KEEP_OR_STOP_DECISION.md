# Runtime Keep or Stop Decision

## Decisão padrão após smoke

Se todos os checks passaram:

`KEEP_RUNNING_FOR_HUMAN_INSPECTION`

## Justificativa

Primeiro smoke precisa permitir inspeção de containers, portas e logs após a execução.

## Proibido

- `docker compose down -v`
- remover volumes
- prune

## Se erro crítico ocorreu

Executar:

cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml stop
