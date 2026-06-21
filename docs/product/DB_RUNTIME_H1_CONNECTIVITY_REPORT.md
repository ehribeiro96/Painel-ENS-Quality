# DB-RUNTIME-H1 - Local Dependency Connectivity

## Status

```text
GO_FASTAPI_BRIDGE_READY
PARTIAL_LOCALHOST_PORT_PUBLISHING_BROKEN
```

## Diagnostico

O runtime FastAPI falhava no startup em `postgres_timeout_after_15s` quando usava o alvo local configurado para Postgres em `127.0.0.1:5432`.

Nesta boundary foi confirmado que:

- os containers Postgres e Redis estao saudaveis;
- as portas aparecem publicadas no Docker Compose;
- TCP do WSL para `127.0.0.1` falha para Postgres e Redis;
- TCP do WSL para os IPs bridge dos containers funciona;
- FastAPI fica pronto quando a execucao local usa override temporario para os IPs bridge.

## Container health

Postgres:

```text
POSTGRES_CONTAINER_READY
/var/run/postgresql:5432 - accepting connections
```

Redis:

```text
REDIS_CONTAINER_READY
PONG
```

## Published ports

Postgres:

```text
0.0.0.0:5432
```

Redis:

```text
0.0.0.0:6379
```

## Host localhost connectivity

```text
POSTGRES_LOCALHOST_5432_TCP_FAIL TimeoutError
POSTGRES_LOCALHOST_NAME_5432_TCP_FAIL TimeoutError
REDIS_LOCALHOST_6379_TCP_FAIL TimeoutError
REDIS_LOCALHOST_NAME_6379_TCP_FAIL TimeoutError
```

## Bridge connectivity

```text
POSTGRES_BRIDGE_5432_TCP_OK
REDIS_BRIDGE_6379_TCP_OK
```

Bridge IPs observados nesta execucao:

```text
Postgres: 172.18.0.3
Redis: 172.18.0.2
```

Esses IPs sao temporarios e nao devem ser versionados em configuracao fixa.

## App settings target redacted

Banco:

```text
DB_SETTING_ATTR=database_url
DB_DRIVER=postgresql+asyncpg
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE_PRESENT=True
DB_USERNAME_PRESENT=True
DB_PASSWORD_PRESENT=True
```

Redis:

```text
REDIS_SETTING_ATTR=redis_url
REDIS_URL_PRESENT=True
REDIS_URL_REDACTED=YES
```

## FastAPI bridge test

O teste temporario em memoria aplicou override somente no processo filho:

```text
DB_OVERRIDE_APPLIED=YES
DB_OVERRIDE_HOST_SET_TO_BRIDGE=YES
DB_OVERRIDE_PORT=5432
DB_USERNAME_PRESENT=True
DB_PASSWORD_PRESENT=True
DB_URL_PRINTED=NO
REDIS_OVERRIDE_APPLIED=YES
REDIS_OVERRIDE_HOST_SET_TO_BRIDGE=YES
REDIS_URL_PRINTED=NO
FASTAPI_BRIDGE_SOCKET_READY=True
```

Resultado de `/health`:

```text
HTTP/1.1 200 OK
startup_complete=true
postgres=ok
redis=ok
migration.status=up_to_date
frontend_ready=true
```

Resultado de `/login`:

```text
HTTP/1.1 200 OK
```

## Causa provavel

O problema nao esta nos containers nem nas credenciais usadas pelo app. A falha esta na publicacao/acesso das portas Docker para `127.0.0.1` dentro do WSL nesta execucao.

O caminho bridge funciona e prova que Postgres, Redis, migrations, bootstrap, frontend check e legado conseguem completar o startup.

## Caminho recomendado para UAT

Para UAT local imediato, usar um wrapper temporario fora do repositorio que descubra os IPs bridge dos containers e injete as URLs somente no ambiente do processo FastAPI.

Para solucao permanente, abrir uma boundary separada para reparar port publishing Docker/WSL, evitando fixar IP bridge em arquivos versionados.

## O que nao foi alterado

- Codigo backend.
- Frontend.
- Migrations.
- Docker/Compose.
- Package files.
- Assets.
- IA/Ollama.
- Credenciais.
- Arquivos `.env`.

## Proxima boundary

`RUNTIME-H5 - run authenticated UAT smoke using local dependency bridge path`
