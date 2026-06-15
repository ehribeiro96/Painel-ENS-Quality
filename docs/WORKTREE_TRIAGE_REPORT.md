# Worktree Triage Report

- Data/hora: 2026-06-12 10:21:03 -03
- Objetivo: classificar o worktree antes de qualquer edição funcional e propor boundaries de commit sem alterar código.
- Branch: `main`
- Upstream: `origin/main`
- Ahead/behind: `main...origin/main [ahead 1]`
- Arquivos tracked modificados: `14`
- Arquivos untracked: `786`
- Arquivos staged: `0`
- B0 segurança/higiene: iniciado e concluído em [docs/SECURITY_HYGIENE_B0_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/SECURITY_HYGIENE_B0_REPORT.md)
- Índice operacional consolidado em [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)

## Estado do Worktree

### `git status --short --branch` antes
```text
## main...origin/main [ahead 1]
 M backend/app/api/v1/routes/ai_chat.py
 M backend/app/domains/imports/normalization/asset_normalizer.py
 M backend/app/domains/imports/service.py
 M backend/app/main.py
 M frontend/itam-platform/src/components/AppShell.tsx
 M frontend/itam-platform/src/components/StateBlocks.tsx
 M frontend/itam-platform/src/pages/AssetsPage.tsx
 M frontend/itam-platform/src/pages/AuditLogsPage.tsx
 M frontend/itam-platform/src/pages/ImportsPage.tsx
 M frontend/itam-platform/src/pages/SettingsPage.tsx
 M frontend/itam-platform/src/styles.css
 M tests/test_ai_chat_api.py
 M tests/test_ai_chat_hardening.py
 M tests/test_ai_chat_provider_mock.py
?? .env.example
?? .firecrawl/
?? .github/
?? .vscode/
?? _audit_findings/
?? _cleanup_backup_manifest.md
?? _migration_proposals/
?? ai-lab/
?? assets/
?? backend/app/domains/ai_chat/rate_limit.py
?? backend/app/domains/imports/classification/
?? backend/app/domains/imports/normalization/__init__.py
?? backend/app/domains/imports/normalization/lansweeper_normalizer.py
?? backend/app/domains/imports/parsing/
?? docs/AI_CHAT_RATE_LIMIT_REDIS_REPORT.md
?? docs/CRITICAL_FIX_ROUND2_MANIFEST.md
?? docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md
?? docs/CSP_HARDENING_REPORT.md
?? docs/GENERAL_PROJECT_AUDIT_REPORT.md
?? docs/GENERAL_PROJECT_EDITING_ROADMAP.md
?? docs/GENERAL_PROJECT_NEXT_ACTIONS.md
?? docs/GENERAL_PROJECT_RISK_REGISTER.md
?? docs/HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md
?? docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md
?? docs/HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md
?? docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md
?? docs/IMPORT_SERVICE_REFACTOR_MANIFEST.md
?? docs/IMPORT_SERVICE_REFACTOR_PLAN.md
?? docs/IMPORT_SERVICE_REFACTOR_REPORT.md
?? docs/LOCAL_AI_BENCHMARK.md
?? docs/LOCAL_AI_MODEL_STRATEGY.md
?? docs/LOCAL_MODEL_ROUTER_PROPOSAL.md
?? docs/OLLAMA_LOCAL_MODEL_PROFILE.md
?? docs/RELEASE_DOCS_HYGIENE_REPORT.md
?? docs/VISUAL_SMOKE_MANUAL_RUNBOOK.md
?? docs/WORKTREE_TRIAGE_REPORT.md
?? docs/audit/
?? docs/hermesops/HERMES_TOOLS_SKILLS_AUDIT.md
?? docx_sample.md
?? docx_template_output.md
?? frontend/itam-platform/docs/brand/mockups/
?? frontend/itam-platform/docs/brand/reference/
?? frontend/itam-platform/docs/local-crawl/console-errors.json
?? frontend/itam-platform/docs/local-crawl/dom-summary.json
?? frontend/itam-platform/docs/local-crawl/network-errors.json
?? frontend/itam-platform/docs/local-crawl/screenshots-manifest.txt
?? frontend/itam-platform/docs/local-crawl/screenshots/
?? frontend/itam-platform/docs/ui-audit/screenshots/
?? frontend/itam-platform/src/assets/
?? frontend/package-lock.json
?? imports/
?? pptx_sample.md
?? pptx_template_output.md
?? tests/fixtures/imports/
?? tests/test_ai_chat_rate_limit.py
?? tests/test_hermes_icons_security.py
?? tests/test_import_conflict_detector.py
?? tests/test_import_identity_classifier.py
?? tests/test_import_lansweeper_normalizer.py
?? tests/test_import_row_classifier.py
?? tests/test_import_spreadsheet_reader.py
?? tests/test_security_headers.py
?? tools/composio_client.py
```

