# Selective Commits GIT-C2

Data/hora: 2026-06-15, America/Sao_Paulo

Status: `PARTIAL`

## 1. Resumo Executivo

A boundary `GIT-C2 — selective commits by approved boundary plan` executou commits seletivos por boundary sem usar `git add .`, sem misturar os grupos aprovados e sem incluir arquivos ambíguos sem revisão clara.

Foram concluídos e commitados os blocos:

- `G1` B0/B1 segurança e auditoria base
- `G2` B2 AI Chat hardening
- `G3` B3 import pipeline/staging
- `G4` B4 frontend shell/UX
- `G5` INFRA-D1 Docker WSL docs/evidências
- `G6` B5 AI Chat Ollama LAN/Qwen3

O pacote documental restante de `docs/audit/` foi analisado, mas ficou para `GIT-C3` porque `git diff --cached --check` revelou whitespace/EOF legados em vários arquivos de auditoria.

## 2. Estado Inicial

- branch: `main`
- upstream: `origin/main`
- ahead/behind: `ahead 1`
- stage inicial: vazio
- worktree inicial: sujo, com mudanças preexistentes em múltiplas boundaries

## 3. Commits Criados

### G1

Commit:

- `b8aef41 chore(security): close hygiene and audit base`

Arquivos principais:

