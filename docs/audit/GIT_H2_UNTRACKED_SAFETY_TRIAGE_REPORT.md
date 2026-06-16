# GIT-H2 — Untracked Safety Triage

Boundary: `GIT-H2 — untracked safety triage`
Data: 2026-06-16
Modo: triagem conservadora de untracked, sem stage, sem commit, sem push e sem correção funcional.

## Resumo executivo

- Status: `PARTIAL`.
- Total de untracked inventariados: `720`.
- Stage inicial: vazio.
- Stage final esperado: vazio; validar na FASE 8.
- Nenhum código funcional foi alterado.
- Nenhum conteúdo de `123`, `123.pub`, `imports/`, `.env*`, credenciais, dumps, bancos ou DOCX/binários grandes foi aberto ou impresso.
- O inventário CSV foi gerado por metadados em `docs/audit/GIT_H2_UNTRACKED_INVENTORY.csv`.
- `PARTIAL` porque a árvore contém volume alto e grupos que exigem aprovação humana: `_migration_proposals/`, `assets/legacy/`, `imports/`, `123`, `123.pub`, screenshots antigas, `ai-lab/`, workflow CI e package-lock.

Observação de segurança: a busca de referências da FASE 4 retornou muito conteúdo de assets legados minificados por causa do padrão solicitado incluir `assets`; isso não incluiu leitura de `123`, `123.pub`, `imports/` ou segredos conhecidos, mas reforça que `assets/legacy/` deve ser tratado como boundary própria e não deve ser vasculhado amplamente sem filtros mais restritos.

## Estado Git

- Branch: `main`.
- Ahead/behind: `main...origin/main [ahead 15]` no início da boundary.
- Stage: vazio no início.
- Tracked diff inicial: `docs/audit/README.md` e `docs/audit/NEXT_BOUNDARY_DECISION.md` já estavam modificados pela boundary anterior H1; são arquivos permitidos também em GIT-H2.
- Untracked: `720` caminhos no inventário de `/tmp/git_h2_untracked_paths.txt`.

## Metodologia

- Listagem de paths via `git ls-files --others --exclude-standard`.
- Inventário por metadados: path, top-level, existência, tipo arquivo/diretório, extensão, tamanho e tipo `file` quando seguro.
- Para nomes potencialmente sensíveis, o comando `file` foi pulado e marcado como `SKIPPED_POTENTIAL_SENSITIVE`.
- Sem leitura de segredos.
- Sem hash de arquivos sensíveis.
- Sem stage/commit/push.
- Sem exclusão, movimentação ou renomeação.
- Sem alteração de `.gitignore`, `.dockerignore`, package-lock, migrations, Docker/Compose ou código funcional.

## Resumo por categoria

| Categoria inicial | Quantidade | Tamanho somado aproximado bytes |
|---|---:|---:|
| MIGRATION_PROPOSAL_DEFER | 348 | 288239 |
| LEGACY_DEFER_REVIEW | 198 | 4354717 |
| AUDIT_DOC_REVIEW | 98 | 18133579 |
| AI_LAB_LOCAL_REVIEW | 28 | 405207 |
| SENSITIVE_DO_NOT_OPEN | 21 | 30045 |
| DOC_REVIEW | 11 | 55810 |
| IMAGE_REVIEW | 6 | 17608 |
| LOCAL_DATA_DO_NOT_COMMIT | 3 | 3587 |
| CODE_OR_CONFIG_REVIEW | 2 | 3835 |
| CI_WORKFLOW_REVIEW | 1 | 940 |
| AUDIT_FINDINGS_REVIEW | 1 | 58763 |
| BINARY_REVIEW | 1 | 11700117 |
| UNKNOWN_REVIEW | 1 | 1 |
| PACKAGE_LOCK_DEFER | 1 | 87 |

## Resumo por top-level

| Top-level | Quantidade |
|---|---:|
| _migration_proposals | 349 |
| assets | 224 |
| docs | 104 |
| ai-lab | 28 |
| imports | 3 |
| tests | 2 |
| .github | 1 |
| 123 | 1 |
| 123.pub | 1 |
| _audit_findings | 1 |
| _cleanup_backup_manifest.md | 1 |
| docx_sample.md | 1 |
| docx_template_output.md | 1 |
| frontend | 1 |
| pptx_sample.md | 1 |
| pptx_template_output.md | 1 |

