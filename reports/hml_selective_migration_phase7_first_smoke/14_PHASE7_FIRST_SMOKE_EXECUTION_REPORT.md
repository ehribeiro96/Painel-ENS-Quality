# Phase 7 First Smoke Execution Report

## Resumo executivo

O primeiro smoke controlado do HermesOps HML foi executado com `docker compose up -d` usando `infra/hermesops/docker-compose.hml.yml` e `infra/hermesops/.env.hml`.
O stack subiu com `postgres`, `redis` e `qdrant`, sem falhas criticas nos logs coletados.

## Status final

`GO — smoke infra HML OK`

## Aprovacao explicita validada

Validada pelo gate:

`APROVADO_UP_D=true`

## `up -d`

Executado com sucesso.

## Compose usado

- `infra/hermesops/docker-compose.hml.yml`
- project name: `hermesops_hml`

## Env usado

- `infra/hermesops/.env.hml`
- valores sensiveis nao reproduzidos neste relatorio

## Containers criados

- `hermesops_hml_postgres`
- `hermesops_hml_qdrant`
- `hermesops_hml_redis`

## Status dos containers

- todos em `running`
- restart count: `0`
- health status: `none` nos tres servicos

## Portas abertas

- `7333` -> `qdrant` HTTP
- `7334` -> `qdrant` gRPC
- `7380` -> `redis`
- `7433` -> `postgres`

## Volumes criados

- `hermesops_hml_postgres_data`
- `hermesops_hml_qdrant_storage`
- `hermesops_hml_redis_data`

## Network criada

- `hermesops_hml_net`

## Logs coletados

- `09_compose_logs_tail_200.txt`
- observacao de 60s concluida sem degradacao

## Scan de segredos nos logs

- nenhum match em `COMPOSIO_API_KEY`
- nenhum match em `POSTGRES_PASSWORD`
- nenhum match em `Bearer ...` ou `password=...`

## Scan de erros criticos

- sem erro critico real no recorte de logs
- a linha de shutdown do PostgreSQL ocorreu como parte do ciclo normal de inicializacao do entrypoint

## Composio

- nao executado
- nenhum marcador de `tools/execute`
- nenhum marcador de `connected account`

## hmlops

- `status`: OK
- `security-scan`: OK
- `inventory`: OK

## Decisao keep/stop

`KEEP_RUNNING_FOR_HUMAN_INSPECTION`

## Rollback

- nao acionado
- rollback leve disponivel via `docker compose stop`
- rollback destrutivo com `down -v` proibido

## Checksums

- arquivo gerado em `PHASE7_SHA256SUMS.txt`

## Commit

- relatados em git apenas os artefatos desta fase
- hash final do commit registrado no estado do repositorio apos o stage/commit

## Proxima fase recomendada

Inspecao humana curta do stack em HML, seguida da validacao funcional do proximo fluxo dependente de banco, redis e qdrant.