- [/.gitignore](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.gitignore)
- [tools/composio_client.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tools/composio_client.py)
- [docs/SECURITY_HYGIENE_B0_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/SECURITY_HYGIENE_B0_REPORT.md)
- [docs/RELEASE_DOCS_HYGIENE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/RELEASE_DOCS_HYGIENE_REPORT.md)
- [docs/WORKTREE_TRIAGE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WORKTREE_TRIAGE_REPORT.md)
- [docs/CRITICAL_FIX_ROUND2_MANIFEST.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_MANIFEST.md)
- [docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md)
- [docs/GENERAL_PROJECT_AUDIT_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_AUDIT_REPORT.md)
- [docs/GENERAL_PROJECT_EDITING_ROADMAP.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_EDITING_ROADMAP.md)
- [docs/GENERAL_PROJECT_NEXT_ACTIONS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_NEXT_ACTIONS.md)
- [docs/GENERAL_PROJECT_RISK_REGISTER.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_RISK_REGISTER.md)
- [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
- [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md)

### G2

Commit:

- `4d8fb3e feat(ai-chat): harden backend chat runtime`

Arquivos principais:

- [backend/app/api/v1/routes/ai_chat.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/api/v1/routes/ai_chat.py)
- [backend/app/core/config/settings.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/core/config/settings.py)
- [backend/app/domains/ai_chat/rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/ai_chat/rate_limit.py)
- [tests/test_ai_chat_api.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_api.py)
- [tests/test_ai_chat_hardening.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_hardening.py)
- [tests/test_ai_chat_provider_mock.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_provider_mock.py)
- [tests/test_ai_chat_rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_rate_limit.py)
- [docs/AI_CHAT_BACKEND_HARDENING_B2_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_BACKEND_HARDENING_B2_REPORT.md)
- [docs/AI_CHAT_RATE_LIMIT_REDIS_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_RATE_LIMIT_REDIS_REPORT.md)
- [docs/CSP_HARDENING_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CSP_HARDENING_REPORT.md)

### G3

Commit:

- `b88f413 feat(imports): validate import staging pipeline`

Arquivos principais:

- [backend/app/domains/imports/service.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/service.py)
- [backend/app/domains/imports/normalization/asset_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/normalization/asset_normalizer.py)
- [backend/app/domains/imports/normalization/__init__.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/normalization/__init__.py)
- [backend/app/domains/imports/normalization/lansweeper_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/normalization/lansweeper_normalizer.py)
- [backend/app/domains/imports/parsing/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/parsing/)
- [backend/app/domains/imports/classification/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/)
- [tests/fixtures/imports/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/fixtures/imports/)
- [tests/test_import_identity_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_identity_classifier.py)
- [tests/test_import_lansweeper_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_lansweeper_normalizer.py)
- [tests/test_import_row_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_row_classifier.py)
- [tests/test_import_spreadsheet_reader.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_spreadsheet_reader.py)
- [docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md)
- [docs/IMPORT_SERVICE_REFACTOR_MANIFEST.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_SERVICE_REFACTOR_MANIFEST.md)
- [docs/IMPORT_SERVICE_REFACTOR_PLAN.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_SERVICE_REFACTOR_PLAN.md)
- [docs/IMPORT_SERVICE_REFACTOR_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_SERVICE_REFACTOR_REPORT.md)

### G4

Commit:

- `c2ec617 feat(frontend): repair Sentinel shell and authenticated UX`

Arquivos principais:

- [frontend/itam-platform/src/components/AppShell.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/AppShell.tsx)
- [frontend/itam-platform/src/components/DataTable.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/DataTable.tsx)
- [frontend/itam-platform/src/components/StateBlocks.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/StateBlocks.tsx)
- [frontend/itam-platform/src/components/ai-chat/ChatComposer.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/ai-chat/ChatComposer.tsx)
- [frontend/itam-platform/src/pages/AssetsPage.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/pages/AssetsPage.tsx)
- [frontend/itam-platform/src/pages/AuditLogsPage.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/pages/AuditLogsPage.tsx)
- [frontend/itam-platform/src/pages/ImportsPage.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/pages/ImportsPage.tsx)
- [frontend/itam-platform/src/pages/SettingsPage.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/pages/SettingsPage.tsx)
- [frontend/itam-platform/src/styles.css](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/styles.css)
- [docs/FRONTEND_AUTHENTICATED_VISUAL_SMOKE_B4D_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_AUTHENTICATED_VISUAL_SMOKE_B4D_REPORT.md)
- [docs/FRONTEND_MANUAL_VISUAL_SMOKE_B4B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_MANUAL_VISUAL_SMOKE_B4B3_REPORT.md)
- [docs/FRONTEND_RUNTIME_NORMALIZATION_B4A2.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_RUNTIME_NORMALIZATION_B4A2.md)
- [docs/FRONTEND_SHELL_UX_B4A_BASELINE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_SHELL_UX_B4A_BASELINE_REPORT.md)
- [docs/FRONTEND_SHELL_UX_B4B_SMOKE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_SHELL_UX_B4B_SMOKE_REPORT.md)
- [docs/FRONTEND_VISUAL_REPAIR_B4C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_VISUAL_REPAIR_B4C_REPORT.md)
- [docs/FRONTEND_VISUAL_SMOKE_B4B2_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_VISUAL_SMOKE_B4B2_REPORT.md)
- [docs/FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md)
- [docs/VISUAL_SMOKE_MANUAL_RUNBOOK.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/VISUAL_SMOKE_MANUAL_RUNBOOK.md)
- [frontend/itam-platform/docs/brand/mockups/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/docs/brand/mockups/)
- [frontend/itam-platform/docs/brand/reference/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/docs/brand/reference/)
- [frontend/itam-platform/docs/local-crawl/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/docs/local-crawl/)
- [frontend/itam-platform/docs/ui-audit/screenshots/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/docs/ui-audit/screenshots/)
- [frontend/itam-platform/src/assets/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/assets/)

### G5

Commit:

- `4811f9a docs(infra): document native Docker Engine on WSL`

Arquivos principais:

- [.codex-browser-runtime/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.codex-browser-runtime/)
- [.firecrawl/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.firecrawl/)
- [.github/workflows/quality-gates.yml](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.github/workflows/quality-gates.yml)
- [docs/LOCAL_DOCKER_WSL_NATIVE_RUNBOOK.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/LOCAL_DOCKER_WSL_NATIVE_RUNBOOK.md)
- [docs/WSL_NATIVE_DOCKER_ENGINE_D1_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1_REPORT.md)
- [docs/WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md)

### G6

Commit:

- `48550ef feat(ai-chat): add Ollama LAN Qwen3 provider`

Arquivos principais:

- [backend/app/domains/ai_chat/providers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/ai_chat/providers.py)
- [tests/test_ai_chat_ollama_provider.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_ollama_provider.py)
- [docs/AI_CHAT_OLLAMA_B5A_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_B5A_REPORT.md)
- [docs/AI_CHAT_OLLAMA_LAN_B5B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5B_REPORT.md)
- [docs/AI_CHAT_OLLAMA_LOCAL_RUNBOOK.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LOCAL_RUNBOOK.md)
- [docs/HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md)
- [docs/HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md)
- [docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md)
- [docs/LOCAL_AI_BENCHMARK.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/LOCAL_AI_BENCHMARK.md)
- [docs/LOCAL_AI_MODEL_STRATEGY.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/LOCAL_AI_MODEL_STRATEGY.md)
- [docs/LOCAL_MODEL_ROUTER_PROPOSAL.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/LOCAL_MODEL_ROUTER_PROPOSAL.md)
- [docs/OLLAMA_LOCAL_MODEL_PROFILE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/OLLAMA_LOCAL_MODEL_PROFILE.md)

## 4. Validações Executadas

Em cada commit:

- `git diff --cached --name-status`
- `git diff --cached --check`
- conferência manual dos grupos antes do `git commit`

Falhas de index tratadas por exclusão seletiva do arquivo problemático, sem `git add .` e sem edição para "facilitar" o commit:

- `tests/test_security_headers.py`
- `tests/test_import_conflict_detector.py`
- `.github/workflows/docker-build-push.yml`
- `docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md`

## 5. Arquivos Ambíguos Deixados para GIT-C3

- [backend/app/main.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/main.py)
- [.env.example](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.env.example)
- [docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md)
- [docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md)
- [tests/test_hermes_icons_security.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_hermes_icons_security.py)
- [tests/test_import_conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_conflict_detector.py)
- [tests/test_security_headers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_security_headers.py)
- [frontend/package-lock.json](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/package-lock.json)
- [.github/workflows/docker-build-push.yml](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.github/workflows/docker-build-push.yml)
- [docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md)
- [docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md)

## 6. Arquivos Excluídos

- `_migration_proposals/`
- `ai-lab/`
- `assets/`
- `imports/`
- `docx_sample.md`
- `docx_template_output.md`
- `pptx_sample.md`
- `pptx_template_output.md`
- `frontend/package-lock.json`
- `.env.example`
- `backend/app/main.py`

## 7. Scanner Redigido

Resultado resumido:

- `COMPOSIO_API_KEY`: nome de variável no client de Composio, sem valor exposto.
- `DATABASE_URL`, `REDIS_URL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`: nomes de configuração/documentação.
- `token`, `secret`, `password`, `bearer`: aparecem apenas como nomes funcionais em docs, testes e relatórios.
- `IP LAN documentado`: esperado em documentação de Ollama LAN e provider backend.
- Nenhum segredo real foi impresso.

## 8. Stage Final

- stage: vazio após os commits seletivos principais.
- arquivos excluídos dos grupos por higiene/qualidade permanecem fora do stage.

## 9. Worktree Restante

- `backend/app/main.py`
- `.env.example`
- `.github/workflows/docker-build-push.yml`
- `docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md`
- `docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md`
- `docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md`
- `tests/test_hermes_icons_security.py`
- `tests/test_import_conflict_detector.py`
- `tests/test_security_headers.py`
- `frontend/package-lock.json`

## 10. Próxima Ação Recomendada

`GIT-C3 — revisar ambíguos remanescentes`

Prioridade sugerida:

1. `backend/app/main.py`
2. `tests/test_security_headers.py`
3. `tests/test_import_conflict_detector.py`
4. `docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md`
5. `docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md`
6. `docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md`
7. `docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md`
8. `tests/test_hermes_icons_security.py`
9. `frontend/package-lock.json`