### `git diff --name-status`
```text
M	backend/app/api/v1/routes/ai_chat.py
M	backend/app/domains/imports/normalization/asset_normalizer.py
M	backend/app/domains/imports/service.py
M	backend/app/main.py
M	frontend/itam-platform/src/components/AppShell.tsx
M	frontend/itam-platform/src/components/StateBlocks.tsx
M	frontend/itam-platform/src/pages/AssetsPage.tsx
M	frontend/itam-platform/src/pages/AuditLogsPage.tsx
M	frontend/itam-platform/src/pages/ImportsPage.tsx
M	frontend/itam-platform/src/pages/SettingsPage.tsx
M	frontend/itam-platform/src/styles.css
M	tests/test_ai_chat_api.py
M	tests/test_ai_chat_hardening.py
M	tests/test_ai_chat_provider_mock.py
```

### `git diff --cached --name-status`
```text
(vazio)
```

### `git ls-files --others --exclude-standard`
- Total bruto de linhas: `786`
- O inventário completo foi classificado por heurística de caminho e resumido abaixo por categoria.

## Tracked Modificados Classificados

| Caminho | Categoria | Risco | Boundary | Motivo | Pode entrar em commit futuro |
|---|---|---:|---|---|---|
| `backend/app/api/v1/routes/ai_chat.py` | Backend real | Médio | `B2` | regra de negócio/backend modular em evolução controlada | Pode entrar em commit se testes do domínio continuarem verdes |
| `backend/app/domains/imports/normalization/asset_normalizer.py` | Backend real | Médio | `B3` | regra de negócio/backend modular em evolução controlada | Pode entrar em commit se testes do domínio continuarem verdes |
| `backend/app/domains/imports/service.py` | Backend real | Médio | `B3` | regra de negócio/backend modular em evolução controlada | Pode entrar em commit se testes do domínio continuarem verdes |
| `backend/app/main.py` | Infra/config | Médio | `B2` | security/middleware/headers do backend | Pode entrar em commit após validação de headers e regressão de rota |
| `frontend/itam-platform/src/components/AppShell.tsx` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `frontend/itam-platform/src/components/StateBlocks.tsx` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `frontend/itam-platform/src/pages/AssetsPage.tsx` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `frontend/itam-platform/src/pages/AuditLogsPage.tsx` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `frontend/itam-platform/src/pages/ImportsPage.tsx` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `frontend/itam-platform/src/pages/SettingsPage.tsx` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `frontend/itam-platform/src/styles.css` | Frontend real | Médio | `B4` | shell/UX real do frontend Vite/React | Pode entrar em commit se build e smoke visual continuarem válidos |
| `tests/test_ai_chat_api.py` | Testes | Baixo | `B2/B3/B4` | cobertura de regressão do comportamento alterado | Pode entrar em commit junto do domínio correspondente |
| `tests/test_ai_chat_hardening.py` | Testes | Baixo | `B2/B3/B4` | cobertura de regressão do comportamento alterado | Pode entrar em commit junto do domínio correspondente |
| `tests/test_ai_chat_provider_mock.py` | Testes | Baixo | `B2/B3/B4` | cobertura de regressão do comportamento alterado | Pode entrar em commit junto do domínio correspondente |

### Resumo tracked
- Backend real: `3`
- Infra/config: `1`
- Frontend real: `7`
- Testes: `3`

## Untracked Classificados

### Sensível/não versionável (`3`)
- `.env.example` | boundary `B0` | risco Alto | template/padrão de ambiente que cai na política de não leitura e não versionamento
- `assets/legacy/Laravel/.env.example` | boundary `B0` | risco Alto | template/padrão de ambiente que cai na política de não leitura e não versionamento
- `tools/composio_client.py` | boundary `B0/B5` | risco Alto | script operacional com API key hardcoded detectada pela triagem

