# Next Boundary Decision

Boundary atual concluída: `AUTH-UAT-H2 — provision documented local UAT test user`.

## Estado consolidado

- `FRONTEND-AUTH-FREEZE-H1`: `PARTIAL_AUTH_REQUIRED`; build e superfície pública foram validados, mas faltava sessão autenticada.
- `AUTH-UAT-H2`: `GO_AUTH_TRACE_REPRODUCED_FREEZE`; usuário sintético local foi criado, login autenticado funcionou e o freeze pós-login foi reproduzido com trace redigido.

## Decisão objetiva

A causa provável do travamento pós-login foi identificada:

```text
Frontend DashboardPage espera /api/v1/dashboard/assets-by-status como { status, count }, mas backend DashboardService.group_by("status") retorna { name, value }. Em / após login, item.status fica undefined e formatStatus(item.status) chama replaceAll em undefined, gerando TypeError fatal e tela em branco/congelada.
```

Evidência resumida:

```text
LOGIN_STATUS=200
ROUTE / after login: shell=false sidebar=false header=false loading=false
PAGE_ERROR TypeError: Cannot read properties of undefined (reading 'replaceAll')
GET /api/v1/dashboard/assets-by-status 200
Payload shape observed: status key absent; name/value present
```

Achado secundário:

```text
GET /api/v1/users?page_size=100 retornou 500 em /assets.
Causa provável: usuário local prévio com e-mail example.test falha validação EmailStr em UserRead.
```

Esse achado secundário afeta seleção de usuários/movimentação, mas não é a causa primária do freeze imediatamente após login em `/`.

## Próxima boundary recomendada

1. `FRONTEND-AUTH-FREEZE-H2 — fix authenticated freeze root cause`
   - Objetivo: corrigir o mismatch mínimo do dashboard e revalidar `/` autenticado.
   - Escopo sugerido: `DashboardPage.tsx` ou contrato backend dashboard, escolhendo o menor patch compatível com o restante do app.
   - Critério de GO: login com usuário UAT, `/` renderiza shell/dashboard sem `replaceAll` TypeError, network sem loop, docs/trace redigidos.

## Boundaries seguintes condicionais

2. `USERS-API-H1 — fix local users serialization failure`
   - Condição: `/api/v1/users` continuar 500 após corrigir dashboard.
   - Objetivo: tratar usuário local com e-mail de domínio reservado sem apagar dados reais e sem relaxar segurança de auth.
   - Critério de GO: `/assets` carrega `api.users('?page_size=100')` sem 500.

3. `HISTORY-H1 — improve asset history readability and audit traceability`
   - Condição: freeze autenticado resolvido e `/assets` funcional.
   - Objetivo: retomar melhoria de histórico/rastreabilidade.

## O que não fazer agora

- Não criar nova credencial em código versionado.
- Não commitar `/tmp/painel_auth_uat_h2_credentials.txt`.
- Não commitar storage state, cookie, token, Authorization header, trace bruto ou perfil de navegador.
- Não apagar dados reais nem resetar banco.
- Não alterar `.env`, `.env.*`, Docker/Compose, migrations, package files, assets, CI ou IA/Ollama.
- Não corrigir múltiplas áreas na mesma boundary sem evidência e escopo explícito.

## Decisão final

Próxima boundary recomendada: `FRONTEND-AUTH-FREEZE-H2 — fix authenticated freeze root cause`.

Justificativa executiva: AUTH-UAT-H2 removeu o bloqueio de autenticação, reproduziu o freeze e isolou a causa provável em contrato dashboard/frontend. A próxima boundary deve ser de correção mínima e revalidação autenticada.