## Itens sensíveis ou potencialmente sensíveis

Ação padrão: `DO_NOT_TOUCH`, não abrir, não imprimir, não commitar, não hashear, exigir `SEC-H2` com revisão humana local.

| Path/grupo | Motivo | Ação recomendada | Boundary necessária |
|---|---|---|---|
| `123` | nome compatível com artefato/chave; conteúdo não aberto | revisão humana local; não commitar | `SEC-H2` |
| `123.pub` | nome compatível com chave pública; conteúdo não aberto | revisão humana local; não commitar sem decisão | `SEC-H2` |
| `_migration_proposals/**/SECURITY*`, `*secret*`, `*token*`, `*credential*` | nomes sensíveis dentro de propostas; conteúdo não inspecionado linha a linha | tratar como revisão humana | `SEC-H2` ou `DOCS-H2` |
| screenshots com `imports` no path | podem conter dados de UI/importação | não abrir/imprimir; decidir se evidência pode ficar | `DOCS-H2`/`SEC-H2` |

Itens classificados automaticamente como `SENSITIVE_DO_NOT_OPEN` no CSV: 21.

## Local data / imports

Ação padrão: `LOCAL_DATA_DO_NOT_COMMIT`, não abrir conteúdo e não commitar.

Paths/grupo:
- `imports/HermesOps-Final-Transfer/IMPORT_MANIFEST.txt`
- `imports/HermesOps-Final-Transfer/IMPORT_REPORT.md`
- `imports/HermesOps-Final-Transfer/ROLLBACK_INSTRUCTIONS.md`

Risco: dados brutos de importação, planilhas/CSV operacionais ou evidências reais podem conter informações patrimoniais ou pessoais.

Ação recomendada: manter fora do Git até revisão humana; se forem fixtures, recriar versões anonimizadas em boundary de testes/imports.

## Docs/audit candidatos

Ação padrão: documentação pode ser commit candidate somente após `DOCS-H2`, com revisão de duplicidade, status e sensibilidade.

