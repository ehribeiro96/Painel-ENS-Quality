# AUDIT-H1 — full project improvement and do-not-touch audit

Data: 2026-06-16T11:28:50-03:00
Boundary: `AUDIT-H1 — full project improvement and do-not-touch audit`
Modo: auditoria somente leitura, com criação exclusiva de documentação em `docs/audit/`.

## Resumo executivo

Status técnico da auditoria: `GO COM RESSALVAS OPERACIONAIS`.

O projeto está em um ponto funcionalmente avançado: backend modular FastAPI, frontend React/Vite, AI Chat com `ollama-lan`, pipeline de importação, legado `/admin` e `/assinaturas`, Docker Engine nativo no WSL, Postgres/Redis e documentação de boundaries recentes. As validações leves executadas nesta auditoria passaram: `compileall` em `backend/app` e `tests` não retornou erro, `npm run build` do frontend passou com Node v22.22.3, Docker Engine respondeu e Postgres/Redis estavam `healthy`.

O principal risco não é uma falha funcional imediata: é o worktree grande e misto. Foram observados 631 untracked no inventário completo posterior, incluindo `_migration_proposals/`, `assets/legacy/`, screenshots, docs/audit antigos, `imports/`, `frontend/package-lock.json`, testes untracked e arquivos `123`/`123.pub`. Isso deve bloquear qualquer edição funcional ampla até triagem humana ou boundary dedicada.

Nenhum stage inicial foi encontrado. Branch: `main`. Relação com origin: `ahead 15`, sem `behind` reportado pelo status local.

## Estado git

Evidência FASE 0:

```text
## main...origin/main [ahead 15]
stage: vazio (`git diff --cached --name-status` sem saída)
commits recentes: HEAD d0fb175 docs(audit): document legacy assets triage; origin/main em 19559d2
```

Riscos:
- `main` está `ahead 15`: há trabalho local ainda não publicado ou não sincronizado.
- Existem muitos untracked antigos fora do escopo.
- Stage inicial estava vazio; portanto a auditoria pôde continuar.

## Escopo

Áreas auditadas:
1. Backend API.
2. Backend domains.
3. AI Chat.
4. Import pipeline.
5. Auth/security.
6. Database/migrations.
7. Frontend React.
8. Legacy `/admin` e `/assinaturas`.
9. Assets/static/vendor.
10. Infra Docker/WSL.
11. CI/CD GitHub Actions.
12. Tests.
13. Docs/audit.
14. Scripts/tools.
15. Untracked/remanescentes.

Fora de escopo: correções funcionais, commits, staging, limpeza de untracked, migrations, alterações em Docker volumes, leitura de `.env*` ou segredos.

## Metodologia

Comandos executados conforme fases 0 a 13, com resultados salvos em `/tmp/audit_h1/` durante a sessão. Os comandos foram de leitura, busca, inventário, validação leve e build. Não houve `git add`, `git reset`, `git checkout`, `git clean`, `push`, `merge`, `rebase`, prune ou `docker compose down -v`.

Validações leves:
- Backend/tests compile: `PASS` — `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests || true` sem saída de erro.
- Frontend build: `PASS` — `npm run build` concluiu: 1818 modules transformed, bundle CSS 39.44 kB gzip 8.01 kB, JS 495.26 kB gzip 148.67 kB, built in 2.16s.
- Docker info: `PASS` — Docker Engine Community 29.5.3, Compose v5.1.4, WSL2, Postgres e Redis containers `healthy`.

## Backend

Evidências:
- Rotas em `backend/app/api/v1/routes`: `ai_chat.py`, `users.py`, `macros.py`, `imports.py`, `auth.py`, `search.py`, `assets.py`, `signatures.py`, `dashboard.py`, `audit.py`.
- Domínios em `backend/app/domains`: `ai_chat`, `imports`, `macros`, `users`, `signatures`, `dashboard`, `assets`, `audit`, `auth`, `movements`.
- Busca FASE 3 encontrou uso recorrente de `APIRouter`, `Depends`, segurança JWT, CORS/CSP, Redis, Postgres e Alembic.
- `except Exception` aparece 15 vezes no escopo backend/tests; `logger.exception` aparece 1 vez.

Avaliação:
- A separação por routes/domains/services está consistente com `AGENTS.md`.
- Backend está compilável.
- O domínio de imports foi extraído para normalização/classificação/parsing/conflitos, indicando arquitetura mais testável.
- Pontos frágeis conservadores: exceções amplas devem ser revisadas por boundary; startup/config depende de variáveis e fallbacks; segurança e headers devem continuar cobertos por testes.