### AI/Hermes/Ollama (`315`)
- `.firecrawl/awesome-hermes.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/github-skill-repos.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/hermes-skill-topic.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/optional-skills-full.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/optional-skills.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/skill-factory.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/skills-catalog.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/skills-dev.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/skills-github.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `.firecrawl/skills-hermes.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/AGENTS.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ENVIRONMENT.hml.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ENVIRONMENT.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/PROJECT_CONTEXT.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ROADMAP.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/SECURITY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_CODE_REVIEW_STANDARD.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_DEBUGGING_STANDARD.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_MEMORY_INTEGRATION.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_MODDING_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_PROMPTING_STANDARD.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_REFACTORING_STANDARD.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_SECURITY_BOUNDARIES.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_STACK_CATALOG.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_TESTING_STRATEGY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_TOOLCHAIN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/CODEROS_WORKFLOW.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/evals/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/examples/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/MODDING_SAFE_BOUNDARIES.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/asset_pipeline.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/config_patch_patterns.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/game_mod_project_structure.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/packaging_release.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/plugin_architecture.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/prohibited_modding_actions.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/troubleshooting_mod_load_order.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/modding/version_compatibility.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/playbooks/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/playbooks/bugfix_workflow.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/playbooks/feature_implementation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/playbooks/refactor_workflow.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/playbooks/repository_triage.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/playbooks/security_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/prompts/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/prompts/code_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/prompts/patch_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/prompts/powershell_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/prompts/security_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/schemas/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/ai_agents.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/docker_compose.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/m365_graph.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/modding_general.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/nextjs.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/node_typescript.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/office_automation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/postgres_sqlalchemy_alembic.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/powershell7.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/python_cli.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/python_data_tools.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/python_fastapi.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/qdrant_rag.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/react_vite.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/redis.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/coderos/stacks/windows_ad_gpo.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/DESKTOP_APP_UI_PLUGIN_PANEL_IMPLEMENTATION_PLAN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/DESKTOP_APP_VISUAL_CHANGE_LIMITS.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/FUTURE_DESKTOP_APP_UI_PLUGIN_PANEL_PLAN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_DISCOVERY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_LOGGING.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_PROJECT_ROUTING.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_ROLLBACK.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_CLI_WRAPPER_PLAN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_MANUAL_ACTIVATION_GUIDE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_MANUAL_ROLLBACK.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_PTBR_KEYBOARD.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/profiles/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/prompts/cli_change_request.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/prompts/cli_debugging.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/prompts/cli_release_checklist.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/prompts/cli_wrapper_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/wrappers/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/docs/HERMES_DESKTOP_WSL.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/ADOBE_ACROBAT_INTEGRATION_PLAN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/ENTERPRISE_OFFICE_SKILLS_ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/HML_DEPLOYMENT_NOTES.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/M365_OFFICE_INTEGRATION_PLAN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/PDF_ADOBE_ACROBAT_SKILL_SPEC.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/POWERPOINT_PPTX_SKILL_SPEC.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/SECURITY_AND_DATA_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/SPREADSHEET_SKILL_SPEC.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/TEXT_EDITING_SKILL_SPEC.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/WORD_DOCX_SKILL_SPEC.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/document_redaction_and_sanitization.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/excel_base_service_desk.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/excel_data_quality_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/pdf_acrobat_standard_workflow.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/pdf_ocr_and_text_extraction.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/pdf_redaction_and_sanitization.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/pdf_signature_and_certificate_caution.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/powerpoint_executive_report_creation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/powerpoint_training_deck_creation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/word_kcs_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/playbooks/word_manual_creation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/corporate_text_rewrite.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/document_quality_audit.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/excel_m365_integration.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/kcs_document_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/pdf_acrobat_workflow.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/pdf_content_extraction.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/pdf_redaction_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/pdf_signature_certificate_handling.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/powerpoint_deck_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/powerpoint_deck_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/powerpoint_training_material.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/spreadsheet_analysis.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/spreadsheet_automation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/spreadsheet_data_quality.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/word_complex_revision.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/prompts/word_document_editing.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/pdf/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/pdf/pdf_audit_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/pdf/pdf_ocr_workflow_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/pdf/pdf_redaction_checklist.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/pdf/pdf_signature_validation_checklist.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/powerpoint/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/powerpoint/executive_deck_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/powerpoint/kcs_training_deck_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/powerpoint/procedure_training_deck_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/powerpoint/service_desk_report_deck_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/spreadsheet/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/word/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/word/corporate_report_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/word/kcs_document_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/word/meeting_minutes_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/enterprise_office_skills/templates/word/procedure_manual_template.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/infra/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/infra/qdrant/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/anydesk/anydesk-unattended-access.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/certificates/certificado-a1-nao-aparece.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/certificates/certificado-a3-token-smartcard.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/alembic-migration-debug.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/docker-compose-debug.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/git-branch-rollback.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/node-npm-dependency-conflict.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/postgresql-redis-debug.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/powershell-script-seguro.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/python-fastapi-debug.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/coding/react-vite-typescript-build.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/gpo-ad/gpo-nao-aplica.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/lansweeper/inventario-lansweeper-divergente.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/ndd-print/ndd-print-pin-portal-360.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/network/dns-incorreto.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/network/maquina-sem-rede.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/network/wake-on-lan.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/office365/office365-ativacao-licenca.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/outlook/outlook-nao-abre.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/printers/impressora-nao-imprime.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/rdp-vpn/rdp-entre-dominios-sem-trust.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/security-incidents/alerta-trend-possivel-malware.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/teams/teams-cache-corrompido.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/windows/bsod-eventos-criticos.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/windows/erro-instalacao-java.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/windows/lentidao-windows.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/windows/perfil-usuario-corrompido.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/wsus-windows-update/windows-update-wsus-travado.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/document-redaction-and-sanitization.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/excel-automation-support.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/excel-base-service-desk.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/excel-data-quality.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/excel-m365-workbook-governance.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/pdf-adobe-acrobat-standard.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/pdf-document-quality-audit.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/pdf-ocr-text-extraction.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/pdf-redaction-sanitization.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/pdf-signature-certificate-handling.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/powerpoint-executive-reporting.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/powerpoint-kcs-training.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/powerpoint-procedure-training.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/word-complex-text-editing.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/word-kcs-generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/word-manual-creation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/enterprise_office_document_skills/word-report-generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_CLI_MESSAGES.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_ENCODING_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_FALLBACK_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_KCS_MACRO_GUIDE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_LOCALIZATION_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_STYLE_GUIDE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/PT_BR_TERMINOLOGY_GUIDE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/code_review_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/coding_assistant_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/desktop_cli_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/kcs_generation_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/m365_excel_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/macro_itil_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/modding_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/office_document_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/pdf_acrobat_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/localization/prompts/service_desk_ptbr.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/MEMORY_ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/MEMORY_CONFLICT_RESOLUTION.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/MEMORY_CONSOLIDATION_RULES.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/MEMORY_LIFECYCLE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/MEMORY_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/MEMORY_RETRIEVAL_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/episodic/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/evals/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/inbox/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/indexes/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/agent_behavior.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/coding_rules.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/hml_promotion_rules.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/office_document_rules.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/security_rules.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/procedural/service_desk_rules.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/rejected/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/semantic/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/semantic/coding/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/semantic/office_skills/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/memory/working/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/PLUGIN_ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/PLUGIN_CHANGE_PROPOSAL_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/PLUGIN_LIFECYCLE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/PLUGIN_LOGGING_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/PLUGIN_REGISTRY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/PLUGIN_SECURITY_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_AUDIT_LOGGING.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_CHANGE_PROPOSAL_WORKFLOW.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_CLI_SPEC.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_HML_ACTIVATION_PLAN.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_LOG_REVIEW_WORKFLOW.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_PERMISSION_MODEL.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_PLUGIN_ARCHITECTURE.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_ROLLBACK.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_RUNTIME_LOGGING.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_SECURITY_POLICY.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_TOOLKIT_ALLOWLIST.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_audit_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_change_proposal.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_connection_triage.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_hml_activation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_log_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_permission_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/prompts/composio_tool_execution_plan.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/code-review/security_review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/codex/implementation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/gemini/review.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/local-model/log_analysis.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/service-desk/first_response_from_seed_corpus.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/service-desk/kcs_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/service-desk/macro_generation.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/service-desk/triage.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/prompts/service-desk/troubleshooting.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/coderos/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/composio_plugin/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/desktop_cli/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/memory/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/office/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/plugins/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/rag/README.md` | boundary `B5` | risco Baixo | propostas e documentação do pacote Hermes selective migration
- `ai-lab/ollama-benchmark/README.md` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/analyze_qwen3_empty_response.py` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/benchmark_local.py` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/check_ollama_context.py` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/healthcheck_20260611T000000Z.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/ollama_context_check_20260611_192736.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/analysis_summary.md` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/health_llama3.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/health_models.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/manifest.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_1_7b_native_chat_think_false.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_1_7b_openai_default.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_1_7b_openai_think_false.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_4b_native_chat_think_false.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_4b_openai_default.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_4b_openai_think_false.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/thinkfalse_recheck.json` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/smoke_test_models.py` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-benchmark/smoke_test_ollama_profile.py` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/Modelfile.llama3.2-3b-hermes-64k` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/Modelfile.qwen2.5-coder-7b-64k` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/Modelfile.qwen2.5-coder-7b-hermes-64k` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/Modelfile.qwen3-1.7b-64k` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/Modelfile.qwen3-4b-64k` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/Modelfile.qwen3-4b-hermes-nothink-64k` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/README.md` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/ollama-modelfiles/create_hermes_ollama_models.sh` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `ai-lab/prompts/apply-hermes-local-ollama-config.prompt.md` | boundary `B5` | risco Médio | catálogo/configuração/dados de tooling Hermes/IA
- `docs/HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/LOCAL_AI_BENCHMARK.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/LOCAL_AI_MODEL_STRATEGY.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/LOCAL_MODEL_ROUTER_PROPOSAL.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama
- `docs/OLLAMA_LOCAL_MODEL_PROFILE.md` | boundary `B5` | risco Baixo | documentação e diagnósticos de Hermes/Ollama

### Script operacional (`2`)
- `.github/workflows/docker-build-push.yml` | boundary `B6` | risco Baixo | workflow de CI/CD
- `.github/workflows/quality-gates.yml` | boundary `B6` | risco Baixo | workflow de CI/CD

### Relatório/documentação útil (`59`)
- `_audit_findings/all_findings.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `_cleanup_backup_manifest.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `assets/legacy/Laravel/README.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `assets/legacy/Laravel/public/robots.txt` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `assets/legacy/Laravel/resources/markdown/policy.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `assets/legacy/Laravel/resources/markdown/terms.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/AI_CHAT_RATE_LIMIT_REDIS_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/CRITICAL_FIX_ROUND2_MANIFEST.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/CSP_HARDENING_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/GENERAL_PROJECT_AUDIT_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/GENERAL_PROJECT_EDITING_ROADMAP.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/GENERAL_PROJECT_NEXT_ACTIONS.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/GENERAL_PROJECT_RISK_REGISTER.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/IMPORT_SERVICE_REFACTOR_MANIFEST.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/IMPORT_SERVICE_REFACTOR_PLAN.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/IMPORT_SERVICE_REFACTOR_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/RELEASE_DOCS_HYGIENE_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/VISUAL_SMOKE_MANUAL_RUNBOOK.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/WORKTREE_TRIAGE_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/ARCHITECTURE_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/AUDIT_ENVIRONMENT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/BACKEND_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/BACKEND_FINDINGS.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/DATABASE_FINDINGS.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/DATABASE_MIGRATIONS_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/DESKTOP_APP_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/DEVOPS_RELEASE_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/FILE_CLASSIFICATION.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/FILE_INVENTORY.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/FRONTEND_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/FRONTEND_FINDINGS.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/FULL_PROJECT_AUDIT_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/GAP_ANALYSIS.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/HIGH_FIX_ROUND3_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/PROJECT_TREE.txt` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/RELEASE_HYGIENE_FINDINGS.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/SCRIPTS_OPS_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/SCRIPTS_OPS_FINDINGS.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/SECURITY_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/SECURITY_FINDINGS.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/TESTING_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/audit/TEST_RESULTS.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docs/hermesops/HERMES_TOOLS_SKILLS_AUDIT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docx_sample.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `docx_template_output.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `imports/HermesOps-Final-Transfer/IMPORT_MANIFEST.txt` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `imports/HermesOps-Final-Transfer/IMPORT_REPORT.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `imports/HermesOps-Final-Transfer/ROLLBACK_INSTRUCTIONS.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `pptx_sample.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `pptx_template_output.md` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/itam_duplicate.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/itam_formula_injection.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/itam_invalid.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/itam_valid.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/lansweeper_duplicate.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/lansweeper_formula_injection.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/lansweeper_invalid.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado
- `tests/fixtures/imports/lansweeper_valid.csv` | boundary `B1` | risco Baixo | documentação, auditoria ou inventário gerado

### Artefato temporário (`44`)
- `frontend/itam-platform/docs/local-crawl/console-errors.json` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/dom-summary.json` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/network-errors.json` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots-manifest.txt` | boundary `B1` | risco Baixo | evidência de crawl/QA visual
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-5173-home-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-ai-chat-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-assets-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-assignments-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-audit-logs-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-home-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-home-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-home-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-imports-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-login-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-macros-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-settings-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-signatures-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-stock-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/local-crawl/screenshots/20260609-local-users-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-ai-chat-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-ai-chat-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-ai-chat-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-assets-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-assets-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-assets-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-audit-logs-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-audit-logs-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-audit-logs-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-home-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-home-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-home-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-imports-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-imports-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-imports-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-login-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-login-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-login-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-macros-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-macros-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-macros-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-settings-1366x768-zoom125.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-settings-1366x768.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/itam-platform/docs/ui-audit/screenshots/20260609-settings-1920x1080.png` | boundary `B1` | risco Baixo | evidência local de navegação e screenshot
- `frontend/package-lock.json` | boundary `B6` | risco Baixo | lockfile gerado pelo gerenciador de pacotes

### Teste novo (`11`)
- `tests/fixtures/imports/itam_valid.xlsx` | boundary `B3/B6` | risco Baixo | fixtures de regressão dos testes
- `tests/fixtures/imports/lansweeper_corrected_shape.xlsx` | boundary `B3/B6` | risco Baixo | fixtures de regressão dos testes
- `tests/fixtures/imports/lansweeper_real_shape.xlsx` | boundary `B3/B6` | risco Baixo | fixtures de regressão dos testes
- `tests/test_ai_chat_rate_limit.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_hermes_icons_security.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_import_conflict_detector.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_import_identity_classifier.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_import_lansweeper_normalizer.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_import_row_classifier.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_import_spreadsheet_reader.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo
- `tests/test_security_headers.py` | boundary `B2/B3/B4` | risco Baixo | teste de regressão novo

