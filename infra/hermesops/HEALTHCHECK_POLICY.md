# HermesOps HML Healthcheck Policy

## Status

Healthchecks applied de forma controlada no Compose HML.

## Serviços

- PostgreSQL: deve usar `pg_isready`.
- Redis: deve usar `redis-cli ping`.
- Qdrant: deve usar endpoint `/readyz` somente se a imagem tiver ferramenta HTTP interna compatível.

## Regras

- Não aplicar healthcheck que dependa de ferramenta ausente no container.
- Não executar `down -v` para aplicar healthchecks.
- Recriação controlada deve usar `docker compose up -d <serviços>`.
- Após mudança, validar `docker compose ps`, `docker inspect`, logs e probes funcionais.

## Critério mínimo

- serviços alterados devem ficar `healthy`;
- `restart_count=0`;
- logs sem secrets;
- logs sem erro crítico.