Grupos relevantes:
- `docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md`
- `docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md`
- `docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md`
- `docs/audit/ARCHITECTURE_AUDIT.md`
- `docs/audit/AUDIT_ENVIRONMENT.md`
- `docs/audit/B4B2_VISUAL_SMOKE_MANUAL_CHECKLIST.md`
- `docs/audit/BACKEND_AUDIT.md`
- `docs/audit/BACKEND_FINDINGS.csv`
- `docs/audit/DATABASE_FINDINGS.csv`
- `docs/audit/DATABASE_MIGRATIONS_AUDIT.md`
- `docs/audit/DESKTOP_APP_AUDIT.md`
- `docs/audit/DEVOPS_RELEASE_AUDIT.md`
- `docs/audit/FILE_CLASSIFICATION.csv`
- `docs/audit/FILE_INVENTORY.md`
- `docs/audit/FRONTEND_AUDIT.md`
- `docs/audit/FRONTEND_FINDINGS.csv`
- `docs/audit/FULL_PROJECT_AUDIT_REPORT.md`
- `docs/audit/GAP_ANALYSIS.md`
- `docs/audit/HERMES_DO_NOT_TOUCH_MAP_H1.md`
- `docs/audit/HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md`
- `docs/audit/HERMES_IMPROVEMENT_BACKLOG_H1.md`
- `docs/audit/HERMES_NEXT_BOUNDARIES_H1.md`
- `docs/audit/HERMES_RISK_REGISTER_H1.md`
- `docs/audit/HIGH_FIX_ROUND3_REPORT.md`
- `docs/audit/POST_COMMIT_VALIDATION_QA_C1_REPORT.md`
- `docs/audit/PROJECT_TREE.txt`
- `docs/audit/RELEASE_HYGIENE_FINDINGS.csv`
- `docs/audit/RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md`
- `docs/audit/SCRIPTS_OPS_AUDIT.md`
- `docs/audit/SCRIPTS_OPS_FINDINGS.csv`
- `docs/audit/SECURITY_AUDIT.md`
- `docs/audit/SECURITY_FINDINGS.csv`
- `docs/audit/TESTING_AUDIT.md`
- `docs/audit/TEST_RESULTS.md`
- `docs/audit/WORKTREE_BOUNDARY_COMMIT_PLAN_GIT_C1.md`
- `docs/audit/screenshots/b4c/after/admin-desktop.png`
- `docs/audit/screenshots/b4c/after/admin-mobile.png`
- `docs/audit/screenshots/b4c/after/ai-chat-desktop.png`
- `docs/audit/screenshots/b4c/after/ai-chat-mobile.png`
- `docs/audit/screenshots/b4c/after/assinaturas-desktop.png`
- `docs/audit/screenshots/b4c/after/assinaturas-mobile.png`
- `docs/audit/screenshots/b4c/after/audit-logs-desktop.png`
- `docs/audit/screenshots/b4c/after/audit-logs-mobile.png`
- `docs/audit/screenshots/b4c/after/imports-desktop.png`
- `docs/audit/screenshots/b4c/after/imports-mobile.png`
- `docs/audit/screenshots/b4c/after/login-desktop.png`
- `docs/audit/screenshots/b4c/after/login-mobile.png`
- `docs/audit/screenshots/b4c/after/macros-desktop.png`
- `docs/audit/screenshots/b4c/after/macros-mobile.png`
- `docs/audit/screenshots/b4c/after/manifest.json`
- `docs/audit/screenshots/b4c/after/root-desktop.png`
- `docs/audit/screenshots/b4c/after/root-mobile.png`
- `docs/audit/screenshots/b4c/after/settings-desktop.png`
- `docs/audit/screenshots/b4c/after/settings-mobile.png`
- `docs/audit/screenshots/b4c/before/login-desktop.png`
- `docs/audit/screenshots/b4c/before/login-mobile.png`
- `docs/audit/screenshots/b4c/before/manifest.json`
- `docs/audit/screenshots/b4c/before/root-redirect-desktop.png`
- `docs/audit/screenshots/b4c/before/root-redirect-mobile.png`
- `docs/audit/screenshots/b4d/after-polish/desktop/ai-chat.png`
- `docs/audit/screenshots/b4d/after-polish/desktop/imports.png`
- `docs/audit/screenshots/b4d/after-polish/manifest.json`
- `docs/audit/screenshots/b4d/after-polish/mobile/ai-chat.png`
- `docs/audit/screenshots/b4d/after-polish/mobile/imports.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/admin.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/ai-chat.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/assinaturas.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/audit-logs.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/imports.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/macros.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/root.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/settings.png`
- `docs/audit/screenshots/b4d/authenticated/manifest.json`
- `docs/audit/screenshots/b4d/authenticated/mobile/admin.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/ai-chat.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/assinaturas.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/audit-logs.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/imports.png`
- `... mais 24 itens no CSV`

Recomendação: separar docs H1/H2 atuais de relatórios antigos e screenshots. Não deletar histórico nesta boundary.

## CI/CD candidatos

- `.github/workflows/docker-build-push.yml`

Risco: workflow de Docker build/push pode usar secrets, publicar imagens ou acionar release indevido.

Decisão: `COMMIT_CANDIDATE_CI` somente com `CI-H2 — GitHub Actions docker build/push review`, sem publish real e sem configurar secrets durante auditoria.

## Legacy/assets candidatos