### Código real novo (`56`)
- `assets/static/ASSINATURAS DE E-MAIL (ENS_LOGO_AZUL_LGPD_semTWITTER)_v21.23.docx` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/.gitkeep` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/Favicon.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/Header.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/Logo.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/facebook.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/instagram.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/linkedin.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/tiktok.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/icons/youtube.png` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/js/signature-copy.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/v4/hero-outlook.css` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/v4/hero-outlook.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/css/bootstrap-icons.css` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/css/bootstrap.min.css` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/css/templatemo-topic-listing.css` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/fonts/bootstrap-icons.woff` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/fonts/bootstrap-icons.woff2` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/js/bootstrap.bundle.min.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/js/click-scroll.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/js/custom.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/js/jquery.min.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/static/vendor/tpl/js/jquery.sticky.js` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/admin.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/admin_edit.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/base.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/change_password.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/hero_outlook.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/index.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/login.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `assets/templates/oauth_not_configured.html` | boundary `B4/B6` | risco Baixo | assets/templates runtime/static versionáveis
- `backend/app/domains/ai_chat/rate_limit.py` | boundary `B2` | risco Médio | hardening/backend de AI Chat e middleware de segurança
- `backend/app/domains/imports/classification/__init__.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/classification/conflict_detector.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/classification/identity_classifier.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/classification/row_classifier.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/normalization/__init__.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/normalization/lansweeper_normalizer.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/parsing/__init__.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `backend/app/domains/imports/parsing/spreadsheet_reader.py` | boundary `B3` | risco Médio | pipeline de importação/staging/refatoração controlada
- `frontend/itam-platform/src/assets/icons/hermesops/icon-manifest.json` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/agent-orbit.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/audit-report.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/book-circuit.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/conflict-split.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/database-pulse.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/document-bolt.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/eye-trace.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/hermes-core.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/neural-node.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/package-chip.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/radar-circuit.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/settings-circuit.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/shield-check.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis
- `frontend/itam-platform/src/assets/icons/hermesops/svg/transfer-circuit.svg` | boundary `B4` | risco Baixo | assets de frontend versionáveis