Findings:
- `P2`: reduzir `except Exception` genérico onde houver caminho operacional crítico, sem quebrar UX de erro.
- `P2`: consolidar documentação de contratos API/DTOs para reduzir risco de retorno acidental de model SQLAlchemy cru.
- `P3`: mapear healthcheck/readiness por dependência Postgres/Redis/AI provider com runbook operacional.
- `DO_NOT_TOUCH`: arquitetura modular atual, auth/RBAC, audit logs, movements/macros e import pipeline sem boundary própria.

## AI Chat/Ollama

Evidências:
- Busca FASE 4 encontrou referências extensas a `ollama`, `ollama-lan`, `qwen`, provider, rate limit, sanitização e docs B5.
- Contexto conhecido e docs apontam provider `ollama-lan`, modelo `qwen3:1.7b-64k`, endpoint backend para `/v1/chat/completions` e same-origin UI.
- Testes existentes incluem `tests/test_ai_chat_ollama_provider.py`, `tests/test_ai_chat_rate_limit.py`, `tests/test_ai_chat_hardening.py`, `tests/test_ai_chat_api.py` e `tests/test_ai_chat_provider_mock.py`.

Avaliação:
- `ollama-lan` deve ser preservado como provider validado.
- `qwen3:1.7b-64k` deve ser preservado como baseline documentado.
- Browser deve continuar falando com backend same-origin, não diretamente com o IP LAN.
- Mock não deve voltar como fallback silencioso quando provider real está configurado.
- Sanitização de `<think>` é `DO_NOT_TOUCH` até haver teste específico autorizando mudança.

Findings:
- `DO_NOT_TOUCH`: provider `ollama-lan` validado.
- `DO_NOT_TOUCH`: baseline `qwen3:1.7b-64k`.
- `DO_NOT_TOUCH`: same-origin browser/backend.
- `P3`: manter um smoke test pequeno e explícito para disponibilidade do Ollama LAN, sem transformar indisponibilidade de LAN em bug de frontend.

## Import pipeline

Evidências:
- Busca FASE 5 foi extensa, com 22.932 linhas, confirmando grande superfície em imports, staging, normalizers, classifiers, spreadsheet reader, conflict detection, fixtures e docs.
- Testes relevantes: `test_import_identity_classifier.py`, `test_import_row_classifier.py`, `test_import_conflict_detector.py`, `test_import_lansweeper_normalizer.py`, `test_import_spreadsheet_reader.py`, `test_import_pipeline_units.py`, `test_imports_regression.py`.
- Fixtures versionadas em `tests/fixtures/imports` e `tests/fixtures/uat`.

Avaliação:
- Pipeline B3 parece consistente e deve ser preservado.
- A separação parsing/normalization/classification/conflict detection é uma área estável.
- Risco forte: diretório `imports/` untracked pode conter dados brutos ou evidências reais; não foi aberto além de inventário de paths.
- Testes untracked de import/security exigem revisão humana antes de commit.

Findings:
- `DO_NOT_TOUCH`: pipeline B3 validado e fixtures anonimizadas/versionadas.
- `P1`: `imports/` untracked deve ser classificado por humano antes de qualquer commit/ignore/delete.
- `P2`: criar boundary de higiene de testes untracked para decidir se `tests/test_import_conflict_detector.py` entra no repo.

## Frontend

Evidências:
- 33 arquivos TSX listados; rotas principais em `App.tsx` incluem assets, imports, AI Chat, audit logs, settings.
- FASE 6 encontrou `localStorage` em `useLocalStorageState.ts`, `fetch(` em `api.ts`, sem `console.log`, sem `dangerouslySetInnerHTML`, sem `as any` detectado pela busca.
- `npm run build` passou.
- Componentes centrais encontrados: `AppShell`, `DataTable`, `StateBlocks`, `MoveAssetDialog`, `AiChatPage`, `ImportsPage`, `AssetsPage`.

Avaliação:
- Shell visual B4 deve ser preservado.
- O build atual é um ponto estável.
- `localStorage` parece encapsulado em helper, mas deve continuar sob regra de não armazenar segredo/token sensível sem revisão.
- O CSS global aparece como área grande; evitar refatoração estética ampla sem screenshot/smoke autenticado.

Findings:
- `DO_NOT_TOUCH`: AppShell/shell visual validado B4.
- `DO_NOT_TOUCH`: `DataTable`, `StateBlocks`, `MoveAssetDialog` sem boundary específica.
- `P2`: boundary futura para UX/accessibility review por rota, com screenshots e critérios objetivos.
- `P3`: documentar contrato de `api.ts` e estados loading/empty/error por página.

## Legacy `/admin` e `/assinaturas`

