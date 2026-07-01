# FRONTEND M9C RAG UI UAT

## 1. Status
GO

## 2. Escopo
- UAT autenticado da UI Apoema RAG read-only implementada em M9B.
- Sem alteracao de backend, Docker, workflow ou package-lock.
- Sem push.

## 3. Estado inicial
- Branch: `main`
- Divergencia local/remota antes do UAT: `0 2`
- Commits locais M9B: `908e5f3`, `fc36945`
- Actions remoto verificado: `success/28515565092`

## 4. Runtime e sessao
- Backend local respondeu `200` em `/health/ready`.
- Vite em `http://127.0.0.1:5175` foi recuperado com `scripts/dev-apoema-vite.sh`.
- O `storageState` antigo de M8C estava expirado e redirecionava para `/login`.
- A sessao valida desta fase foi renovada com credencial UAT local temporaria fora do repo, a partir de `/tmp/painel_runtime_h5_credentials.txt`, sem imprimir ou registrar a senha.
- O UAT visual foi executado com Playwright local. O browser in-app nao foi usado porque o bootstrap falhou com `sandboxCwd is not a local file URI`.

## 5. Rotas validadas
- `/apoema/rag`
- `/apoema/rag/documents/institutional-guideline-01`
- `/apoema/rag/courses/apoema-onboarding`
- `/apoema-preview/rag`
- `/apoema-preview/rag/documents/institutional-guideline-01`
- `/apoema-preview/rag/courses/apoema-onboarding`
- Controle 404: `/apoema/rag/documents/unknown-document`

## 6. API smoke autenticado
- `POST /api/v1/auth/refresh` -> `200`
- `GET /api/v1/rag/collections` autenticado -> `200`
- `POST /api/v1/rag/search` consulta sintetica -> `200`
- `POST /api/v1/rag/search` consulta deterministica -> `200`
- `GET /api/v1/rag/documents/institutional-guideline-01` -> `200`
- `GET /api/v1/rag/course-context/apoema-onboarding` -> `200`
- `GET /api/v1/rag/audit/recent` -> `200`
- `GET /api/v1/rag/collections` sem token -> `401` com `missing_token`
- `GET /api/v1/rag/documents/unknown-document` -> `404` controlado

## 7. UAT funcional
- Sessao autenticada validada: sim
- Collections carregadas do backend: sim
- Busca RAG executada com resultado backend-backed: sim
- Detalhe de documento aberto por rota: sim
- Contexto de curso aberto por rota: sim
- Audit recent exibido para o usuario atual (`ADMIN`): sim
- `/apoema-preview/rag` e rotas filhas abriram autenticadas: sim
- Mobile `390x844` permaneceu autenticado e sem quebra de layout observada.

## 8. Seguranca
- Sem chamada direta para MCP, vector DB ou provider no frontend.
- Sem `provider key`, `vector key`, cookie, token ou `storageState` commitado.
- Sem `internal_path`, `storage_path` ou token renderizado na UI.
- Sem ingestao, memory-write ou Chat-RAG anunciados como implementados.
- Sem fallback enganoso para `401/403/429`.

## 9. Erros controlados
- `401` sem token confirmado em API smoke.
- `404` de documento inexistente confirmado em API smoke e UI.
- `403`, `410` e `429` nao foram provocados nesta sessao autenticada especifica; o codigo da UI permanece com tratamento explicito para esses estados e sem fallback mock.

## 10. Evidencias
- `raw/runtime-check.log`
- `raw/api-smoke-redacted.log`
- `raw/playwright-rag-uat-redacted.json`
- `screenshots/m9c-rag-desktop-1366x768.png`
- `screenshots/m9c-rag-document-1366x768.png`
- `screenshots/m9c-rag-course-1366x768.png`
- `screenshots/m9c-rag-preview-1920x1080.png`
- `screenshots/m9c-rag-mobile-390x844.png`
- `screenshots/m9c-rag-preview-document-390x844.png`
- `screenshots/m9c-rag-preview-course-390x844.png`
- `screenshots/m9c-rag-not-found-1366x768.png`

## 11. Gates
- `git diff --check`: PASS
- `pytest -s -q`: PASS (`357 passed, 22 skipped, 1 warning`)
- `ruff check backend tests scripts`: PASS
- `compileall`: PASS
- `npm run build`: PASS
- `docker compose config --services`: PASS

## 12. Commit e push
- Bugfix frontend nesta fase: nao
- Commit docs UAT: permitido e executado somente se gates passarem
- Push: nao executado nesta fase

## 13. Proxima fase recomendada
`FRONTEND_M9D_RAG_UI_PUSH_PREP`