### Incerto/requer revisão humana (`296`)
- `.vscode/settings.json` | boundary `hold` | risco Baixo | config local de editor
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/code_context_builder.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/code_review_checker.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/coderos_audit.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/coderos_eval.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/coding_memory_capture.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/dependency_risk_scanner.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/docx_export_sample.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/docx_structure_reader.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/docx_template_builder.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/docx_text_reviewer.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/excel_fidelity_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/m365_workbook_operation_plan.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_audit.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_capture.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_classify.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_conflict_check.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_consolidate.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_eval.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_index.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_query.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_retention.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/memory_sanitize.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/modding_project_analyzer.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/native_format_policy.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/office_format_router.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/office_job_router.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/office_safety_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/patch_plan_builder.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pdf_acrobat_workflow_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pdf_metadata_inspector.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pdf_safety_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pdf_text_extraction_skeleton.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/powershell_static_checker.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pptx_deck_reviewer.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pptx_export_sample.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pptx_structure_reader.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/pptx_template_builder.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/ptbr_encoding_check.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/ptbr_glossary_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/ptbr_localization_audit.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/ptbr_message_catalog_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/ptbr_prompt_audit.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/ptbr_text_lint.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/repo_mapper.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/spreadsheet_data_quality.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/spreadsheet_export_sample.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/spreadsheet_offline_analyzer.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/spreadsheet_schema_validator.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/stack_detector.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/python/validation_runner.py` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/code_review.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/coding_memory.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/coding_task.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/document_review.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/docx_job.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/memory_decision_schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/memory_event_schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/memory_item_schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/memory_policy_schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/memory_research_schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/modding_project.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/office_audit.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/patch_plan.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/pdf_audit.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/pdf_job.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin_audit_event.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin_change_proposal.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin_command.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin_connection.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin_permission.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/plugin_runtime_log.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/pptx_job.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/presentation_review.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/repo_profile.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/spreadsheet_job.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/spreadsheet_validation.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/text_editing_job.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/toolchain_profile.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `_migration_proposals/hermesops_selective_migration/tools/hermesops_offline/schemas/validation_result.schema.json` | boundary `hold` | risco Médio | não classificado por heurística
- `assets/legacy/Laravel/.editorconfig` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/.gitattributes` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Actions/Fortify/CreateNewUser.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Actions/Fortify/PasswordValidationRules.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Actions/Fortify/ResetUserPassword.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Actions/Fortify/UpdateUserPassword.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Actions/Fortify/UpdateUserProfileInformation.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Actions/Jetstream/DeleteUser.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Console/Kernel.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Exceptions/Handler.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Controllers/Controller.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Controllers/DashboardController.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Controllers/DataFeedController.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Kernel.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/Authenticate.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/EncryptCookies.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/PreventRequestsDuringMaintenance.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/RedirectIfAuthenticated.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/TrimStrings.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/TrustHosts.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/TrustProxies.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/ValidateSignature.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Http/Middleware/VerifyCsrfToken.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Models/DataFeed.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Models/User.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/AppServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/AuthServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/BroadcastServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/EventServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/FortifyServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/JetstreamServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/Providers/RouteServiceProvider.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/View/Components/AppLayout.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/View/Components/AuthenticationLayout.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/View/Components/EmptyLayout.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/app/View/Components/GuestLayout.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/artisan` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/bootstrap/app.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/bootstrap/cache/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/composer.json` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/composer.lock` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/app.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/auth.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/broadcasting.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/cache.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/cors.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/database.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/filesystems.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/fortify.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/hashing.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/jetstream.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/livewire.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/logging.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/mail.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/queue.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/sanctum.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/services.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/session.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/config/view.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/factories/UserFactory.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/migrations/2014_10_12_000000_create_users_table.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/migrations/2014_10_12_200000_add_two_factor_columns_to_users_table.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/migrations/2019_08_19_000000_create_failed_jobs_table.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/migrations/2022_03_23_163443_create_sessions_table.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/migrations/2022_05_11_154250_create_datafeeds_table.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/seeders/DashboardTableSeeder.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/database/seeders/DatabaseSeeder.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/lang/en/auth.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/lang/en/pagination.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/lang/en/passwords.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/lang/en/validation.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/package.json` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/phpunit.xml` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/pnpm-lock.yaml` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/postcss.config.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/.htaccess` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/favicon.ico` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/404-illustration-dark.svg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/404-illustration.svg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/auth-image.jpg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/icon-01.svg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/icon-02.svg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/icon-03.svg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/user-36-05.jpg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/user-36-06.jpg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/user-36-07.jpg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/user-36-08.jpg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/user-36-09.jpg` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/images/user-avatar-32.png` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/public/index.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/css/additional-styles/flatpickr.css` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/css/additional-styles/utility-patterns.css` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/css/app.css` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/app.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/bootstrap.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-01.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-02.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-03.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-04.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-05.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-06.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-08.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-09.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/components/dashboard-card-11.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/js/utils.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/api/api-token-manager.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/api/index.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/confirm-password.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/forgot-password.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/login.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/register.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/reset-password.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/two-factor-challenge.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/auth/verify-email.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/action-message.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/action-section.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/app/header.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/app/sidebar.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/button.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/confirmation-modal.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/confirms-password.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/danger-button.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-01.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-02.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-03.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-04.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-05.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-06.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-07.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-08.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-09.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-10.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-11.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-12.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dashboard/dashboard-card-13.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/date-select.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/datepicker.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dialog-modal.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dropdown-filter.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dropdown-help.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dropdown-link.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dropdown-notifications.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dropdown-profile.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/dropdown.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/form-section.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/input-error.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/input.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/label.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/modal-search.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/modal.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/nav-link.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/pagination-classic.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/pagination-numeric.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/responsive-nav-link.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/search-form.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/secondary-button.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/section-border.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/section-title.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/switchable-team.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/theme-toggle.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/components/validation-errors.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/layouts/app.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/layouts/authentication.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/layouts/guest.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/pages/dashboard/dashboard.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/pages/utility/404.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/policy.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/profile/delete-user-form.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/profile/logout-other-browser-sessions-form.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/profile/show.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/profile/two-factor-authentication-form.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/profile/update-password-form.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/profile/update-profile-information-form.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/terms.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/vendor/pagination/simple-tailwind.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/resources/views/vendor/pagination/tailwind.blade.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/routes/api.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/routes/channels.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/routes/console.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/routes/web.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/app/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/app/public/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/framework/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/framework/cache/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/framework/cache/data/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/framework/sessions/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/framework/testing/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/storage/framework/views/.gitignore` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/CreatesApplication.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/ApiTokenPermissionsTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/AuthenticationTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/BrowserSessionsTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/CreateApiTokenTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/DeleteAccountTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/DeleteApiTokenTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/EmailVerificationTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/ExampleTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/PasswordConfirmationTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/PasswordResetTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/ProfileInformationTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/RegistrationTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/TwoFactorAuthenticationSettingsTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Feature/UpdatePasswordTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/TestCase.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/tests/Unit/ExampleTest.php` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/Laravel/vite.config.js` | boundary `hold` | risco Médio | tree legado importado e muito amplo
- `assets/legacy/ens-hero-client.css` | boundary `hold` | risco Médio | artefatos legados mistos
- `assets/legacy/hero.js` | boundary `hold` | risco Médio | artefatos legados mistos
- `assets/legacy/hero.js.map` | boundary `hold` | risco Médio | artefatos legados mistos
- `frontend/itam-platform/docs/brand/mockups/command-center-mockup.png` | boundary `hold` | risco Médio | não classificado por heurística
- `frontend/itam-platform/docs/brand/reference/guardian.png` | boundary `hold` | risco Médio | não classificado por heurística
- `frontend/itam-platform/docs/brand/reference/guardiao-original.png` | boundary `hold` | risco Médio | não classificado por heurística
- `frontend/itam-platform/docs/brand/reference/sentinel-logo-reference.png` | boundary `hold` | risco Médio | não classificado por heurística

