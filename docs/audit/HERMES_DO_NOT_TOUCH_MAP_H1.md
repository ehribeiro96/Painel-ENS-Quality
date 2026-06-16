# HERMES_DO_NOT_TOUCH_MAP_H1

## AI Chat Ollama LAN provider
Área: AI Chat/Ollama
Arquivos/Componentes: `backend/app/domains/ai_chat/*`, `backend/app/api/v1/routes/ai_chat.py`, frontend AI Chat.
Motivo para não mexer: provider `ollama-lan` foi validado e fecha o fluxo backend proxy/same-origin.
Última validação conhecida: B5-D same-origin authenticated smoke; auditoria H1 encontrou referências e testes.
Risco de mexer: regressão para mock, exposição direta do IP LAN ao browser, perda de sanitização.
Quando pode mexer: somente em boundary AI Chat explícita.
Boundary obrigatória se precisar mexer: `AI-H2 — Ollama provider controlled change`.

## qwen3 baseline
Área: AI Chat/Ollama
Arquivos/Componentes: docs B5, configuração provider, testes Ollama.
Motivo para não mexer: `qwen3:1.7b-64k` é baseline validado.
Última validação conhecida: B5-D e contexto H1.
Risco de mexer: comparação de qualidade/performance inválida e regressão de UX.
Quando pode mexer: após benchmark controlado.
Boundary obrigatória se precisar mexer: `AI-H2 — local model benchmark and decision`.

## Sanitização de `<think>`
Área: AI Chat/Ollama
Arquivos/Componentes: provider/service AI Chat e testes relacionados.
Motivo para não mexer: protege UX e evita expor raciocínio bruto do modelo.
Última validação conhecida: docs/testes B5.
Risco de mexer: vazamento de conteúdo indesejado e ruído no chat.
Quando pode mexer: somente com teste de regressão explícito.
Boundary obrigatória se precisar mexer: `AI-H2 — chat output sanitization review`.

## Import pipeline validado
Área: Import pipeline
Arquivos/Componentes: `backend/app/domains/imports/`, `backend/app/api/v1/routes/imports.py`, fixtures e testes de imports.
Motivo para não mexer: B3 validado; parsing, normalização, classificação e conflitos têm blast radius de dados.
Última validação conhecida: B3 e H1 compileall.
Risco de mexer: corrupção de staging, classificação incorreta e perda de conflito/review.
Quando pode mexer: quando a boundary for só de imports.
Boundary obrigatória se precisar mexer: `IMPORT-H2 — controlled import pipeline change`.

## Frontend shell validado
Área: Frontend React
Arquivos/Componentes: `AppShell`, `DataTable`, `StateBlocks`, `styles.css`, rotas principais.
Motivo para não mexer: B4 validou shell/UX e build H1 passou.
Última validação conhecida: B4-D/B4-E e H1 `npm run build` PASS.
Risco de mexer: regressão visual ampla, shell autenticado quebrado, rotas inacessíveis.
Quando pode mexer: somente com screenshot/smoke autenticado.
Boundary obrigatória se precisar mexer: `FRONTEND-H2 — route UX/accessibility review`.

## Legacy CSP validado
Área: Legacy `/admin` e `/assinaturas`
Arquivos/Componentes: templates/assets legacy, security headers/CSP.
Motivo para não mexer: Google Fonts removidas e CSP validada sem `unsafe-eval` e sem CSP malformada.
Última validação conhecida: B4-E/GIT-C5 e H1 busca legacy.
Risco de mexer: quebrar admin/assinaturas, DOCX, assets e cópia de assinatura.
Quando pode mexer: apenas com smoke legado.
Boundary obrigatória se precisar mexer: `LEGACY-H2 — CSP/assets controlled validation`.

## Assets runtime commitados
Área: Assets/static/vendor
Arquivos/Componentes: assets mínimos de runtime em `assets/static/` e templates que os referenciam.
Motivo para não mexer: foram versionados seletivamente para manter legado funcional.
Última validação conhecida: GIT-C5.
Risco de mexer: 404 em `/admin`/`/assinaturas` e regressão visual.
Quando pode mexer: somente com mapa de dependência.
Boundary obrigatória se precisar mexer: `LEGACY-H2 — legacy asset dependency map`.

## Docker volumes
Área: Infra/Docker
Arquivos/Componentes: volumes `postgres_data`, `app_data`, Docker root `/var/lib/docker`.
Motivo para não mexer: podem conter estado operacional local.
Última validação conhecida: H1 `docker compose ps` mostrou Postgres/Redis healthy.
Risco de mexer: perda de dados locais.
Quando pode mexer: só com backup e aprovação humana.
Boundary obrigatória se precisar mexer: `OPS-H2 — Docker data migration/cleanup`.

## Migrations
Área: Database/migrations
Arquivos/Componentes: `backend/alembic/versions/*`, `backend/alembic.ini`.
Motivo para não mexer: Postgres é fonte canônica; migrations exigem política e validação própria.
Última validação conhecida: testes de migrations existentes e compileall H1.
Risco de mexer: divergência schema/runtime e perda de dados.
Quando pode mexer: somente por necessidade de schema aprovada.
Boundary obrigatória se precisar mexer: `DB-H2 — migration change`.

## package-lock
Área: Frontend/dependências
Arquivos/Componentes: `frontend/package-lock.json`, `frontend/itam-platform/package-lock.json` se aplicável.
Motivo para não mexer: lockfiles definem reprodutibilidade e podem refletir árvore errada se editados fora de contexto.
Última validação conhecida: H1 build com Node v22.22.3 passou.
Risco de mexer: drift de dependências e falhas de CI/build.
Quando pode mexer: só em boundary de dependências.
Boundary obrigatória se precisar mexer: `DEPS-H2 — frontend dependency lock review`.

## Untracked remanescentes
Área: Worktree
Arquivos/Componentes: `_migration_proposals/`, `assets/legacy/`, `imports/`, screenshots, `ai-lab/`, testes untracked, docs antigas, `123`, `123.pub`.
Motivo para não mexer: podem conter histórico, dados brutos, artefatos sensíveis ou material experimental.
Última validação conhecida: H1 inventário untracked.
Risco de mexer: apagar evidência útil, expor segredo, commitar lixo ou quebrar boundary.
Quando pode mexer: após triagem humana.
Boundary obrigatória se precisar mexer: `GIT-H2 — untracked safety triage`.

## docs/audit antigos
Área: Documentação/auditoria
Arquivos/Componentes: relatórios e screenshots antigos em `docs/audit/`.
Motivo para não mexer: histórico de decisões e validações.
Última validação conhecida: README existente e FASE 11.
Risco de mexer: perder rastreabilidade.
Quando pode mexer: só para indexar/arquivar sem deletar.
Boundary obrigatória se precisar mexer: `DOCS-H2 — audit docs consolidation`.
