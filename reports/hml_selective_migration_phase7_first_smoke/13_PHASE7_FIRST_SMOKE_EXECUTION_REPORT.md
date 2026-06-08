# Phase 7 First Smoke Execution Report

## Executive summary
- The first controlled HML smoke test was executed with `docker compose up -d`.
- The HermesOps infra stack started successfully and remained stable through the observation window.
- The smoke remained within the allowed scope: no Composio, no connected account, no push, and no destructive teardown.

## Final status
- `GO COM RESSALVAS - smoke infra HML iniciado e observado`

## `up -d`
- Executed: yes

## Compose used
- `infra/hermesops/docker-compose.hml.yml`

## Env used
- `infra/hermesops/.env.hml`
- Values were not printed

## Containers created
- `hermesops_hml_postgres`
- `hermesops_hml_qdrant`
- `hermesops_hml_redis`

## Status of containers
- All were `running`
- Restart count: `0`

## Health
- No Compose healthcheck was defined, so Docker inspect health was `none`

## Ports open
- `7333`, `7334`, `7380`, `7433`

## Volumes created
- `hermesops_hml_postgres_data`
- `hermesops_hml_qdrant_storage`
- `hermesops_hml_redis_data`

## Network created
- `hermesops_hml_net`

## Logs collected
- `docker compose logs --tail=200 --timestamps` was collected and reviewed

## Log scans
- No secrets in logs
- One benign PostgreSQL lifecycle line matched the broad critical-error grep, but it was not a failure condition

## Composio
- Not executed

## HMLOps
- Validation passed

## Decision keep/stop
- `KEEP_RUNNING_FOR_HUMAN_INSPECTION`

## Rollback
- Use `docker compose stop` first if a rollback is needed

## Checksums
- Phase checksum file generated and verified

## Commit
- Local commit created for the phase reports

## Next phase recommended
- Human inspection of the running containers, then decide whether to proceed to a deeper runtime validation phase.
