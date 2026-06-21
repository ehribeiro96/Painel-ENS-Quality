# Next Boundary Decision

Boundary atual: `DB-RUNTIME-H1 - fix local dependency connectivity for UAT`.

## Estado consolidado

- `RUNTIME-H4`: concluida; commit `454af0b fix(runtime): prevent FastAPI startup readiness hang`.
- FastAPI nao trava mais indefinidamente em startup.
- Postgres e Redis containers estao saudaveis.
- As portas Docker aparecem publicadas em localhost.
- TCP do WSL para `127.0.0.1:5432` e `127.0.0.1:6379` falha por timeout.
- TCP do WSL para IP bridge dos containers funciona.
- FastAPI com override temporario para bridge fica pronto e responde `/health` e `/login`.

## Decisao objetiva

A proxima boundary deve executar smoke UAT autenticado usando o bridge path local validado.

Motivo:

- O runtime completo foi restaurado por caminho operacional seguro sem alterar codigo, Compose ou `.env`.
- `/health` retornou `startup_complete=true`, Postgres OK, Redis OK e migrations up-to-date.
- `/login` retornou HTTP 200.
- A causa de localhost port publishing deve ser tratada separadamente para nao bloquear UAT.

## Evidencia resumida DB-RUNTIME-H1

```text
POSTGRES_CONTAINER_READY
REDIS_CONTAINER_READY
POSTGRES_LOCALHOST_5432_TCP_FAIL TimeoutError
REDIS_LOCALHOST_6379_TCP_FAIL TimeoutError
POSTGRES_BRIDGE_5432_TCP_OK
REDIS_BRIDGE_6379_TCP_OK
FASTAPI_BRIDGE_SOCKET_READY=True
GET /health -> HTTP 200
GET /login -> HTTP 200
```

Startup completo via bridge:

```text
database_wait_ok
redis_wait_ok
migrations_ok
bootstrap_admin_ok
frontend_check_ok
startup_complete
```

## Proxima boundary recomendada

1. `RUNTIME-H5 - run authenticated UAT smoke using local dependency bridge path`
   Objetivo: executar smoke autenticado usando runtime local em WSL com override temporario para bridge, sem versionar credenciais e sem imprimir segredos.

## Boundary tecnica paralela

2. `WSL-DOCKER-NET-H1 - repair Docker port publishing for local UAT`
   Objetivo: corrigir a falha de acesso do WSL a `127.0.0.1:5432` e `127.0.0.1:6379`, preservando o caminho padrao por localhost.

## O que nao fazer agora

- Nao alterar frontend.
- Nao alterar migrations.
- Nao fixar IP bridge em `.env` ou codigo.
- Nao imprimir credenciais, tokens, cookies ou storage state.
- Nao apagar dados locais.
- Nao resetar banco.
- Nao executar `docker compose down -v`.
- Nao misturar smoke autenticado com ajuste estrutural de Docker/WSL.

## Decisao final

Proxima boundary recomendada: `RUNTIME-H5 - run authenticated UAT smoke using local dependency bridge path`.
