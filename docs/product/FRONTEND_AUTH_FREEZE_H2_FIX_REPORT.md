# FRONTEND-AUTH-FREEZE-H2 — Fix Report

## Status

`GO_FREEZE_FIXED`

Audit run: 2026-06-20T20:42:12-03:00.

## Causa raiz

A rota `/` autenticada quebrava durante render do `DashboardPage` por mismatch de formato em `/api/v1/dashboard/assets-by-status`.

O backend observado retorna itens no formato:

```text
{ name, value }
```

O frontend antes da correção tratava os itens como:

```text
{ status, count }
```

Com payload `{ name, value }`, `item.status` ficava `undefined`. A chamada `formatStatus(item.status)` executava `replaceAll` sobre `undefined`, causando erro fatal:

```text
TypeError: Cannot read properties of undefined (reading 'replaceAll')
```

## Correção aplicada

Foi aplicado patch mínimo no frontend em `DashboardPage.tsx`:

- adicionada normalização local dos itens de status;
- aceito `status ?? name` para o rótulo;
- aceito `count ?? value` para o contador;
- convertido contador inválido para `0`;
- protegido `formatStatus()` contra `undefined`/`null` com fallback `Não informado`;
- mantido suporte ao formato antigo `{ status, count }`;
- não mascarado erro real de API: `isError` de React Query continua exibindo `AlertBlock`.

## Arquivos alterados

- `frontend/itam-platform/src/pages/DashboardPage.tsx`
- `docs/product/FRONTEND_AUTH_FREEZE_H2_FIX_REPORT.md`
- `docs/product/FRONTEND_AUTH_FREEZE_H2_AUTH_TRACE.md`
- `docs/audit/FRONTEND_AUTH_FREEZE_H2_EXECUTIVE_SUMMARY.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`

## Contrato observado

Backend:

```text
GET /api/v1/dashboard/assets-by-status -> 200
Payload observado: array; primeiro item com chaves [name, value]
```

Frontend antes:

```text
statusQuery.data?.find((item) => item.status === "DEFECTIVE")?.count
formatStatus(item.status)
```

Frontend depois:

```text
status: String(item.status ?? item.name ?? "Não informado")
count: Number(item.count ?? item.value ?? 0)
formatStatus(status?: string | null)
```

## O que ficou fora do escopo

- Não alterou autenticação.
- Não alterou usuário UAT H2.
- Não alterou backend.
- Não alterou contrato do endpoint.
- Não alterou migrations.
- Não alterou Docker/Compose.
- Não alterou IA/Ollama.
- Não alterou `package.json` ou `package-lock.json`.
- Não corrigiu `/api/v1/users` 500 nesta boundary.

## Validações

Static/build:

```text
node -p "process.platform + ' ' + process.arch + ' ' + process.execPath"
linux x64 /home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node

npm -v
10.9.8

npm run build
PASS — tsc --noEmit && vite build
CSS: dist/_assets/index-ByTPm-5T.css 39.44 kB gzip 8.01 kB
JS:  dist/_assets/index-5C8aGaCW.js 496.01 kB gzip 148.88 kB

npm run typecheck --if-present
PASS/SKIPPED — script ausente, sem falha.

npm run lint --if-present
PASS/SKIPPED — script ausente, sem falha.

npm run test --if-present
PASS/SKIPPED — script ausente, sem falha.
```

Recheck autenticado redigido:

```text
POST /api/v1/auth/login 200
GET /api/v1/dashboard/summary 200
GET /api/v1/dashboard/assets-by-status 200
GET /api/v1/assets 200
GET /api/v1/audit-logs 200
GET /api/v1/macros/templates 200
GET /api/v1/ai-chat/health 200
GET /api/v1/ai-chat/conversations 200
```

Visual autenticado:

```text
/           shell=true sidebar=true header=true dashboard=true pageErrors=[]
/assets     shell=true sidebar=true header=true
/audit-logs shell=true sidebar=true header=true
/macros     shell=true sidebar=true header=true
/ai-chat    shell=true sidebar=true header=true
```

## Riscos restantes

- `frontend/itam-platform/src/lib/api.ts` ainda tipa `assetsByStatus` como `{ status, count }`; o patch local neutraliza o crash sem ampliar escopo. Uma boundary futura pode alinhar tipos compartilhados se for decidido padronizar o contrato.
- `/api/v1/users` continua retornando 500 em `/assets`; isso é achado secundário confirmado e não foi corrigido aqui.
- O build Docker local tentou executar `apt-get` durante subida do serviço `app` e ficou bloqueado por timeout de rede Debian. A validação autenticada foi feita com Postgres/Redis via Compose e FastAPI local via `.venv`, sem alterar Compose.

## Próxima boundary

`USERS-API-H1 — fix local users serialization failure`

Motivo: `/api/v1/users` 500 permanece como secundário e afeta `/assets`/movimentação, mas não causa mais freeze da rota `/`.
