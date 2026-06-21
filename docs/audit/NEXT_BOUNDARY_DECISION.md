# Next Boundary Decision

Boundary atual: `RUNTIME-H5 - run authenticated UAT smoke using local dependency bridge path`.

## Estado consolidado

- `RUNTIME-H4`: concluiu falha rapida de startup com causa clara.
- `DB-RUNTIME-H1`: validou bridge path para Postgres/Redis.
- `RUNTIME-H5`: executou smoke autenticado API usando FastAPI local `.venv` e bridge path temporario.

## Resultado RUNTIME-H5

```text
GO_AUTHENTICATED_UAT_API_SMOKE_OK
PARTIAL_UI_SMOKE_SKIPPED
```

## Evidencia resumida

Runtime:

```text
GET /health -> HTTP 200
startup_complete=true
postgres=ok
redis=ok
migration.status=up_to_date
GET /login -> HTTP 200
```

Smoke autenticado:

```text
LOGIN_STATUS=200
USERS_STATUS=200
ASSETS_STATUS=200
DASHBOARD_SUMMARY_STATUS=200
DASHBOARD_ASSETS_BY_STATUS_STATUS=200
AUDIT_LOGS_STATUS=200
ASSET_HISTORY_STATUS=200
```

Filtros audit validados:

```text
action
entity_type
entity_id
source
correlation_id
request_id
```

## Decisao objetiva

A proxima boundary recomendada e checklist de prontidao de release, porque o smoke API autenticado passou com runtime local restaurado por bridge path.

## Proxima boundary recomendada

1. `RELEASE-H1 - production readiness and final UAT checklist`
   Objetivo: consolidar status final, pendencias conhecidas e decisao de release/piloto controlado.

## Boundary opcional

2. `UI-UAT-H1 - authenticated browser smoke using bridge runtime`
   Objetivo: repetir smoke visual autenticado quando o Browser in-app ou outro caminho seguro estiver operacional.

## Boundary tecnica paralela

3. `WSL-DOCKER-NET-H1 - repair Docker port publishing for local UAT`
   Objetivo: corrigir acesso do WSL a `127.0.0.1:5432` e `127.0.0.1:6379`, para voltar ao caminho padrao sem bridge IP.

## O que nao fazer agora

- Nao alterar frontend sem bug confirmado.
- Nao alterar migrations.
- Nao fixar IP bridge em `.env` ou codigo.
- Nao imprimir credenciais, tokens, cookies ou storage state.
- Nao apagar dados locais.
- Nao resetar banco.
- Nao executar `docker compose down -v`.

## Decisao final

Proxima boundary recomendada: `RELEASE-H1 - production readiness and final UAT checklist`.
