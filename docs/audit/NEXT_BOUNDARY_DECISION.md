# Next Boundary Decision

Boundary atual: `UI-UAT-H1 - authenticated browser smoke using bridge runtime`.

## Estado consolidado

```text
GO_RELEASE_CANDIDATE_API_VALIDATED
PARTIAL_BROWSER_TOOLING_UNAVAILABLE
PARTIAL_RUNTIME_FRONTEND_PORT_UNAVAILABLE
PARTIAL_DOCKER_PORT_PUBLISHING_BROKEN
```

## Evidencia RELEASE-H1

Backend:

```text
python -m compileall -q backend/app backend/alembic tests -> OK
python -m unittest discover -s tests -> 159 tests OK, 8 skipped
```

Frontend:

```text
Linux Node v22.22.3
npm 10.9.8
npm run build -> OK
```

API UAT autenticado:

```text
GET /health -> 200
GET /login -> 200
POST /api/v1/auth/login -> 200
GET /api/v1/users?page_size=100 -> 200
GET /api/v1/assets?page_size=20 -> 200
GET /api/v1/dashboard/summary -> 200
GET /api/v1/dashboard/assets-by-status -> 200
GET /api/v1/audit-logs?page_size=20 -> 200
GET /api/v1/assets/{id}/history -> 200
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

## Evidencia UI-UAT-H1

Backend bridge:

```text
GET /health -> 200
GET /login -> 200
POST /api/v1/auth/login -> 200
```

Frontend/browser:

```text
Linux Node v22.22.3
npm 10.9.8
Vite registrou readiness em 127.0.0.1:5173
curl 127.0.0.1:5173 -> timeout
playwright -> ausente
@playwright/test -> ausente
chromium/chrome/edge no WSL -> ausentes
```

Seguranca:

```text
Senha/token/cookie/Authorization/storage state/DSN nao impressos
Nenhum screenshot ou storage state commitado
Processos temporarios encerrados
```

## Decisao objetiva

A release candidate esta validada no nivel API/backend/frontend build. O full production GO segue pendente de UI smoke autenticado porque o runner de navegador esta indisponivel no WSL e o Vite dev server nao permaneceu acessivel em `127.0.0.1:5173` nesta execucao.

## Proxima boundary principal

1. `UI-UAT-H2 - provide supported browser runner for WSL`
   Objetivo: disponibilizar browser runner suportado no WSL, estabilizar o servidor frontend local e repetir smoke visual autenticado sem expor credenciais.

## Boundary paralela

2. `UI-RUNTIME-H1 - stabilize Vite dev server accessibility in WSL`
   Objetivo: investigar por que o Vite registra readiness, mas `127.0.0.1:5173` expira e a porta nao permanece acessivel.

3. `WSL-DOCKER-NET-H1 - repair Docker port publishing for local UAT`
   Objetivo: corrigir acesso WSL a `127.0.0.1:5432` e `127.0.0.1:6379`.

## Boundary seguinte

4. `RELEASE-H2 - final release sign-off after UI smoke`
   Condicao: UI smoke autenticado aprovado ou explicitamente dispensado pelo responsavel de release.

## O que nao fazer agora

- Nao fazer deploy.
- Nao fazer push sem autorizacao.
- Nao alterar frontend/backend/migrations.
- Nao fixar bridge IP em `.env` ou codigo.
- Nao imprimir credenciais, tokens, cookies ou storage state.
- Nao executar `docker compose down -v`.

## Decisao final

Proxima boundary recomendada: `UI-UAT-H2 - provide supported browser runner for WSL`.