Evidências:
- Busca FASE 7 encontrou templates legados em `assets/templates`, JS `signature-copy.js`, `hero_outlook.html`, DOCX e referências a Bootstrap/admin/assinaturas.
- Docs recentes indicam remoção de Google Fonts e CSP validado sem `unsafe-eval` e sem CSP malformada.
- Foram detectadas referências externas remanescentes em material legado/hero, incluindo URL de imagem externa em template legacy; tratar somente em boundary separada.

Avaliação:
- Legado está funcional e validado recentemente; mexer sem boundary é alto risco.
- CSP faseada com `unsafe-inline` legado pode ser aceitável temporariamente se documentada e coberta por validação.
- Assets runtime mínimos commitados devem ser preservados.
- `assets/legacy/` e DOCX grande não devem ser mexidos nesta auditoria.

Findings:
- `DO_NOT_TOUCH`: remoção de Google Fonts já validada.
- `DO_NOT_TOUCH`: assets runtime commitados.
- `DO_NOT_TOUCH`: CSP legado validado.
- `P2`: abrir boundary própria para inventariar `assets/legacy/` e referências externas remanescentes.
- `P3`: avaliar remoção faseada de `unsafe-inline` somente com teste visual/funcional do legado.

## Segurança

Evidências:
- Scanner FASE 8 foi executado apenas sobre arquivos tracked, excluindo `.env`, binários grandes, builds e imagens.
- Regex de alto risco retornou muitos falsos positivos/documentação/testes/placeholders.
- Detecção específica não encontrou padrões reais `sk-...`, `ghp_...` ou AWS `AKIA...` no output processado.
- Achados recorrentes são nomes de variáveis (`JWT_SECRET`, `DATABASE_URL`, `POSTGRES_PASSWORD`, `REDIS_URL`, `COMPOSIO_API_KEY`) em docs, testes, `.env.example`, scripts e compose.

Classificação:
- Nome de variável: esperado em config, docs e testes.
- Placeholder: esperado em `.env.example`, Docker e docs sanitizadas.
- Teste: esperado em testes de startup, AI Chat e mock provider.
- Documentação: muitos achados em relatórios e evidências históricas.
- Falso positivo: service-desk sobre token de certificado, documentação de segurança e validadores que bloqueiam segredos.
- Risco real: não confirmado nesta auditoria. Não houve impressão de segredo real.

Riscos residuais:
- `123` e `123.pub` untracked têm nome compatível com chave/artefato; não foram abertos e exigem revisão humana.
- `imports/` untracked pode conter dados brutos.
- Relatórios históricos podem conter dumps sanitizados; não limpar sem boundary.

## Infra/Docker/CI

Evidências:
- Docker Engine Community 29.5.3, Compose v5.1.4, kernel WSL2, Docker Root Dir `/var/lib/docker`.
- `docker compose ps`: Postgres e Redis `healthy`; app não listado no momento do comando.
- `docker-compose.yml` usa Postgres 17 alpine, Redis 7 alpine, app build via `backend/Dockerfile`, healthcheck em `/health/ready`, volumes `postgres_data` e `app_data`.
- `.github/workflows/docker-build-push.yml` está untracked.

Avaliação:
- Docker Engine nativo WSL é área estável e deve ser preservada.
- Volumes Docker são `DO_NOT_TOUCH`.
- CI/CD com workflow docker-build-push untracked é risco de release se for commitado sem revisão de secrets, registry, tags e permissões.

Findings:
- `P1`: não versionar workflow de build/push sem revisão humana de secrets e permissões.
- `P2`: criar boundary de CI quality gates com build/test explícitos antes de publish.
- `DO_NOT_TOUCH`: Docker volumes e runtime nativo validado.

## Testes

Evidências:
- 31 arquivos Python de teste rastreados pelo inventário `search_files`.
- Testes cobrem AI Chat, imports, security headers, auth, assets, macros, legacy, signatures, migrations e operational contracts.
- `compileall` passou.
- FASE 10 listou `__pycache__` em `tests/`; artefato local ignorável, não deve ser commitado.

Avaliação:
- Cobertura por domínio é boa para o estágio atual.
- Falta uma boundary para padronizar markers/tiers: unit, integration, smoke, operational.
- Não rodar pytest amplo sem escopo se houver árvores copiadas/relatórios que causem import mismatch.

Findings:
- `DO_NOT_TOUCH`: testes de AI Chat/import/legacy que validam boundaries recentes.
- `P2`: criar markers de pytest e comandos canônicos por tipo de validação.
- `P2`: revisar testes untracked antes de commit.

## Documentação