Grupos relevantes:
- `assets/legacy/Laravel/.editorconfig`
- `assets/legacy/Laravel/.gitattributes`
- `assets/legacy/Laravel/.gitignore`
- `assets/legacy/Laravel/README.md`
- `assets/legacy/Laravel/app/Actions/Fortify/CreateNewUser.php`
- `assets/legacy/Laravel/app/Actions/Fortify/UpdateUserProfileInformation.php`
- `assets/legacy/Laravel/app/Actions/Jetstream/DeleteUser.php`
- `assets/legacy/Laravel/app/Console/Kernel.php`
- `assets/legacy/Laravel/app/Exceptions/Handler.php`
- `assets/legacy/Laravel/app/Http/Controllers/Controller.php`
- `assets/legacy/Laravel/app/Http/Controllers/DashboardController.php`
- `assets/legacy/Laravel/app/Http/Controllers/DataFeedController.php`
- `assets/legacy/Laravel/app/Http/Kernel.php`
- `assets/legacy/Laravel/app/Http/Middleware/Authenticate.php`
- `assets/legacy/Laravel/app/Http/Middleware/EncryptCookies.php`
- `assets/legacy/Laravel/app/Http/Middleware/PreventRequestsDuringMaintenance.php`
- `assets/legacy/Laravel/app/Http/Middleware/RedirectIfAuthenticated.php`
- `assets/legacy/Laravel/app/Http/Middleware/TrimStrings.php`
- `assets/legacy/Laravel/app/Http/Middleware/TrustHosts.php`
- `assets/legacy/Laravel/app/Http/Middleware/TrustProxies.php`
- `assets/legacy/Laravel/app/Http/Middleware/ValidateSignature.php`
- `assets/legacy/Laravel/app/Models/DataFeed.php`
- `assets/legacy/Laravel/app/Models/User.php`
- `assets/legacy/Laravel/app/Providers/AppServiceProvider.php`
- `assets/legacy/Laravel/app/Providers/AuthServiceProvider.php`
- `assets/legacy/Laravel/app/Providers/BroadcastServiceProvider.php`
- `assets/legacy/Laravel/app/Providers/EventServiceProvider.php`
- `assets/legacy/Laravel/app/Providers/FortifyServiceProvider.php`
- `assets/legacy/Laravel/app/Providers/JetstreamServiceProvider.php`
- `assets/legacy/Laravel/app/Providers/RouteServiceProvider.php`
- `assets/legacy/Laravel/app/View/Components/AppLayout.php`
- `assets/legacy/Laravel/app/View/Components/AuthenticationLayout.php`
- `assets/legacy/Laravel/app/View/Components/EmptyLayout.php`
- `assets/legacy/Laravel/app/View/Components/GuestLayout.php`
- `assets/legacy/Laravel/artisan`
- `assets/legacy/Laravel/bootstrap/app.php`
- `assets/legacy/Laravel/bootstrap/cache/.gitignore`
- `assets/legacy/Laravel/composer.json`
- `assets/legacy/Laravel/composer.lock`
- `assets/legacy/Laravel/config/app.php`
- `assets/legacy/Laravel/config/auth.php`
- `assets/legacy/Laravel/config/broadcasting.php`
- `assets/legacy/Laravel/config/cache.php`
- `assets/legacy/Laravel/config/cors.php`
- `assets/legacy/Laravel/config/database.php`
- `assets/legacy/Laravel/config/filesystems.php`
- `assets/legacy/Laravel/config/fortify.php`
- `assets/legacy/Laravel/config/hashing.php`
- `assets/legacy/Laravel/config/jetstream.php`
- `assets/legacy/Laravel/config/livewire.php`
- `assets/legacy/Laravel/config/logging.php`
- `assets/legacy/Laravel/config/mail.php`
- `assets/legacy/Laravel/config/queue.php`
- `assets/legacy/Laravel/config/sanctum.php`
- `assets/legacy/Laravel/config/services.php`
- `assets/legacy/Laravel/config/session.php`
- `assets/legacy/Laravel/config/view.php`
- `assets/legacy/Laravel/database/.gitignore`
- `assets/legacy/Laravel/database/factories/UserFactory.php`
- `assets/legacy/Laravel/database/migrations/2014_10_12_000000_create_users_table.php`
- `assets/legacy/Laravel/database/migrations/2014_10_12_200000_add_two_factor_columns_to_users_table.php`
- `assets/legacy/Laravel/database/migrations/2019_08_19_000000_create_failed_jobs_table.php`
- `assets/legacy/Laravel/database/migrations/2022_03_23_163443_create_sessions_table.php`
- `assets/legacy/Laravel/database/migrations/2022_05_11_154250_create_datafeeds_table.php`
- `assets/legacy/Laravel/database/seeders/DashboardTableSeeder.php`
- `assets/legacy/Laravel/database/seeders/DatabaseSeeder.php`
- `assets/legacy/Laravel/lang/en/auth.php`
- `assets/legacy/Laravel/lang/en/pagination.php`
- `assets/legacy/Laravel/lang/en/validation.php`
- `assets/legacy/Laravel/package.json`
- `assets/legacy/Laravel/phpunit.xml`
- `assets/legacy/Laravel/pnpm-lock.yaml`
- `assets/legacy/Laravel/postcss.config.js`
- `assets/legacy/Laravel/public/.htaccess`
- `assets/legacy/Laravel/public/favicon.ico`
- `assets/legacy/Laravel/public/images/404-illustration-dark.svg`
- `assets/legacy/Laravel/public/images/404-illustration.svg`
- `assets/legacy/Laravel/public/images/auth-image.jpg`
- `assets/legacy/Laravel/public/images/icon-01.svg`
- `assets/legacy/Laravel/public/images/icon-02.svg`
- `... mais 126 itens no CSV`

