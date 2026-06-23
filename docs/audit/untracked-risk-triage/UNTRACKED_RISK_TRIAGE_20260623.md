# Untracked Risk Triage — 2026-06-23

## 1. Resumo executivo
- Status: PARTIAL_GO
- Total de untracked: 714
- Tamanho estimado: elevado, com muitos artefatos de docs, legado, caches e evidências locais
- Riscos críticos: candidatos de secret por conteúdo presentes
- Ações recomendadas: revisar manualmente caminhos com token/password/secret/key no nome, manter exports/reports/screenshots fora do Git e reforçar .gitignore

## 2. Escopo
Triagem somente leitura dos untracked preexistentes.
Nenhum arquivo foi apagado.
Nenhum arquivo foi movido.
Nenhum secret foi impresso.

## 3. Top diretórios por tamanho
- 52K	backups
- 72K	.pytest_cache
- 336K	.ruff_cache
- 696K	frontend/itam-platform/dist
- 9.9M	data
- 12M	reports
- 35M	docs
- 37M	_validation
- 110M	exports

## 4. Arquivos grandes
- assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx (12M)
- docs/audit/FILE_CLASSIFICATION.csv (3.6M)
- assets/legacy/hero.js.map (2.6M)
- docs/audit/PROJECT_TREE.txt (2.0M)
- docs/audit/screenshots/b5d2-same-origin-ai-chat/04-ai-chat-response.png (1.7M)
- docs/audit/screenshots/b5d2-same-origin-ai-chat/03-ai-chat-initial.png (1.6M)
- docs/apoema-visual-qa/screenshots/1366x768__chat-response.png (796K)
- docs/apoema-visual-qa/screenshots/1920x1080__assets.png (644K)
- docs/apoema-visual-qa/screenshots/1920x1080__chat-response.png (644K)
- docs/apoema-visual-qa/screenshots/1366x768__assets.png (644K)
- docs/apoema-visual-qa/screenshots/1366x768__chat-sensitive-warning.png (624K)
- assets/legacy/hero.js (588K)
- docs/apoema-visual-qa/screenshots/1366x768__chat.png (580K)
- docs/apoema-visual-qa/screenshots/1366x768__chat-dragover.png (580K)
- docs/apoema-visual-qa/screenshots/1366x768__dashboard.png (556K)
- docs/apoema-visual-qa/screenshots/1920x1080__dashboard.png (540K)
- docs/apoema-visual-qa/screenshots/1920x1080__chat-sensitive-warning.png (524K)
- docs/apoema-visual-qa/screenshots/1920x1080__chat-dragover.png (512K)
- docs/apoema-visual-qa/screenshots/after-polish/1920-chat.png (512K)
- docs/apoema-visual-qa/screenshots/1920x1080__chat.png (512K)
- docs/audit/screenshots/b4d/after-polish/desktop/imports.png (472K)
- docs/audit/screenshots/b4d/authenticated/desktop/imports.png (464K)
- docs/audit/screenshots/b4d/authenticated/desktop/root.png (448K)
- docs/apoema-visual-qa/screenshots/1920x1080__integrations.png (412K)
- docs/apoema-visual-qa/screenshots/1920x1080__settings-auto.png (400K)
- docs/apoema-visual-qa/screenshots/after-polish/1920-settings.png (400K)
- docs/apoema-visual-qa/screenshots/1920x1080__settings-dark.png (400K)
- docs/apoema-visual-qa/screenshots/1920x1080__settings-light.png (400K)
- docs/audit/screenshots/b4d/authenticated/mobile/root.png (400K)
- docs/audit/screenshots/b4d/after-polish/mobile/imports.png (372K)
- docs/audit/screenshots/b4d/authenticated/mobile/imports.png (360K)
- docs/audit/screenshots/b4d/authenticated/desktop/audit-logs.png (348K)
- docs/apoema-visual-qa/screenshots/after-polish/1366-dashboard.png (340K)
- docs/apoema-visual-qa/screenshots/1366x768__integrations.png (324K)
- assets/legacy/Laravel/composer.lock (324K)
- docs/audit/screenshots/b4d/authenticated/desktop/ai-chat.png (320K)
- docs/apoema-visual-qa/screenshots/1366x768__settings-auto.png (316K)
- docs/apoema-visual-qa/screenshots/1366x768__settings-dark.png (312K)
- docs/apoema-visual-qa/screenshots/1366x768__settings-light.png (312K)
- docs/apoema-visual-qa/screenshots/after-polish/1366-settings.png (312K)
- docs/audit/screenshots/b5d2-same-origin-ai-chat/02-post-login-home.png (292K)
- docs/audit/screenshots/b4d/after-polish/desktop/ai-chat.png (292K)
- docs/audit/screenshots/b4d/authenticated/mobile/audit-logs.png (236K)
- docs/audit/screenshots/b4d/authenticated/mobile/ai-chat.png (236K)
- docs/audit/screenshots/b4d/after-polish/mobile/ai-chat.png (236K)
- assets/legacy/Laravel/public/images/auth-image.jpg (228K)
- docs/audit/screenshots/b4c/before/root-redirect-desktop.png (208K)
- docs/audit/screenshots/b4c/before/login-desktop.png (208K)
- docs/audit/screenshots/b4d/authenticated/desktop/settings.png (204K)
- docs/audit/screenshots/b4c/after/settings-desktop.png (196K)
- docs/audit/screenshots/b4c/after/root-desktop.png (196K)
- docs/audit/screenshots/b4c/after/macros-desktop.png (196K)
- docs/audit/screenshots/b4c/after/login-desktop.png (196K)
- docs/audit/screenshots/b4c/after/imports-desktop.png (196K)
- docs/audit/screenshots/b4c/after/audit-logs-desktop.png (196K)
- docs/audit/screenshots/b4c/after/ai-chat-desktop.png (196K)
- docs/audit/screenshots/b5d2-same-origin-ai-chat/01-login.png (192K)
- docs/audit/screenshots/b4d/authenticated/desktop/macros.png (188K)
- docs/audit/screenshots/b4d/authenticated/mobile/macros.png (172K)
- docs/audit/screenshots/b4d/authenticated/mobile/settings.png (164K)
- docs/audit/screenshots/b4c/before/root-redirect-mobile.png (108K)
- docs/audit/screenshots/b4c/before/login-mobile.png (108K)
- docs/audit/screenshots/b4c/after/settings-mobile.png (100K)
- docs/audit/screenshots/b4c/after/root-mobile.png (100K)
- docs/audit/screenshots/b4c/after/macros-mobile.png (100K)
- docs/audit/screenshots/b4c/after/login-mobile.png (100K)
- docs/audit/screenshots/b4c/after/imports-mobile.png (100K)
- docs/audit/screenshots/b4c/after/audit-logs-mobile.png (100K)
- docs/audit/screenshots/b4c/after/ai-chat-mobile.png (100K)
- assets/legacy/Laravel/resources/views/components/app/sidebar.blade.php (72K)
- docs/audit/untracked-risk-triage/untracked-files.txt (60K)
- docs/audit/BACKEND_FINDINGS.csv (48K)
- docs/audit/SCRIPTS_OPS_FINDINGS.csv (44K)
- docs/audit/screenshots/b4e/before/desktop/backend-assinaturas-1366x768.png (44K)
- docs/audit/screenshots/b4d/authenticated/desktop/assinaturas.png (44K)
- docs/audit/WORKTREE_BOUNDARY_COMMIT_PLAN_GIT_C1.md (44K)
- docs/audit/screenshots/b4e/before/mobile/backend-assinaturas-390x844.png (40K)
- docs/audit/screenshots/b4d/authenticated/mobile/assinaturas.png (40K)
- assets/legacy/Laravel/pnpm-lock.yaml (40K)
- docs/audit/screenshots/b4e/before/desktop/backend-admin-1366x768.png (36K)

