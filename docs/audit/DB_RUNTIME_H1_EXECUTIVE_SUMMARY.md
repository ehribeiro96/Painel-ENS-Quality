# DB-RUNTIME-H1 - Executive Summary

## Status

```text
GO_FASTAPI_BRIDGE_READY
PARTIAL_LOCALHOST_PORT_PUBLISHING_BROKEN
```

## Resultado

Foi estabelecido um caminho confiavel para rodar FastAPI local via WSL usando conectividade bridge para Postgres e Redis.

## Achados

- Postgres container: healthy.
- Redis container: healthy.
- Portas publicadas: `5432` e `6379`.
- TCP via `127.0.0.1`: timeout para Postgres e Redis.
- TCP via bridge Docker: OK para Postgres e Redis.
- FastAPI via bridge: `/health` e `/login` HTTP 200.

## Causa provavel

A publicacao de portas Docker para localhost no WSL esta inconsistente nesta execucao. As dependencias e o app funcionam quando o processo local usa os IPs bridge dos containers.

## Decisao

Usar bridge path temporario para desbloquear UAT local autenticado. Nao fixar IP bridge em configuracao versionada.

## Proxima boundary

`RUNTIME-H5 - run authenticated UAT smoke using local dependency bridge path`

## Boundary tecnica separada

`WSL-DOCKER-NET-H1 - repair Docker port publishing for local UAT`
