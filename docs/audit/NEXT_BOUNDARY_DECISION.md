# Next Boundary Decision

Boundary atual concluída: `FRONTEND-AUTH-FREEZE-H2 — fix authenticated freeze root cause`.

## Estado consolidado

- `FRONTEND-AUTH-FREEZE-H1`: `PARTIAL_AUTH_REQUIRED`; build e superfície pública foram validados, mas faltava sessão autenticada.
- `AUTH-UAT-H2`: `GO_AUTH_TRACE_REPRODUCED_FREEZE`; usuário sintético local foi criado, login autenticado funcionou e o freeze pós-login foi reproduzido com trace redigido.
- `FRONTEND-AUTH-FREEZE-H2`: `GO_FREEZE_FIXED`; a rota `/` autenticada renderizou shell/sidebar/header/dashboard sem `TypeError replaceAll` após patch mínimo no Dashboard.

## Decisão objetiva

O freeze primário foi corrigido.

Causa raiz corrigida:

```text
Frontend DashboardPage esperava /api/v1/dashboard/assets-by-status como { status, count }, mas backend DashboardService.group_by("status") retorna { name, value }. Em / após login, item.status ficava undefined e formatStatus(item.status) chamava replaceAll em undefined, gerando TypeError fatal e tela em branco/congelada.
```

Correção aplicada:

```text
DashboardPage normaliza itens de status aceitando status/count e name/value, e formatStatus passa a ter fallback seguro para undefined/null.
```

Evidência resumida após patch:

```text
POST /api/v1/auth/login 200
GET /api/v1/dashboard/summary 200
GET /api/v1/dashboard/assets-by-status 200
Payload shape observed: status/count absent; name/value present
ROUTE / after login: shell=true sidebar=true header=true dashboard=true
PAGE_ERRORS=[]
TypeError replaceAll: ausente
```

## Achado secundário confirmado

```text
GET /api/v1/users?page_size=100 retornou 500 em /assets.
```

Classificação:

```text
PARTIAL_USERS_500_REMAINS_SECONDARY
```

Esse achado afeta `/assets`/movimentação, mas não é a causa primária do freeze imediatamente após login em `/` e não foi corrigido na boundary H2.

## Próxima boundary recomendada

1. `USERS-API-H1 — fix local users serialization failure`
   - Objetivo: corrigir a falha local de serialização/listagem de usuários sem apagar dados reais e sem relaxar segurança de auth.
   - Escopo sugerido: investigar `GET /api/v1/users?page_size=100`, DTO `UserRead`, dados locais incompatíveis e validação de e-mail, com patch mínimo.
   - Critério de GO: `/api/v1/users?page_size=100` retorna 200 com payload válido; `/assets` não registra 500 de users; não alterar auth, migrations ou usuário UAT sem necessidade explícita.

## Boundaries seguintes condicionais

2. `HISTORY-H1 — improve asset history readability and audit traceability`
   - Condição: `/assets` funcional após `USERS-API-H1`.
   - Objetivo: retomar melhoria de histórico/rastreabilidade.

3. `DASHBOARD-CONTRACT-H1 — align dashboard API/frontend typing`
   - Condição: se for decidido padronizar contrato em vez de manter compatibilidade defensiva no frontend.
   - Objetivo: alinhar `frontend/itam-platform/src/lib/api.ts`, tipos compartilhados e documentação do contrato dashboard, sem quebrar consumidores existentes.

## O que não fazer agora

- Não criar nova credencial em código versionado.
- Não commitar `/tmp/painel_auth_uat_h2_credentials.txt`.
- Não commitar storage state, cookie, token, Authorization header, trace bruto ou perfil de navegador.
- Não apagar dados reais nem resetar banco.
- Não alterar `.env`, `.env.*`, Docker/Compose, migrations, package files, assets, CI ou IA/Ollama.
- Não misturar correção de `/api/v1/users` com novas melhorias de dashboard.
- Não relaxar validação de autenticação/RBAC para contornar o 500.

## Decisão final

Próxima boundary recomendada: `USERS-API-H1 — fix local users serialization failure`.

Justificativa executiva: FRONTEND-AUTH-FREEZE-H2 removeu o bloqueio primário de render da rota `/`. O principal risco remanescente observado em UAT autenticado é `/api/v1/users` 500, confirmado como secundário e agora isolado para uma boundary própria.