## 5. Candidatos sensíveis
Listar apenas caminhos.
- _migration_proposals/hermesops_selective_migration/docs/hermesops/desktop_cli/HERMES_DESKTOP_PTBR_KEYBOARD.md
- _migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/certificates/certificado-a3-token-smartcard.md
- assets/legacy/Laravel/.env.example
- assets/legacy/Laravel/app/Actions/Fortify/PasswordValidationRules.php
- assets/legacy/Laravel/app/Actions/Fortify/ResetUserPassword.php
- assets/legacy/Laravel/app/Actions/Fortify/UpdateUserPassword.php
- assets/legacy/Laravel/app/Http/Middleware/VerifyCsrfToken.php
- assets/legacy/Laravel/lang/en/passwords.php
- assets/legacy/Laravel/resources/views/api/api-token-manager.blade.php
- assets/legacy/Laravel/resources/views/auth/confirm-password.blade.php
- assets/legacy/Laravel/resources/views/auth/forgot-password.blade.php
- assets/legacy/Laravel/resources/views/auth/reset-password.blade.php
- assets/legacy/Laravel/resources/views/components/confirms-password.blade.php
- assets/legacy/Laravel/resources/views/profile/update-password-form.blade.php
- assets/legacy/Laravel/tests/Feature/ApiTokenPermissionsTest.php
- assets/legacy/Laravel/tests/Feature/CreateApiTokenTest.php
- assets/legacy/Laravel/tests/Feature/DeleteApiTokenTest.php
- assets/legacy/Laravel/tests/Feature/PasswordConfirmationTest.php
- assets/legacy/Laravel/tests/Feature/PasswordResetTest.php
- assets/legacy/Laravel/tests/Feature/UpdatePasswordTest.php

