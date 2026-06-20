# FRONTEND-AUTH-FREEZE-H2 — Authenticated Trace

## Status

`GO_FREEZE_FIXED`

Audit run: 2026-06-20T20:42:12-03:00.

## Usuário sintético usado

Usuário UAT H2 sintético local existente.

Não registrar senha.

Senha impressa: não.
Token impresso: não.
Cookie impresso: não.
Storage state salvo/commitado: não.

Credencial lida somente por script temporário em `/tmp`:

```text
/tmp/painel_auth_uat_h2_credentials.txt
```

Resultado redigido salvo fora do repositório:

```text
/tmp/frontend_auth_freeze_h2_probe_result.json
```

## Rotas testadas

```text
ROUTE       FINAL_PATH  SHELL  SIDEBAR  HEADER  LOGIN_FORM  LOADING  DASHBOARD  BODY_EMPTY
/           /           true   true     true    false       false    true       false
/assets     /assets     true   true     true    false       false    false      false
/audit-logs /audit-logs true   true     true    false       false    false      false
/macros     /macros     true   true     true    false       false    false      false
/ai-chat    /ai-chat    true   true     true    false       false    false      false
```

## Network audit redigido

```text
METHOD PATH STATUS COUNT OBSERVATION
POST /api/v1/auth/refresh 401 1 expected initial no-cookie refresh before login
POST /api/v1/auth/login 200 1 ok
GET /api/v1/dashboard/summary 200 2 ok
GET /api/v1/dashboard/assets-by-status 200 2 ok; shape name/value observed
GET /api/v1/assets 200 3 ok
POST /api/v1/auth/refresh 200 5 ok after authenticated navigation
GET /api/v1/users 500 2 secondary issue remains, not fixed in H2
GET /api/v1/audit-logs 200 1 ok
GET /api/v1/macros/templates 200 1 ok
GET /api/v1/ai-chat/health 200 1 ok
GET /api/v1/ai-chat/conversations 200 1 ok
```

Shape observado de `/api/v1/dashboard/assets-by-status`:

```text
status=200
isArray=true
firstKeys=[name, value]
hasStatusCount=false
hasNameValue=true
```

## Console audit redigido

Console após patch:

```text
error Failed to load resource: the server responded with a status of 401 (Unauthorized)
error Failed to load resource: the server responded with a status of 500 (Internal Server Error)
error Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

Classificação:

- 401: refresh inicial sem cookie antes do login, esperado no fluxo local.
- 500: `/api/v1/users` em `/assets`, achado secundário fora do escopo desta boundary.

Page errors após patch:

```text
[]
```

Não houve `TypeError replaceAll` após a correção.

## Resultado visual

A rota `/` autenticada renderizou shell, sidebar, header e dashboard. O componente `DashboardPage` consumiu payload `{ name, value }` de `assets-by-status` sem quebrar o render.

## Achados secundários

`/api/v1/users` continua retornando 500 em `/assets`.

Classificação:

```text
PARTIAL_USERS_500_REMAINS_SECONDARY
```

Esse achado deve seguir para boundary própria:

```text
USERS-API-H1 — fix local users serialization failure
```