Evidências:
- FASE 11 encontrou documentação ampla, com status `GO`, `PARTIAL`, `NO-GO`, next boundary, riscos, AI/Ollama, B4/B5, GIT-C e QA-C.
- `docs/audit/README.md` já atua como índice operacional extenso.
- Há docs antigos e relatórios de evidência untracked em `docs/audit/` e screenshots.

Avaliação:
- Documentação é valiosa, mas está volumosa e parcialmente duplicada.
- Não limpar agora: risco de apagar histórico útil.
- Próxima melhoria segura é índice/arquivamento, não deleção.

Findings:
- `P2`: criar boundary `DOCS-H2` para consolidar índice, status e histórico.
- `DO_NOT_TOUCH`: docs/audit antigos até decisão humana.

## Untracked/remanescentes

Inventário resumido:
- Total completo observado: 631 untracked.
- Grupos principais: `_migration_proposals/`, `assets/legacy/`, `docs/audit/screenshots/`, `ai-lab/`, `docs/audit/`, `assets/static/icons/`, `docs/`, `imports/`, `tests/`, `.github/workflows/`, `frontend/package-lock.json`, `123`, `123.pub`, amostras docx/pptx.

Classificação conservadora:
- `KEEP_UNTRACKED_LOCAL`: `123`, `123.pub` até revisão humana; não abrir/commit/delete.
- `COMMIT_CANDIDATE`: docs H1 criados nesta boundary; possivelmente alguns docs AI/Docker recentes somente após revisão.
- `REVIEW_HUMAN`: `_migration_proposals/`, `ai-lab/`, `docs/hermesops/`, `tests/test_import_conflict_detector.py`, `tests/test_security_headers.py`, `.github/workflows/docker-build-push.yml`.
- `IGNORE_CANDIDATE`: screenshots antigas e outputs gerados, somente após boundary.
- `DELETE_CANDIDATE_MANUAL_ONLY`: artefatos temporários e amostras, somente com aprovação humana.
- `DO_NOT_TOUCH`: `imports/`, `assets/legacy/`, DOCX grande, `frontend/package-lock.json`, docs/audit antigos.

## Riscos

Ver `HERMES_RISK_REGISTER_H1.md` para registro estruturado. Top riscos:
1. Worktree misto e grande.
2. Arquivos untracked possivelmente sensíveis (`123`, `123.pub`, `imports/`).
3. Workflow docker build/push untracked.
4. Docs/evidências históricas volumosas e duplicadas.
5. `assets/legacy/` não triado.
6. DOCX grande não decidido.
7. Possível referência externa legada remanescente.
8. Exceções genéricas no backend.
9. Falta de markers/tier de testes.
10. `main` ahead 15.

## Onde melhorar

1. Triagem segura de untracked por grupo.
2. Boundary de CI/CD antes de qualquer build/push.
3. Consolidação de docs/audit e decisão de histórico.
4. Markers e comandos canônicos de testes.
5. Revisão de exceções genéricas backend.
6. Runbook de health/readiness com Postgres/Redis/Ollama.
7. Inventário de `assets/legacy/`.
8. UX/accessibility review por rota com screenshots.
9. Revisão de referências externas no legado.
10. Contratos de DTO/API por rota crítica.

## Onde não mexer

1. AI Chat provider `ollama-lan`.
2. Baseline `qwen3:1.7b-64k`.
3. Sanitização de `<think>`.
4. Same-origin browser/backend do AI Chat.
5. Import pipeline B3.
6. Frontend shell/AppShell/DataTable/StateBlocks validado B4.
7. Legacy CSP/removal Google Fonts validada.
8. Assets runtime legados commitados.
9. Docker volumes.
10. Migrations e package-lock.

## Próximas boundaries recomendadas

1. `GIT-H2 — untracked safety triage`.
2. `DOCS-H2 — audit docs consolidation and index hygiene`.
3. `TEST-H2 — pytest markers and validation command standardization`.
4. `CI-H2 — GitHub Actions build/push review without publishing`.
5. `LEGACY-H2 — legacy assets and external-reference inventory`.
6. `BACKEND-H2 — exception handling and API contract hardening`.
7. `FRONTEND-H2 — route UX/accessibility review with authenticated screenshots`.
8. `OPS-H2 — health/readiness/runbook consolidation`.

## Decisão final

`GO` para finalizar esta auditoria e usar os relatórios H1 como base de decisão.

`NO-GO` para qualquer correção funcional imediata enquanto o worktree untracked não for triado e enquanto não houver boundary específica. Não mexer em código funcional, migrations, Docker volumes, AI Chat/Ollama, ImportService, frontend shell, CSP, assets legados ou package-lock sem aprovação humana.