## 6. Cobertura .gitignore
- Ignorados: 1
- Não ignorados: 35
- Regras recomendadas: .env, .env.*, backups, dumps, exports, reports, screenshots e caches de build/runtime

## 7. Classificação
| Categoria | Quantidade | Exemplos | Ação recomendada |
|---|---:|---|---|
| A_CRITICAL_SECRET_CANDIDATE | 17 | _migration_proposals/hermesops_selective_migration/docs/hermesops/AGENTS.md, _migration_proposals/hermesops_selective_migration/docs/hermesops/README.md, _migration_proposals/hermesops_selective_migration/docs/hermesops/SECURITY.md | Revisão humana imediata; não versionar até confirmar sanitização. |
| B_LOCAL_ENV_OR_BACKUP | 1 | _cleanup_backup_manifest.md | Manter fora do Git; arquivar ou substituir por exemplo redigido. |
| C_RELEASE_ARTIFACT | 0 | - | Não versionar; tratar como artefato de release/runtime. |
| D_VALIDATION_EVIDENCE | 91 | docs/apoema-visual-qa/screenshots/1366x768__assets.png, docs/apoema-visual-qa/screenshots/1366x768__chat-dragover.png, docs/apoema-visual-qa/screenshots/1366x768__chat-response.png | Versionar apenas evidência sanitizada e necessária. |
| E_DOCS_REPORT | 45 | docs/ADMIN_SUPPORT_PERMISSIONS.md, docs/AI_CHAT_IMPLEMENTATION_REPORT.md, docs/AI_CHAT_INTEGRATION_TODO.md | Pode ser versionado se não contiver segredos. |
| F_CACHE_OR_BUILD_OUTPUT | 0 | - | Adicionar ao .gitignore e remover apenas em saneamento futuro. |
| G_LEGACY_REFERENCE | 210 | assets/legacy/Laravel/.editorconfig, assets/legacy/Laravel/.gitattributes, assets/legacy/Laravel/.gitignore | Manter separado do runtime atual; revisar utilidade. |
| H_RUNTIME_DATA_OR_EXPORT | 0 | - | Não versionar; mover para storage externo ou tratar manualmente. |
| I_SAFE_SOURCE_CANDIDATE | 342 | _migration_proposals/hermesops_selective_migration/docs/hermesops/ARCHITECTURE.md, _migration_proposals/hermesops_selective_migration/docs/hermesops/ENVIRONMENT.hml.md, _migration_proposals/hermesops_selective_migration/docs/hermesops/ENVIRONMENT.md | Revisar se é novo código intencional antes de versionar. |
| J_UNKNOWN_REVIEW_REQUIRED | 8 | assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx, assets/static/icons/.gitkeep, assets/static/icons/Logo.png | Revisão manual obrigatória. |

## 8. P0 manual
Itens que exigem ação humana antes de push/release:
- Rotacionar/remover .env.bak_* local
- Verificar arquivos de secret
- Confirmar que exports/dumps não serão versionados

## 9. Recomendações
- Adicionar regras ao .gitignore
- Mover artefatos para storage externo
- Manter docs úteis
- Não commitar runtime data

## 10. Próxima fase
Proposta de prompt para saneamento controlado, se aprovado.
