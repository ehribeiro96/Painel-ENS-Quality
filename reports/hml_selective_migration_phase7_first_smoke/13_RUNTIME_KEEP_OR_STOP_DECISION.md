# Runtime Keep or Stop Decision

## Decisao

`KEEP_RUNNING_FOR_HUMAN_INSPECTION`

## Justificativa

O primeiro smoke da infra HML subiu com sucesso, os tres servicos esperados ficaram `running`, as portas publicadas ficaram acessiveis e a observacao de 60s nao mostrou reinicios.

## Proibido

- `docker compose down -v`
- remover volumes
- `docker system prune`
- apagar containers fora do projeto Compose

## Se houver rollback leve

Executar apenas:

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml stop
```
