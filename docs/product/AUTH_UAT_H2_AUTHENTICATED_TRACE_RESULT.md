# AUTH-UAT-H2 — Authenticated Trace Result

## Status

`GO_AUTH_TRACE_REPRODUCED_FREEZE`

## Login autenticado obtido

Sim.

Usuário sintético local:

```text
auth.uat.h2.1781997487@ens.edu.br
```

Senha impressa: não.

Token impresso: não.

Cookie impresso: não.

Storage state salvo/commitado: não.

Arquivo de resultado temporário local:

```text
/tmp/frontend_auth_freeze_authenticated_probe_result.json
```

O arquivo fica fora do repositório e não deve ser commitado.

## Rotas testadas

- `/login` para autenticação via UI.
- `/` após login.
- `/assets`.
- `/audit-logs`.
- `/macros`.
- `/ai-chat`.

Resumo visual:

```text
ROUTE FINAL_PATH SHELL SIDEBAR HEADER LOGIN_FORM LOADING OBSERVATION
/ / false false false false false dashboard blank after render exception
/assets /assets true true true false false shell rendered
/audit-logs /audit-logs true true true false false shell rendered
/macros /macros true true true false false shell rendered
/ai-chat /ai-chat true true true false false shell rendered
```

## Network audit redigido

```text
METHOD PATH STATUS COUNT OBSERVATION
POST /api/v1/auth/login 200 1 ok
POST /api/v1/auth/refresh 401 1 expected initial no-cookie refresh before login
POST /api/v1/auth/refresh 200 5 ok after login/navigation reloads
GET /api/v1/dashboard/summary 200 2 ok
GET /api/v1/dashboard/assets-by-status 200 2 response shape mismatch with frontend expectation
GET /api/v1/assets 200 3 ok
GET /api/v1/users 500 2 secondary issue on AssetsPage movement user query
GET /api/v1/audit-logs 200 1 ok
GET /api/v1/macros/templates 200 1 ok
GET /api/v1/ai-chat/health 200 1 ok
GET /api/v1/ai-chat/conversations 200 1 ok
```

Repetições observadas:

- Bundles JS/CSS recarregaram por navegação direta de rotas SPA.
- `POST /api/v1/auth/refresh 200` ocorreu uma vez por navegação direta pós-login, sem loop 401/403.
- Não houve request failure.

## Console audit redigido

Console:

```text
error Failed to load resource: the server responded with a status of 401 (Unauthorized)
error Failed to load resource: the server responded with a status of 500 (Internal Server Error)
error Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

Page errors:

```text
TypeError: Cannot read properties of undefined (reading 'replaceAll')
    at df (.../_assets/index-CYFwUpId.js:358:62519)
    at .../_assets/index-CYFwUpId.js:358:68521
    at Array.map (<anonymous>)
    at Fw (.../_assets/index-CYFwUpId.js:358:68350)
```

Stack sanitizado aponta para bundle minificado. Mapeamento estático por ocorrência de `replaceAll` no source aponta candidatos:

- `frontend/itam-platform/src/pages/DashboardPage.tsx:50`
- `frontend/itam-platform/src/pages/DashboardPage.tsx:54`
- `frontend/itam-platform/src/pages/AuditLogsPage.tsx:14-15`
- `frontend/itam-platform/src/lib/format.ts:59`

Pelo timing e pela tela `/` quebrar antes do shell estabilizar, o candidato principal é `DashboardPage.tsx`.

## Freeze reproduzido

Sim.

Após login, a navegação final foi `/`, mas o snapshot de `/` ficou sem shell/sidebar/header/form/loading e com body vazio, acompanhado de `TypeError` fatal. Isso reproduz o sintoma relatado como travamento/congelamento pós-login.

## Classificação

`FREEZE_RENDER_EXCEPTION`

Subtipo provável:

`FREEZE_DASHBOARD_QUERY_LOOP` não foi evidenciado. O problema observado é exceção de render por payload inesperado no dashboard, não loop de network.

`FREEZE_USERS_API_LOOP` não foi evidenciado como causa do freeze inicial, mas `/api/v1/users` retornou 500 ao abrir `/assets`.

## Causa provável

Causa raiz provável do freeze pós-login:

```text
DashboardPage espera itens de /api/v1/dashboard/assets-by-status com campos { status, count }, mas o backend retorna { name, value } via DashboardService.group_by("status"). O frontend acessa item.status e chama replaceAll em valor undefined, causando TypeError fatal durante render do dashboard após login.
```

Evidência:

- `GET /api/v1/dashboard/assets-by-status` retornou 200.
- Probe de dados mostrou `STATUS_VALUES=None`, ou seja, os itens não possuem chave `status`.
- `DashboardService.group_by()` retorna `{"name": str(name), "value": count}`.
- `DashboardPage.tsx` usa `item.status` e `item.count`.
- Page error: `Cannot read properties of undefined (reading 'replaceAll')`.
- Rota `/` ficou sem shell renderizado após a exceção.

Causa secundária em `/assets`:

```text
GET /api/v1/users?page_size=100 retornou 500 porque existe usuário local prévio com e-mail de domínio especial/reservado (`example.test`) que falha validação de EmailStr em UserRead.
```

Evidência segura:

- Probe de serialização local encontrou erro em usuário `uat-h1-20260616-163443@example.test`.
- Não há senha/hash/token impresso.
- O problema de `/users` é secundário: `/assets` ainda renderizou shell, mas a query de usuários falhou.

## Próxima boundary

`FRONTEND-AUTH-FREEZE-H2 — fix authenticated freeze root cause`.

Escopo recomendado da próxima boundary:

1. Corrigir o contrato dashboard frontend/backend de forma mínima.
2. Validar `/` autenticado sem TypeError.
3. Tratar separadamente o 500 de `/api/v1/users` por usuário local com e-mail inválido/reservado, se necessário, sem apagar dados reais.
4. Reexecutar trace autenticado sanitizado.
