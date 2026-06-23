# Deep Project Audit — Painel ENS-Quality — 2026-06-23

Branch: `main` @ `16b690e`
Modo: somente auditoria — sem alteração de código de produto

## 1. Status executivo

**GO/PARTIAL-GO/NO-GO: PARTIAL-GO**

Gates automatizados (unittest, ruff, compileall, build, docker compose) **passam**. Hardening de segurança P0/P1 do commit `283d9bc` está refletido no código e nos testes. Não há P0_BLOCKER confirmado nesta rodada.

A decisão é **PARTIAL-GO** porque:

- Backend runtime via WSL bridge **indisponível** — smoke API ao vivo não executado
- Auditoria autenticada **limitada** — sem credencial UAT segura
- Playwright route audit **não executado** — binários Chromium ausentes
- Permanecem achados **P1** de UX/contrato no fallback do Apoema Chat

## 2. Escopo

- Backend FastAPI, testes, ruff, compileall
- Frontend React/Vite build e análise estática de rotas
- Apoema preview (`/apoema`, `/apoema-preview`)
- AI Chat (principal + Apoema)
- RBAC frontend/backend
- UI/UX e acessibilidade básica (estática)
- Runtime WSL bridge `http://172.18.0.1:8080` (tentativa)
- Frontend dev `http://127.0.0.1:18086` (probe HTTP)
- Segurança funcional estática
- Docker compose config

## 3. Gates

| Gate | Status | Observação |
|------|--------|------------|
| unittest | **PASS** | 172 tests OK, 8 skipped |
| ruff | **PASS** | All checks passed |
| compileall | **PASS** | backend/app, alembic, tests, scripts |
| npm run build | **PASS** | Warning chunk 598 KB > 500 KB |
| npm run lint | **N/A** | Script ausente no package.json |
| npm run test | **N/A** | Script ausente |
| uat:ui:smoke | **FAIL** | `NO-GO_UAT_CREDENTIAL_UNAVAILABLE` |
| docker compose config | **PASS** | postgres, redis, app |
| git diff --check | **PASS** | Sem conflitos de whitespace |
| Playwright route audit | **SKIPPED** | Chromium não instalado |

Log completo: `deep-audit-gates.log`

## 4. Resultado por área

| Área | Status | Principais achados |
|------|--------|-------------------|
| Login/Auth | PARTIAL | Redirect OK; acentuação; sem teste autenticado |
| Dashboard | PASS* | Loading/error/empty; *sem dados reais |
| Assets | PASS* | RBAC escrita; *sem teste autenticado |
| Imports | PASS | Accept alinhado; fluxo completo no código |
| Macros | PASS* | Permissões OK |
| AI Chat | PASS | Erros mapeados; auth backend |
| Apoema | PARTIAL | ProtectedRoute OK; fallback mock P1 |
| Users/RBAC | PASS | Menu filtrado; guards alinhados |
| Signatures | PASS* | API real; link legado |
| Audit Logs | PASS | Role guard |
| Settings | PARTIAL | Visual-only |
| Backend API | PASS | Contratos e RBAC nos testes |
| Runtime | SKIPPED | Bridge down |
| Segurança | PASS* | Hardening OK; *smoke vivo pendente |
| UI/UX | PARTIAL | Acentos, status fixo, fallback Apoema |

## 5. P0/P1 encontrados

### P0
Nenhum.

### P1
- **BUG-001** — Apoema `sendAiMessage` mascara falhas com mock
- **BUG-002** — Apoema `getAiProviders` oculta 401
- **BUG-003** — Auditoria autenticada/runtime não executada (limitação)

## 6. Bugs funcionais

Ver `BUG_BACKLOG.md` — 14 bugs catalogados (0 P0, 3 P1, 8 P2, 3 P3).

## 7. Bugs visuais/responsivos

- Sem evidência screenshot (Playwright skip)
- CSS indica suporte 1366/1920; mobile não validado visualmente
- Apoema densidade responsiva presente no CSS (commit `d22c432`)

## 8. Inconsistências API/frontend

- Apoema não reutiliza cliente `api.ts` — tratamento de erro divergente (P1)
- `enableAiChat` morto vs backend `enable_ai_chat` (P2)
- Ver `API_CONTRACT_AUDIT.md`

## 9. Riscos de segurança remanescentes

| Risco | Severidade |
|-------|------------|
| Fallback Apoema esconde 401 | P1 |
| Rate limit HTTP em memória | P2 |
| Legado Flask CSP fraco | P2 |
| `/metrics` aberto em local | INFO |
| Health expõe estado startup | P3 |

P0s anteriores (AI sem auth, Apoema público, metrics aberto em prod) **corrigidos** em `283d9bc`.

## 10. Limitações da auditoria

1. Backend `172.18.0.1:8080` não respondeu
2. Sem credencial em `/tmp/painel_runtime_h5_credentials.txt`
3. Playwright browsers não instalados
4. Screenshots não gerados
5. Não foi lido `.env` (política de segurança)
6. Fluxos de escrita (import apply, move asset) não exercitados em runtime

## 11. Plano de correção recomendado

### Imediato (P1)
1. Corrigir fallback Apoema para propagar 401/403/429
2. Subir backend e repetir smoke API + UAT smoke

### Antes de piloto (P2)
3. Health pill dinâmico
4. Busca global com erro explícito
5. Normalizar PT-BR
6. Rate limit Redis para HTTP

### Manutenção (P3)
7. Code-splitting bundle
8. ESLint no frontend
9. Modais acessíveis vs confirm()

## 12. Ordem sugerida de commits para correção

```
fix(apoema): propagate auth and api errors instead of silent mock fallback
test(apoema): add regression for 401 on providers and message
fix(ui): show global search api failures explicitly
fix(ui): normalize pt-br copy in auth and error states
feat(ui): bind shell status pills to health/ready endpoint
perf(frontend): lazy-load apoema and ai-chat routes
chore(frontend): add eslint script to package.json
docs(audit): record authenticated uat rerun results
```

## Artefatos gerados

- `BUG_BACKLOG.md`
- `FRONTEND_FUNCTIONAL_AUDIT.md`
- `API_CONTRACT_AUDIT.md`
- `RBAC_SECURITY_AUDIT.md`
- `UI_UX_ACCESSIBILITY_AUDIT.md`
- `deep-project-audit-findings.json`
- `project-structure-map.txt`
- `frontend-routes-map.txt`
- `backend-endpoints-map.txt`
- `security-static-checks.txt`
- `code-smell-scan.txt`
- `runtime-api-smoke.txt`
- `deep-audit-gates.log`
- `deep-audit-runtime.log`
- `playwright-route-audit.json` (SKIPPED)

## Conferência inicial git

- Staged antes da auditoria: **0 arquivos** — prosseguimento autorizado
- Alterações permitidas: apenas `docs/audit/deep-project-audit/**`
