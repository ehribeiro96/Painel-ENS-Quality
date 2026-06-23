# P0 Untracked Sanitization Plan — 2026-06-23

## 1. Objetivo
Reduzir risco dos untracked preexistentes sem apagar ou mover arquivos automaticamente.

## 2. Status
PARTIAL-GO

## 3. O que foi feito
- Revisão dos relatórios da triagem
- Classificação dos candidatos P0
- Atualização segura do `.gitignore`
- Validação de cobertura do `.gitignore`

## 4. O que não foi feito
- Nenhum arquivo foi apagado
- Nenhum arquivo foi movido
- Nenhum secret foi impresso
- Nenhum conteúdo sensível foi commitado

## 5. Candidatos P0
| Path | Categoria | Ação recomendada | Coberto por ignore |
|---|---|---|---|
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/AGENTS.md` | DOC_FALSE_POSITIVE | SAFE_FALSE_POSITIVE | não |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/README.md` | DOC_FALSE_POSITIVE | SAFE_FALSE_POSITIVE | não |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/SECURITY.md` | REPORT_WITH_SENSITIVE_TERMS | SAFE_FALSE_POSITIVE | não |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_CLI_SPEC.md` | CONFIG_TEMPLATE_REVIEW | MANUAL_REVIEW_REQUIRED | não |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_PERMISSION_MODEL.md` | DOC_FALSE_POSITIVE | SAFE_FALSE_POSITIVE | não |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/plugins/composio/COMPOSIO_SECURITY_POLICY.md` | REPORT_WITH_SENSITIVE_TERMS | SAFE_FALSE_POSITIVE | não |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/tools/composio_plugin/README.md` | DOC_FALSE_POSITIVE | SAFE_FALSE_POSITIVE | não |
| `assets/legacy/Laravel/.env.example` | CONFIG_TEMPLATE_REVIEW | SANITIZE_BEFORE_TRACKING | não |
| `assets/legacy/Laravel/config/cache.php` | LEGACY_EXAMPLE | MANUAL_REVIEW_REQUIRED | não |
| `assets/legacy/Laravel/config/database.php` | LEGACY_EXAMPLE | MANUAL_REVIEW_REQUIRED | não |
| `assets/legacy/Laravel/config/filesystems.php` | LEGACY_EXAMPLE | MANUAL_REVIEW_REQUIRED | não |
| `assets/legacy/Laravel/config/queue.php` | LEGACY_EXAMPLE | MANUAL_REVIEW_REQUIRED | não |
| `assets/legacy/Laravel/config/services.php` | LEGACY_EXAMPLE | MANUAL_REVIEW_REQUIRED | não |
| `docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md` | REPORT_WITH_SENSITIVE_TERMS | SAFE_FALSE_POSITIVE | não |
| `docs/audit/FILE_CLASSIFICATION.csv` | REPORT_WITH_SENSITIVE_TERMS | SAFE_FALSE_POSITIVE | não |
| `docs/audit/PROJECT_TREE.txt` | REPORT_WITH_SENSITIVE_TERMS | SAFE_FALSE_POSITIVE | não |
| `docs/audit/WORKTREE_BOUNDARY_COMMIT_PLAN_GIT_C1.md` | REPORT_WITH_SENSITIVE_TERMS | SAFE_FALSE_POSITIVE | não |

## 6. Regras adicionadas ao `.gitignore`
- `_cleanup_backup_manifest.md`
- `*_backup_manifest.md`
- `data/exports/`
- `docs/audit/screenshots/`
- `docs/apoema-visual-qa/screenshots/`
- `docs/apoema-visual-qa/*.pid`

## 7. Ações manuais obrigatórias
- Revisar localmente arquivos classificados como `REAL_SECRET_LIKELY` se surgirem em futuras varreduras
- Rotacionar secrets se houver confirmação
- Remover backups locais manualmente após aprovação humana
- Mover exports/reports pesados para storage externo, se necessário

## 8. Fora do escopo
- Limpeza automática
- Remoção de legado
- Sanitização de docs antigos
- Commit de arquivos grandes

## 9. Próxima fase recomendada
Saneamento humano orientado por review dos legacy refs e decisão explícita sobre versionamento de evidências, exports e relatórios locais.
