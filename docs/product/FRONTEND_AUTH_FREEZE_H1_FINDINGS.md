# FRONTEND-AUTH-FREEZE-H1 — Findings

## FRONTEND-FREEZE-H1-FINDING-001 — Authenticated freeze could not be reproduced without safe session

Prioridade: P0

Área: Auth/UAT/runtime validation

Classificação: `PARTIAL_AUTH_REQUIRED`

Evidência:

- `/login` renderizou normalmente.
- `/` redirecionou via SPA para `/login` sem loop visível quando não autenticado.
- Probe seguro registrou somente `POST /api/v1/auth/refresh 401` uma vez no navegador sem sessão.
- Docs anteriores de `AUTH-UAT-H1` registram que a sessão autenticada local ainda não estava disponível de forma segura.

Impacto:

- O bug relatado pós-login não pode ser confirmado nem descartado.
- A causa raiz permanece classificada como hipótese, não fato.
- Qualquer correção agora seria especulativa e fora desta boundary.

Arquivos prováveis:

- `frontend/itam-platform/src/lib/auth.tsx`
- `frontend/itam-platform/src/App.tsx`
- `frontend/itam-platform/src/pages/LoginPage.tsx`
- `frontend/itam-platform/src/pages/DashboardPage.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`
- `frontend/itam-platform/src/lib/api.ts`

Correção recomendada:

- Não corrigir ainda.
- Primeiro provisionar sessão/usuário UAT local seguro e repetir a auditoria autenticada com network/console/performance.

Boundary sugerida:

- `AUTH-UAT-H2 — provision documented local UAT test user`

Critério de aceite:

- Auditor consegue autenticar localmente sem imprimir ou salvar senha/token/cookie.
- `/`, `/assets` e `/assets/:id` são testados autenticados.
- Relatório registra URL final, endpoints, contagens e erros sem segredo.

## FRONTEND-FREEZE-H1-FINDING-002 — Auth guard and unauthenticated refresh path did not show loop

Prioridade: P1

Área: Auth provider/router

Classificação: `NOT_REPRODUCED_UNAUTH_SURFACE`

Evidência:

- `AuthProvider` executa `refreshSession()` no mount e chama `setLoading(false)` no caminho de sucesso do promise e no catch externo.
- Sem sessão, o runtime saiu do loading e renderizou `/login`.
- `request()` tenta refresh uma vez em 401 quando permitido; probe observou apenas uma chamada a `/api/v1/auth/refresh` sem repetição infinita.
- `ProtectedRoute` redireciona para `/login` se `!token || !user` e não foi observado ciclo público.

Impacto:

- Reduz probabilidade de `FREEZE_AUTH_GUARD_LOOP`, `FREEZE_LOADING_STATE_STUCK` e `FREEZE_API_401_LOOP` na superfície sem sessão.
- Não elimina a possibilidade de bug autenticado após `login()`.

Arquivos prováveis:

- `frontend/itam-platform/src/lib/auth.tsx`
- `frontend/itam-platform/src/lib/api.ts`
- `frontend/itam-platform/src/App.tsx`
- `frontend/itam-platform/src/pages/LoginPage.tsx`

Correção recomendada:

- Não alterar nesta boundary.
- Revalidar com sessão autenticada e observar se `token/user` permanecem consistentes após login.

Boundary sugerida:

- `FRONTEND-AUTH-FREEZE-H1B — collect authenticated trace`, somente após sessão UAT segura.

Critério de aceite:

- Após login, `loading=false`, `token` presente e `user` presente sem redirecionamento cíclico.
- Não há sequência repetida `/auth/refresh` ou `/auth/me` com 401/403.

## FRONTEND-FREEZE-H1-FINDING-003 — Post-login candidates are dashboard and authenticated data queries

Prioridade: P1

Área: Authenticated shell/dashboard/assets

Classificação: `FREEZE_UNKNOWN_NEEDS_TRACE`

Evidência:

- Rota `/` autenticada renderiza `DashboardPage` dentro de `AppShell`.
- `DashboardPage` inicia três React Query calls: dashboard summary, assets by status e assets overview com `page_size=200`.
- `AssetsPage` e `AssetDetailsPage` iniciam `api.users(token, '?page_size=100')` para seleção de movimentação.
- Não há evidência runtime autenticada nesta boundary para confirmar se alguma dessas chamadas repete, falha ou bloqueia render.

Impacto:

- Se o freeze só ocorre após login, a causa pode estar em query autenticada, renderização do dashboard, payload inesperado ou erro de componente após shell.
- Sem trace autenticado, não é possível separar backend lento/erro 500, loop de query, render exception ou payload incompatível.

Arquivos prováveis:

- `frontend/itam-platform/src/pages/DashboardPage.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`
- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/lib/api.ts`

Correção recomendada:

- Não corrigir ainda.
- Coletar trace autenticado com contagem de endpoints, console errors e estado visual.

Boundary sugerida:

- `FRONTEND-AUTH-FREEZE-H1B — collect authenticated trace`

Critério de aceite:

- Network audit autenticado lista endpoint, status, count e observação.
- Se houver loop, endpoint com maior count é identificado.
- Se houver exceção, stack sanitizado aponta arquivo/componente provável.