Decisão: `COMMIT_CANDIDATE_LEGACY` apenas para boundary `LEGACY-H2`. `assets/legacy/` contém árvore grande, Laravel/JS/assets e deve ser inventariado por dependência antes de qualquer commit ou delete. O DOCX grande deve ter decisão humana: Git LFS, artifact externo, storage documental ou ignore.

## Package-lock

- `frontend/package-lock.json`

Decisão: `PACKAGE_LOCK_DEFER`.

Motivo: lockfile afeta reprodutibilidade; não alterar nem commitar sem boundary de dependências ou CI que explique qual árvore npm gerou o arquivo.

## Itens para ignore futuro

Candidatos prováveis, sem alterar `.gitignore` nesta boundary:

- `_cleanup_backup_manifest.md`
- `docs/audit/screenshots/b4c/after/admin-desktop.png`
- `docs/audit/screenshots/b4c/after/admin-mobile.png`
- `docs/audit/screenshots/b4c/after/ai-chat-desktop.png`
- `docs/audit/screenshots/b4c/after/ai-chat-mobile.png`
- `docs/audit/screenshots/b4c/after/assinaturas-desktop.png`
- `docs/audit/screenshots/b4c/after/assinaturas-mobile.png`
- `docs/audit/screenshots/b4c/after/audit-logs-desktop.png`
- `docs/audit/screenshots/b4c/after/audit-logs-mobile.png`
- `docs/audit/screenshots/b4c/after/imports-desktop.png`
- `docs/audit/screenshots/b4c/after/imports-mobile.png`
- `docs/audit/screenshots/b4c/after/login-desktop.png`
- `docs/audit/screenshots/b4c/after/login-mobile.png`
- `docs/audit/screenshots/b4c/after/macros-desktop.png`
- `docs/audit/screenshots/b4c/after/macros-mobile.png`
- `docs/audit/screenshots/b4c/after/manifest.json`
- `docs/audit/screenshots/b4c/after/root-desktop.png`
- `docs/audit/screenshots/b4c/after/root-mobile.png`
- `docs/audit/screenshots/b4c/after/settings-desktop.png`
- `docs/audit/screenshots/b4c/after/settings-mobile.png`
- `docs/audit/screenshots/b4c/before/login-desktop.png`
- `docs/audit/screenshots/b4c/before/login-mobile.png`
- `docs/audit/screenshots/b4c/before/manifest.json`
- `docs/audit/screenshots/b4c/before/root-redirect-desktop.png`
- `docs/audit/screenshots/b4c/before/root-redirect-mobile.png`
- `docs/audit/screenshots/b4d/after-polish/desktop/ai-chat.png`
- `docs/audit/screenshots/b4d/after-polish/desktop/imports.png`
- `docs/audit/screenshots/b4d/after-polish/manifest.json`
- `docs/audit/screenshots/b4d/after-polish/mobile/ai-chat.png`
- `docs/audit/screenshots/b4d/after-polish/mobile/imports.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/admin.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/ai-chat.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/assinaturas.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/audit-logs.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/imports.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/macros.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/root.png`
- `docs/audit/screenshots/b4d/authenticated/desktop/settings.png`
- `docs/audit/screenshots/b4d/authenticated/manifest.json`
- `docs/audit/screenshots/b4d/authenticated/mobile/admin.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/ai-chat.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/assinaturas.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/audit-logs.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/imports.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/macros.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/root.png`
- `docs/audit/screenshots/b4d/authenticated/mobile/settings.png`
- `docs/audit/screenshots/b4e/before/desktop/backend-admin-1366x768.json`
- `docs/audit/screenshots/b4e/before/desktop/backend-admin-1366x768.png`
- `docs/audit/screenshots/b4e/before/desktop/backend-assinaturas-1366x768.json`
- `docs/audit/screenshots/b4e/before/desktop/backend-assinaturas-1366x768.png`
- `docs/audit/screenshots/b4e/before/desktop/preview-admin-1366x768.json`
- `docs/audit/screenshots/b4e/before/desktop/preview-admin-1366x768.png`
- `docs/audit/screenshots/b4e/before/desktop/preview-assinaturas-1366x768.json`
- `docs/audit/screenshots/b4e/before/desktop/preview-assinaturas-1366x768.png`
- `docs/audit/screenshots/b4e/before/mobile/backend-admin-390x844.json`
- `docs/audit/screenshots/b4e/before/mobile/backend-admin-390x844.png`
- `docs/audit/screenshots/b4e/before/mobile/backend-assinaturas-390x844.json`
- `docs/audit/screenshots/b4e/before/mobile/backend-assinaturas-390x844.png`
- `docs/audit/screenshots/b4e/before/mobile/preview-admin-390x844.json`
- `docs/audit/screenshots/b4e/before/mobile/preview-admin-390x844.png`
- `docs/audit/screenshots/b4e/before/mobile/preview-assinaturas-390x844.json`
- `docs/audit/screenshots/b4e/before/mobile/preview-assinaturas-390x844.png`
- `docs/audit/screenshots/b5d2-same-origin-ai-chat/01-login.png`
- `docs/audit/screenshots/b5d2-same-origin-ai-chat/02-post-login-home.png`
- `docs/audit/screenshots/b5d2-same-origin-ai-chat/03-ai-chat-initial.png`
- `docs/audit/screenshots/b5d2-same-origin-ai-chat/04-ai-chat-response.png`
- `docx_sample.md`
- `docx_template_output.md`
- `pptx_sample.md`
- `pptx_template_output.md`

