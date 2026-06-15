# Auditoria geral do projeto Painel ENS-Quality

Data: 2026-06-12 09:13:51 -03
Modo: auditoria segura, não destrutiva, sem alteração de código-fonte
Status: GO para planejamento; não é GO de release
Índice operacional da auditoria: [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
Próxima boundary recomendada: [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md)

## Resumo executivo

O projeto está funcionalmente estruturado como uma aplicação web operacional com backend FastAPI, frontend React/Vite/TypeScript, PostgreSQL/Redis via Docker Compose, Alembic para migrations, autenticação JWT/RBAC, módulos de ativos, movimentações, macros, importação/staging, auditoria e AI Chat.

A auditoria confirmou que os gates principais direcionados passam quando executados com escopo correto:

- `compileall`: OK.
- `pytest tests -q -o addopts=''`: 128 passed, 22 skipped, 1 warning.
- `pytest tests --collect-only -q -o addopts=''`: 150 testes coletados.
- `npm run build` em `frontend/itam-platform`: OK.
- `alembic heads`: `0006_ai_chat (head)`.
- `ruff check backend tests scripts`: OK.

O principal problema operacional não é uma falha imediata de build/test, mas sim higiene e isolamento do worktree: há alterações rastreadas em backend, frontend e testes, além de grande volume de arquivos untracked em `docs/`, `ai-lab/`, `backend/`, `frontend/`, `tests/`, `_migration_proposals/`, `assets/` e outros diretórios. A próxima edição deve começar com congelamento/higiene para não misturar features, auditoria, experimentos de IA e alterações funcionais.

## Estado atual do repositório

Comando inicial:

```bash
git status --short --branch
```

Resultado resumido:

- Branch: `main`.
- Relação com upstream: `main...origin/main [ahead 1]`.
- Ahead/behind: `1` commit à frente, `0` atrás.
- Staged changes: nenhum arquivo staged.
- Worktree: suja.

Arquivos modificados rastreados:

| Arquivo | Diff resumido |
|---|---:|
| `backend/app/api/v1/routes/ai_chat.py` | +8/-17 |
| `backend/app/domains/imports/normalization/asset_normalizer.py` | +0/-10 |
| `backend/app/domains/imports/service.py` | +19/-133 |
| `backend/app/main.py` | +25/-7 |
| `frontend/itam-platform/src/components/AppShell.tsx` | +42/-22 |
| `frontend/itam-platform/src/components/StateBlocks.tsx` | +9/-2 |
| `frontend/itam-platform/src/pages/AssetsPage.tsx` | +29/-7 |
| `frontend/itam-platform/src/pages/AuditLogsPage.tsx` | +13/-15 |
| `frontend/itam-platform/src/pages/ImportsPage.tsx` | +30/-2 |
| `frontend/itam-platform/src/pages/SettingsPage.tsx` | +7/-6 |
| `frontend/itam-platform/src/styles.css` | +65/-2768 |
| `tests/test_ai_chat_api.py` | +2/-2 |
| `tests/test_ai_chat_hardening.py` | +22/-7 |
| `tests/test_ai_chat_provider_mock.py` | +1/-1 |

Untracked relevantes por grupo:

- `_migration_proposals`: 349 arquivos.
- `assets`: 248 arquivos.
- `frontend`: 63 arquivos.
- `docs`: 42 arquivos.
- `ai-lab`: 28 arquivos.
- `tests`: 19 arquivos.
- `backend`: 9 arquivos.
- `.firecrawl`: 10 arquivos.
- `.github`: 2 arquivos.
- outros artefatos soltos: `docx_sample.md`, `pptx_sample.md`, etc.

## Stack detectada

Backend:

- Python 3.12.
- FastAPI `0.115.12`.
- SQLAlchemy async `2.0.49`.
- Alembic `1.15.2`.
- PostgreSQL via `asyncpg`.
- Redis `5.2.1`.
- Pydantic v2 / pydantic-settings.
- JWT via `python-jose`.
- `structlog` para logging.

Frontend:

- React `19.1.0`.
- TypeScript `5.8.3`.
- Vite `6.3.5`.
- React Router `7.6.2`.
- TanStack Query `5.100.14`.
- React Hook Form + Zod.
- CSS global em `frontend/itam-platform/src/styles.css`.

Infra:

- `docker-compose.yml` com `postgres`, `redis`, `app`.
- Docker Desktop/WSL não disponível no ambiente atual: `docker compose config --services` falhou porque Docker não está integrado a esta distro WSL.

Banco:

- Alembic com cadeia linear de 6 migrations: `0001_initial_itam` -> `0006_ai_chat`.
- `alembic heads` retorna `0006_ai_chat (head)`.

IA/Hermes/Ollama:

- Hermes default operacional documentado: `openai-codex` / `gpt-5.5` / `context_length 262144` / `agent.tool_use_enforcement: true`.
- Ollama LAN existe, mas não deve ser default.
- `qwen2.5-coder:7b-hermes-64k` funciona manualmente.
- `llama3.2:3b-hermes-64k` continua não confiável via wrapper Hermes por retorno JSON/tool-call-like.
- Qwen3 não deve ser promovido.

## Arquitetura atual

### Backend

Estrutura principal:

- `backend/app/main.py`: composição FastAPI, CORS, middleware de contexto, rate limit in-memory genérico, headers de segurança, healthchecks, métricas e montagem do frontend/legado.
- `backend/app/api/v1/router.py`: registra rotas de auth, users, assets, dashboard, imports, signatures, macros, ai-chat, audit e search.
- `backend/app/core`: settings, database, security, RBAC, startup, health, frontend/legacy mounting, observabilidade.
- `backend/app/domains`: módulos de domínio para assets, movements, macros, imports, audit, auth, users, signatures, ai_chat, dashboard.
- `backend/app/shared`: modelos base, paginação, snapshots, transações, enums e contexto de auditoria.

Rotas principais identificadas:

- Auth: login, refresh, logout, me.
- Assets: list/create/get/update/delete/move/history.
- Imports: upload Lansweeper/spreadsheet, preview, staging, conflicts, validation-errors, mapping, apply, cancel, report.
- Macros: templates, render, generate, generations, mark copied, autocomplete, suggested macro for movement.
- AI Chat: health, conversations, messages.
- Audit/search/dashboard/signatures.

### Frontend

Estrutura principal:

- `frontend/itam-platform/src/App.tsx`: rotas SPA e guards por autenticação/role.
- `frontend/itam-platform/src/lib/api.ts`: client central de API, refresh 401, mapeamento de erros de AI Chat.
- `frontend/itam-platform/src/lib/auth.tsx`: provider de autenticação, refresh e logout.
- `frontend/itam-platform/src/pages`: páginas de dashboard, assets, imports, macros, AI Chat, audit logs, settings etc.
- `frontend/itam-platform/src/components`: AppShell, DataTable, MoveAssetDialog, StateBlocks, componentes de identidade visual.
- `frontend/itam-platform/src/styles.css`: estilo global; está no diff com grande redução de linhas.

### Banco/migrations

- `backend/alembic/env.py` usa `settings.database_url` e `Base.metadata`.
- `backend/alembic/versions` contém 6 revisions, cadeia linear sem múltiplos heads detectados.
- Modelos usam mixins comuns e soft delete em entidades principais.

### Legado

- Legado de assinaturas permanece montado em `/admin` e `/assinaturas`.
- CSP diferencia rotas legadas de rotas SPA/API.

## Auditoria de segurança

### Achados de segurança e higiene

1. Presença de arquivos sensíveis locais por nome:
   - `.env` existe.
   - `.env.bak_20260603_132713` existe.
   - `data/`, `backups/`, `uat_evidence/` existem.
   - Nenhum desses arquivos foi lido nesta auditoria.

2. Possível segredo hardcoded em arquivo untracked:
   - `tools/composio_client.py`, linhas próximas de 17/24/28, contém `COMPOSIO_API_KEY`/`api_key` com valor redigido no scanner.
   - Recomendação: tratar como risco alto; remover do worktree ou substituir por leitura de env/credential store antes de qualquer commit.

3. Configuração possivelmente sensível em arquivo untracked:
   - `.vscode/settings.json`, linha 2, contém `CodeGPT.apiKey` com valor redigido.
   - Recomendação: não versionar; mover para configuração local ignorada.

4. `docker-compose.yml` contém credenciais padrão para ambiente local:
   - `POSTGRES_PASSWORD: itam`.
   - Como compose local/dev, severidade média; em produção, alta. O próprio app exige `ADMIN_PASSWORD` via variável.

5. CORS:
   - `CORSMiddleware` só é adicionado se `settings.allowed_origins` não estiver vazio.
   - Quando habilitado, usa `allow_methods=['*']`, `allow_headers=['*']` e `allow_credentials=True`.
   - Risco: precisa garantir que `allowed_origins` nunca seja wildcard com credentials em ambiente sensível.

6. JWT/Auth/RBAC:
   - `get_current_user` valida token, existência e status ativo.
   - `require_role` centraliza autorização por role.
   - Settings bloqueiam `jwt_secret_key` padrão em produção.
   - Frontend possui guard de role, mas segurança real está no backend.

7. Headers de segurança:
   - CSP estrito para SPA/API; CSP legado mais permissivo em rotas legadas com report-only estrito.
   - `x-content-type-options`, `x-frame-options`, `referrer-policy`, `permissions-policy` aplicados.

8. Upload/importação:
   - Limite de tamanho via `settings.upload_max_mb`.
   - Limite de linhas via `settings.import_max_rows`.
   - Há testes para CSV malicioso/formula injection e extensões inválidas.

9. Logs:
   - Middleware registra IP, user_id, rota, status, duração e contexto. Não foi visto logging direto de payloads nem tokens nos arquivos lidos.

## Auditoria backend

### Pontos fortes

- Arquitetura modular por domínio.
- DTOs/schemas explícitos em rotas principais.
- Transações encapsuladas por `commit_or_rollback` nas mutações relevantes.
- Auditoria explícita em criação/update/delete/move/import/macro.
- Healthchecks e métricas existem.
- Testes cobrem auth, assets, imports, macros, AI Chat, migrations e rotas legadas.
- `compileall` e `ruff` passaram.

### Áreas frágeis

1. `ImportService` é muito grande:
   - `backend/app/domains/imports/service.py`: 733 linhas.
   - Já existem novos módulos untracked de classificação, parsing e normalização, sugerindo refatoração em andamento.
   - Risco: editar importação/staging agora sem consolidar os untracked pode quebrar fluxo Lansweeper.

2. `AssetService.move` salva movimentação, atualiza ativo e audita, mas a macro automática fica em endpoint separado `/movements/{id}/suggested-macro`.
   - Regra do projeto: macro oficial só pode ser gerada depois da movimentação salva.
   - Estado atual parece respeitar a regra, mas fluxo completo depende do frontend chamar a geração/cópia corretamente.

3. Rate limit genérico em `main.py` é in-memory.
   - Para multi-worker/multi-container, pode não ser suficiente.
   - AI Chat já tem abstração nova de rate limit em arquivo untracked `backend/app/domains/ai_chat/rate_limit.py`.

4. Responses de algumas rotas retornam entidades ORM com `response_model`.
   - Funciona com Pydantic, mas deve continuar sendo monitorado para não retornar model cru em endpoint sensível.

5. Múltiplas mudanças backend já estão no worktree.
   - Não editar backend novo antes de estabilizar e decidir se essas mudanças entram, são separadas ou descartadas.

## Auditoria frontend

### Pontos fortes

- Rotas protegidas por `ProtectedRoute` e `RoleGuard`.
- API client central com refresh automático e tratamento de 401.
- Uso de React Query para dados e invalidação.
- Páginas principais existentes para ativos, imports, macros, audit logs, settings e AI Chat.
- Build frontend passou.

### Áreas frágeis

1. `styles.css` teve redução massiva no diff:
   - +65/-2768.
   - Risco alto de regressão visual ou classes órfãs/removidas sem cobertura visual automática.

2. Páginas grandes:
   - `AssetsPage.tsx`: 481 linhas.
   - `ImportsPage.tsx`: 429 linhas.
   - Risco de baixa coesão, bugs de estado e dificuldade de evolução.

3. UX/UI:
   - Há estados de loading/error via `StateBlocks`, mas a consistência precisa de smoke visual/manual.
   - Arquivos de crawl/screenshot untracked indicam auditorias visuais anteriores; devem ser consolidados antes de mais redesign.

4. Rotas protegidas no frontend não substituem RBAC backend.
   - Toda nova ação sensível deve ter dependência backend apropriada.

5. AI Chat no frontend depende de flags/env e mensagens de erro específicas.
   - Manter mock/offline como caminho seguro para testes.

## Auditoria banco e dados

### Pontos fortes

- Alembic chain linear: `0001` a `0006`.
- `alembic heads` retornou um único head.
- Modelos possuem índices para assets, imports/staging e conflicts.
- Soft delete e campos de auditoria são padrão em entidades via mixins.

### Riscos

1. Não foi executado `alembic current` nem `alembic check` porque isso depende do DB alvo online e poderia ser interpretado como interação com ambiente real. Apenas `alembic heads` foi executado.
2. Constraints únicas em `Asset.serial` e `Asset.patrimony` podem conflitar com importações sujas se normalização não for correta.
3. Import staging usa JSONB para payloads; útil, mas exige cuidado com índices e crescimento.
4. Sem validação de DB online, não há confirmação nesta auditoria de que o banco local atual está no head.

## Auditoria testes/build

### Comandos executados

```bash
PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts
```

Resultado: OK.

```bash
PYTHONPATH=backend timeout 120 .venv/bin/python -m pytest tests --collect-only -q -o addopts=''
```

Resultado: 150 testes coletados, 1 warning.

```bash
PYTHONPATH=backend timeout 300 .venv/bin/python -m pytest tests -q -o addopts=''
```

Resultado: 128 passed, 22 skipped, 1 warning.

```bash
PYTHONPATH=backend timeout 120 .venv/bin/python -m ruff check backend tests scripts
```

Resultado: All checks passed.

```bash
cd backend && timeout 60 ../.venv/bin/python -m alembic heads
```

Resultado: `0006_ai_chat (head)`.

```bash
cd frontend/itam-platform && timeout 180 npm run build
```

Resultado: build OK.

```bash
docker compose config --services
```

Resultado: falhou porque Docker não está disponível/integrado nesta distro WSL.

### Observação importante

A primeira tentativa de `pytest --collect-only` sem restringir `tests` coletou também `_validation/`, `exports/` e `imports/`, causando 91 erros de import mismatch e contaminação por cópias/release candidates. Isso é uma limitação de higiene de árvore/test discovery, não uma falha dos testes principais quando executados com escopo correto.

## Auditoria AI/Hermes/Ollama

Estado recomendado atual:

- Manter Hermes default em `openai-codex` / `gpt-5.5`.
- Manter `model.context_length: 262144`.
- Manter `agent.tool_use_enforcement: true`.
- Não promover Ollama LAN como default.
- Usar `qwen2.5-coder:7b-hermes-64k` manualmente quando necessário.
- Não usar `llama3.2:3b-hermes-64k` via wrapper Hermes como default porque responde JSON/tool-call-like.
- Não promover Qwen3.

Arquivos AI/Hermes/Ollama relevantes:

- `docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md`
- `docs/HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md`
- `docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md`
- `docs/OLLAMA_LOCAL_MODEL_PROFILE.md`
- `docs/HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md`
- `docs/LOCAL_AI_BENCHMARK.md`
- `docs/LOCAL_AI_MODEL_STRATEGY.md`
- `docs/LOCAL_MODEL_ROUTER_PROPOSAL.md`
- `ai-lab/ollama-benchmark/`
- `ai-lab/ollama-modelfiles/`
- `ai-lab/prompts/`

Risco principal: há muitos artefatos e relatórios de experimentos locais. Antes de integrar IA local ao produto, consolidar documentação e separar scripts úteis de resultados temporários.

## Principais conclusões

1. O projeto está testável e buildável no escopo correto.
2. O worktree está muito sujo; próxima edição deve começar por higiene e congelamento.
3. Há pelo menos dois achados de segurança/higiene em arquivos untracked (`tools/composio_client.py` e `.vscode/settings.json`) que não devem ser commitados como estão.
4. Importação/staging e CSS/global UI são as áreas mais frágeis para editar agora.
5. Docker não pôde ser validado por ausência de integração WSL/Docker Desktop.
6. Banco/migrations parecem organizados, mas sem validação de DB online nesta rodada.
7. AI local deve permanecer manual/experimental.

## Limitações da auditoria

- `.env`, `.env.bak`, dados reais, dumps, bancos locais e evidências sensíveis não foram lidos.
- Docker não pôde ser validado porque o comando `docker` não está disponível nesta distro WSL.
- Não foi executado `alembic current/check` por depender de DB alvo online.
- Não foi executado benchmark Ollama, conforme regra.
- Não foi feita auditoria visual em navegador.
- Não houve correção de código nesta rodada.