### Resumo untracked
- AI/Hermes/Ollama: `315`
- Artefato temporário: `44`
- Código real novo: `56`
- Incerto/requer revisão humana: `296`
- Relatório/documentação útil: `59`
- Script operacional: `2`
- Sensível/não versionável: `3`
- Teste novo: `11`

## Possíveis Secrets Redigidos

- Varredura executada apenas em arquivos untracked não sensíveis/ignorados, sem `.env`, `.env.*`, bancos, dumps, `.git`, `.venv` e `node_modules`.
- Achados totais do scanner seguro: `11`
- Interpretação: `1` hit de alta confiança (`tools/composio_client.py`) e os demais são falso-positivo ou placeholder documentado.

| Caminho | Linha aprox. | Tipo | Contexto redigido | Ação recomendada |
|---|---:|---|---|---|
| `.firecrawl/hermes-skill-topic.json` | `1` | `sk-` | `sk-management` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `.github/workflows/docker-build-push.yml` | `24` | `password` | `password: [REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/anydesk/anydesk-unattended-access.md` | `2` | `sk-` | `sk-unattended` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `assets/legacy/Laravel/app/Actions/Fortify/PasswordValidationRules.php` | `16` | `password` | `Password:[REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `assets/legacy/Laravel/tests/Feature/ApiTokenPermissionsTest.php` | `25` | `token` | `token = [REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `assets/legacy/Laravel/tests/Feature/DeleteApiTokenTest.php` | `25` | `token` | `token = [REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `assets/legacy/hero.js` | `165` | `token` | `token:[REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `assets/static/vendor/tpl/css/bootstrap.min.css` | `6` | `sk-` | `sk-position` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `assets/static/vendor/tpl/js/jquery.min.js` | `2` | `password` | `password:[REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md` | `126` | `api_key` | `api_key: [REDACTED]` | Verificar e manter redigido; provável falso positivo ou placeholder |
| `tools/composio_client.py` | `17` | `api_key` | `API_KEY = [REDACTED]` | Remover/rotacionar a chave e tratar como não versionável |

## Arquivos que Não Devem Ser Versionados Agora

- `.env.example`
- `tools/composio_client.py`
- `frontend/itam-platform/docs/local-crawl/`
- `frontend/itam-platform/docs/ui-audit/`
- `assets/legacy/Laravel/`

## Arquivos que Exigem Revisão Humana

- `.vscode/settings.json`
- `tools/composio_client.py`
- `assets/legacy/Laravel/`
- `frontend/package-lock.json`

## Boundaries de Commit Recomendadas

| Boundary | Objetivo | Arquivos candidatos | Riscos | Pré-validações | Critérios de aceite | O que não misturar |
|---|---|---|---|---|---|---|
| `B0` Segurança/higiene | remover/isolamento de segredos e arquivos não versionáveis | `.env.example`, `tools/composio_client.py`, ignorações | vazamento de segredo e ruído de release | scanner redigido, revisão humana | nenhum valor sensível versionado | código funcional, UI, imports |
| `B1` Documentação de auditoria | relatórios e inventários | `docs/audit/`, `docs/GENERAL_*`, `docs/WORKTREE_TRIAGE_REPORT.md` | volume alto de docs | revisão de links e referências | docs publicáveis e sem segredo | runtime backend/frontend |
| `B2` AI Chat/backend hardening | rate limit, CSP, headers e testes associados | `backend/app/domains/ai_chat/`, `backend/app/main.py`, `tests/test_ai_chat_*`, `tests/test_security_headers.py` | regressão de segurança/headers | `ruff`, `pytest`, `alembic heads`, build local quando possível | 429/503, headers e smoke mantidos | import pipeline, UX ampla |
| `B3` Import pipeline/staging | parsing, normalização, classificação e tests | `backend/app/domains/imports/`, `tests/test_import_*`, `tests/fixtures/imports/` | quebra de contratos de import | `pytest`, fixtures, `ruff`, `compileall` | preview/staging/report/apply parcial preservados | frontend shell, docs gerais |
| `B4` Frontend shell/UX | shell React/Vite e páginas | `frontend/itam-platform/src/`, `frontend/itam-platform/src/assets/icons/hermesops/` | regressão visual/build | `npm run build`, smoke visual | navegação e build passam | backend, docs audit, scripts |
| `B5` Hermes/Ollama docs/scripts | material de IA/Hermes e base de conhecimento | `.firecrawl/`, `ai-lab/`, `docs/HERMES_*`, `docs/OLLAMA_*`, `_migration_proposals/hermesops_selective_migration/` | confusão entre docs e runtime | revisão de sensibilidade | só documentação/knowledge base, sem segredos | backend runtime, frontend runtime |
| `B6` Testes/infra | workflows, lockfiles, fixtures e automação | `.github/workflows/`, `frontend/package-lock.json`, `tests/fixtures/`, `tests/` | lockfile/workflow gerados | execução de pipeline e revisão | CI e testes reproduzíveis | segredos, runtime produtivo |

## Validações Executadas e Resultados

- `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` -> `PASS`
- `timeout 120 .venv/bin/python -m ruff check backend tests scripts` -> `PASS`
- `cd backend && timeout 60 ../.venv/bin/python -m alembic heads` -> `PASS` (`0006_ai_chat`)
- `PYTHONPATH=backend timeout 300 .venv/bin/python -m pytest tests -q -o addopts=` -> `FAIL` antes de executar testes; `pytest` abortou com `FileNotFoundError` na limpeza de captura
- `cd frontend/itam-platform && timeout 180 npm run build` -> `FAIL`; wrapper Windows/UNC no WSL e `tsc` não reconhecido

## Riscos Remanescentes

- `tools/composio_client.py` contém API key hardcoded e deve ser tratado como sensível até remover o valor.
- `assets/legacy/Laravel/` é um tree legado muito amplo e não deve entrar em commit misturado com work funcional atual.
- `pytest` neste ambiente falhou antes de rodar testes por um problema de captura/ambiente, então a validação de regressão Python não ficou completa.
- O build do frontend continua bloqueado pelo problema WSL/Windows UNC/`tsc` ausente no caminho de execução do `npm`.

## Primeira Área Segura para Começar a Editar

- `docs/` para consolidar triagem, relatórios e boundaries sem tocar em runtime.
- Se a próxima rodada for funcional, `backend/app/domains/imports/` é o próximo domínio mais isolável, mas somente com commit separado.

## O que Não Fazer Agora

- Não misturar `B0` com runtime de frontend/backend.
- Não tocar em `.env.example` nem em `tools/composio_client.py` sem resolver a sensibilidade.
- Não abrir `assets/legacy/Laravel/` em um commit funcional do Painel sem revisão humana e boundary próprio.
- Não executar ações destrutivas ou `git add` amplo para tentar “limpar” o estado.

## Prompt Recomendado para a Próxima Rodada

> Executar uma rodada focada apenas em `B0`/`B1`, removendo ou redigindo a chave hardcoded de `tools/composio_client.py`, consolidando relatórios de auditoria em `docs/`, sem tocar em runtime de backend/frontend nem em `assets/legacy/Laravel/`.

## Comandos Executados

- `git status --short --branch`
- `git diff --name-status`
- `git diff --cached --name-status`
- `git ls-files --others --exclude-standard`
- scanner seguro via `.venv/bin/python` para padrões de secret em arquivos untracked não excluídos
- `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `timeout 120 .venv/bin/python -m ruff check backend tests scripts`
- `PYTHONPATH=backend timeout 300 .venv/bin/python -m pytest tests -q -o addopts=`
- `cd backend && timeout 60 ../.venv/bin/python -m alembic heads`
- `cd frontend/itam-platform && timeout 180 npm run build`
