# 05 Final Runtime Probes

## Probes executados
- Postgres:
  - `pg_isready` passou
  - `select 1` retornou com sucesso
- Redis:
  - `redis-cli ping` retornou `PONG`
- Qdrant:
  - `GET /readyz` retornou `all shards are ready`
  - `GET /collections` retornou `status=ok`

## Conclusão
- Os três serviços do stack HML responderam corretamente.
- Não houve necessidade de derrubar volumes nem recriar containers.

