# FRONTEND-AUTH-FREEZE-H2 — Executive Summary

## Status final

```text
GO_FREEZE_FIXED
PARTIAL_USERS_500_REMAINS_SECONDARY
```

Audit run: 2026-06-20T20:42:12-03:00.

## Decisão

O freeze autenticado da rota `/` foi corrigido com patch mínimo no frontend.

## Causa raiz confirmada

`DashboardPage` assumia que `/api/v1/dashboard/assets-by-status` retornava itens `{ status, count }`, mas o backend observado retorna `{ name, value }` via `DashboardService.group_by("status")`.

Antes do patch, `item.status` ficava `undefined` e `formatStatus(item.status)` chamava `replaceAll` em valor indefinido, gerando exceção fatal de render e tela em branco pós-login.

## Correção

Arquivo funcional alterado:

```text
frontend/itam-platform/src/pages/DashboardPage.tsx
```

Mudança:

- normalizar itens de status aceitando `status/count` e `name/value`;
- proteger `formatStatus` contra `undefined/null`;
- usar fallback `Não informado` para item inválido;
- preservar tratamento de erro real da API.

Backend não foi alterado.

## Evidência de validação

Build frontend:

```text
npm run build
PASS — tsc --noEmit && vite build
```

Scripts opcionais:

```text
npm run typecheck --if-present: sem script presente, sem falha
npm run lint --if-present: sem script presente, sem falha
npm run test --if-present: sem script presente, sem falha
```

Recheck autenticado:

```text
/           shell=true sidebar=true header=true dashboard=true pageErrors=[]
/assets     shell=true sidebar=true header=true
/audit-logs shell=true sidebar=true header=true
/macros     shell=true sidebar=true header=true
/ai-chat    shell=true sidebar=true header=true
```

Network redigido:

```text
POST /api/v1/auth/login 200
GET /api/v1/dashboard/summary 200
GET /api/v1/dashboard/assets-by-status 200
GET /api/v1/assets 200
GET /api/v1/users 500
GET /api/v1/audit-logs 200
GET /api/v1/macros/templates 200
GET /api/v1/ai-chat/health 200
GET /api/v1/ai-chat/conversations 200
```

Console/pageerror:

```text
TypeError replaceAll: ausente após patch
pageErrors: []
```

## Fora do escopo preservado

- Autenticação não alterada.
- Usuário UAT H2 não alterado.
- `/api/v1/users` não corrigido.
- Migrations não alteradas.
- Docker/Compose não alterados.
- IA/Ollama não alterados.
- `package.json` e `package-lock.json` não alterados.
- Nenhum token, senha, cookie, Authorization header ou storage state foi registrado.

## Risco remanescente

`/api/v1/users` 500 permanece como achado secundário e afeta `/assets`/movimentação. Deve ser tratado em boundary separada.

## Próxima boundary recomendada

```text
USERS-API-H1 — fix local users serialization failure
```

Motivo: corrigir falha local de serialização/listagem de usuários sem misturar com o freeze do dashboard já resolvido.
