# RUNTIME-H5 - Bridge Path Validation

## Status

`GO_AUTHENTICATED_UAT_API_SMOKE_OK`

## Dependencias

Postgres:

```text
container healthy
pg_isready accepting connections
```

Redis:

```text
container healthy
redis-cli ping -> PONG
```

## Runtime

FastAPI local foi iniciado em:

```text
http://127.0.0.1:18086
```

Comandos destrutivos nao foram executados. O runtime temporario foi encerrado ao final.

## Health publico

```text
GET /health -> HTTP 200
startup_complete=true
postgres=ok
redis=ok
migration.status=up_to_date
frontend_ready=true
```

## Login publico

```text
GET /login -> HTTP 200
```

## Logs redigidos

Sinais de startup:

```text
database_wait_ok
redis_wait_ok
migrations_ok
bootstrap_admin_ok
frontend_check_ok
startup_complete
```

## Cleanup

```text
RUNTIME_H5_FASTAPI_BRIDGE_CLEANED=YES
PORT_18086_FREE=YES
```

O arquivo de credencial UAT em `/tmp` foi mantido com permissao `0600` para eventual reuso imediato. O conteudo nao foi impresso.