Também considerar, após revisão: screenshots antigas, outputs locais, amostras docx/pptx, artefatos temporários e resultados locais de benchmark.

## Itens para delete manual futuro

Somente com aprovação humana; não deletar nesta boundary:

- `_cleanup_backup_manifest.md`
- `docx_sample.md`
- `docx_template_output.md`
- `pptx_sample.md`
- `pptx_template_output.md`

## Do-not-touch

- `123`
- `123.pub`
- `imports/`
- `assets/legacy/`
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`
- `frontend/package-lock.json`
- `.github/workflows/docker-build-push.yml` até `CI-H2`
- `_migration_proposals/` até decisão humana
- `_audit_findings/` até decisão documental
- `ai-lab/` até boundary de AI/local lab
- screenshots antigas com dados de UI/imports
- qualquer arquivo com nome de segredo/chave/token/certificado/dump/db

## Próximas boundaries recomendadas

1. `SEC-H2 — local sensitive artifact triage`.
2. `DOCS-H2 — audit docs consolidation`.
3. `CI-H2 — GitHub Actions docker build/push review`.
4. `LEGACY-H2 — legacy assets and DOCX large artifact decision`.
5. `TEST-H2 — pytest markers and validation standardization`.
6. `IGNORE-H2 — gitignore hygiene for local artifacts`.

## Decisão final

`PARTIAL` para GIT-H2: inventário e matriz criados, stage preservado vazio e nenhum arquivo sensível proibido foi aberto; porém a decisão final de commit/ignore/delete exige revisão humana por grupo, especialmente para arquivos possivelmente sensíveis, dados locais, legado, CI e package-lock.
