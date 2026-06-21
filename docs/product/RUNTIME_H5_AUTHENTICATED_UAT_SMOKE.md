# RUNTIME-H5 - Authenticated UAT Smoke via Bridge Path

## Status

```text
GO_AUTHENTICATED_UAT_API_SMOKE_OK
PARTIAL_UI_SMOKE_SKIPPED
```

## Runtime usado

- FastAPI local via `.venv`.
- Postgres e Redis acessados por bridge path temporario dos containers Docker.
- Docker app build nao foi usado.
- Docker localhost port publishing permanece fora de escopo nesta boundary.

## Bridge path

O runtime foi iniciado em `127.0.0.1:18086` com override temporario em memoria para Postgres e Redis.

O helper confirmou:

```text
POSTGRES_BRIDGE_IP_PRESENT=True
REDIS_BRIDGE_IP_PRESENT=True
DB_OVERRIDE_APPLIED=YES
DB_OVERRIDE_HOST_SET_TO_BRIDGE=YES
DB_URL_PRINTED=NO
REDIS_OVERRIDE_APPLIED=YES
REDIS_OVERRIDE_HOST_SET_TO_BRIDGE=YES
REDIS_URL_PRINTED=NO
FASTAPI_BRIDGE_READY=YES
```

## Credencial UAT

Arquivo temporario:

```text
/tmp/painel_runtime_h5_credentials.txt
mode 0600
```

Senha impressa: NAO.

Usuario sintetico:

```text
UAT_USER_CREATED=YES
UAT_ROLE=ADMIN
```

## API smoke

Login:

```text
LOGIN_STATUS=200
ACCESS_TOKEN_PRESENT=True
ACCESS_TOKEN_PRINTED=NO
```

Endpoints:

```text
USERS_STATUS=200
USERS_ITEMS_COUNT=7
USERS_TOTAL=7

ASSETS_STATUS=200
ASSETS_ITEMS_COUNT=2
ASSETS_TOTAL=2

DASHBOARD_SUMMARY_STATUS=200
DASHBOARD_SUMMARY_DICT_KEYS=defective,in_use,maintenance,stock,total_assets,without_user

DASHBOARD_ASSETS_BY_STATUS_STATUS=200
DASHBOARD_ASSETS_BY_STATUS_LIST_COUNT=2

AUDIT_LOGS_STATUS=200
AUDIT_LOGS_ITEMS_COUNT=20
AUDIT_LOGS_TOTAL=61
```

## Audit filters

Filtros validados:

```text
AUDIT_FILTER_ACTION_STATUS=200
AUDIT_FILTER_ACTION_ITEMS_COUNT=5

AUDIT_FILTER_ENTITY_TYPE_STATUS=200
AUDIT_FILTER_ENTITY_TYPE_ITEMS_COUNT=5

AUDIT_FILTER_ENTITY_ID_STATUS=200
AUDIT_FILTER_ENTITY_ID_ITEMS_COUNT=1

AUDIT_FILTER_SOURCE_STATUS=200
AUDIT_FILTER_SOURCE_ITEMS_COUNT=5

AUDIT_FILTER_CORRELATION_ID_STATUS=200
AUDIT_FILTER_CORRELATION_ID_ITEMS_COUNT=1

AUDIT_FILTER_REQUEST_ID_STATUS=200
AUDIT_FILTER_REQUEST_ID_ITEMS_COUNT=1
```

## Asset history

```text
ASSET_HISTORY_STATUS=200
ASSET_HISTORY_LIST_COUNT=1
```

## UI smoke

Classificacao:

```text
PARTIAL_UI_SMOKE_SKIPPED
```

Motivo: o Browser in-app nao conseguiu carregar o client local por permissao no caminho montado `/mnt/c`. O smoke de `/login` via HTTP passou, mas a validacao visual autenticada foi deixada para boundary propria.

## Seguranca

Nao foram impressos:

- DB URL.
- Redis URL.
- senha.
- token.
- cookie.
- header Authorization.
- storage state.

## Limitacoes

- Bridge IP e temporario e nao deve ser versionado em configuracao.
- Docker localhost port publishing continua quebrado nesta sessao WSL.
- UI smoke autenticado nao foi executado por bloqueio da ferramenta de navegador.

## Proxima boundary

`RELEASE-H1 - production readiness and final UAT checklist`

Boundary opcional para UI:

`UI-UAT-H1 - authenticated browser smoke using bridge runtime`
