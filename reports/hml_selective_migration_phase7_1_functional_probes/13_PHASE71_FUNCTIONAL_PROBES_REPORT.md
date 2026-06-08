# Phase 7.1 Functional Probes Report

## Resumo executivo

A Fase 7.1 validou os servicos HermesOps HML ja em execucao por meio de probes read-only. O runtime permaneceu inalterado.

## Status final

`GO COM RESSALVAS - probes funcionais OK, healthcheck plan pendente de aplicacao`

## Confirmacao de runtime

- nenhum `up` executado nesta fase
- nenhum `down` executado nesta fase
- nenhum `restart` executado nesta fase
- nenhum `stop` executado nesta fase

## Estado dos containers

- `hermesops_hml_postgres`: `running`, `restart_count=0`, `health=none`
- `hermesops_hml_redis`: `running`, `restart_count=0`, `health=none`
- `hermesops_hml_qdrant`: `running`, `restart_count=0`, `health=none`

## PostgreSQL

- `pg_isready` OK
- `select 1` retornou `1`

## Redis

- `PING` retornou `PONG`

## Qdrant

- `/readyz` OK
- `/healthz` OK
- `/collections` respondeu com sucesso

## Portas, volumes e network

- portas: `7333`, `7334`, `7380`, `7433`
- volumes: `hermesops_hml_postgres_data`, `hermesops_hml_qdrant_storage`, `hermesops_hml_redis_data`
- network: `hermesops_hml_net`

## Logs

- logs coletados em modo limitado
- sem segredo exposto

## Scan de segredos

- sem match nos artefatos coletados

## Scan de erros criticos

- nenhum erro critico real encontrado

## Composio

- nao executado
- sem `tools/execute`
- sem `connected account`

## hmlops

- `status` OK
- `security-scan` OK
- `inventory` OK

## Healthcheck proposal

Proposta documentada em `11_HEALTHCHECK_PROPOSAL.md`

## Checksums

- serão gerados para os artefatos desta fase, excluindo `.env.hml`

## Commit

- sera criado somente com os relatórios desta fase

## Proxima fase recomendada

Fase 7.2 para aplicar healthchecks no Compose e recriar containers de forma controlada, sem apagar volumes.
