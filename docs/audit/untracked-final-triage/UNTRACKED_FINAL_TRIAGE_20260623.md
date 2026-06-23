# Triagem Final dos Untracked - 2026-06-23

## 1. Status
GO

## 2. Resumo executivo
- Untracked preexistentes classificados: 622
- Grupos principais: 349 propostas de migracao, 215 arquivos de legado, 50 documentos/auditorias e 8 ativos estaticos.
- Possiveis segredos por nome/conteudo: 7 candidatos por nome, 9 hits de conteudo; nenhum segredo real confirmado.
- Mudanca de escopo: nenhuma exclusao, nenhum reset, nenhum arquivo fora de `docs/audit/untracked-final-triage/` foi alterado por esta triagem.

## 3. Distribuicao por grupo
| Grupo | Qtde | Acao recomendada | Observacao |
|---|---:|---|---|
| `_migration_proposals/hermesops_selective_migration` | 349 | KEEP_UNTRACKED / MANUAL_REVIEW | Propostas de migracao e playbooks de referencia. |
| `assets/legacy` | 215 | KEEP_UNTRACKED | Fonte/legado preservado como referencia historica. |
| `docs/audit` | 29 | KEEP_UNTRACKED | Relatorios de auditoria mantidos fora do commit. |
| `assets/static` | 8 | KEEP_UNTRACKED | Midia/arquivos estaticos nao entram nesta rodada. |
| `docs/apoema-visual-qa` | 4 | KEEP_UNTRACKED | Evidencias de QA visual. |
| `docs/root` | 14 | KEEP_UNTRACKED | Documentos avulsos do projeto. |
| `docs/hermesops` | 1 | KEEP_UNTRACKED | Documentacao HermesOps. |
| `docs/product` | 1 | KEEP_UNTRACKED | Documentacao de produto. |
| `docs/superpowers` | 1 | KEEP_UNTRACKED | Plano utilitario nao alvo desta entrega. |

## 4. Classificacao operacional
| Categoria | Qtde | Recomendacao |
|---|---:|---|
| MIGRATION_PROPOSAL | 349 | Manter untracked; revisar manualmente antes de qualquer incorporacao. |
| LEGACY_REFERENCE | 215 | Manter untracked. |
| DOC_AUDIT_REPORT | 50 | Manter untracked, exceto os artefatos desta triagem. |
| STATIC_ASSET | 8 | Manter untracked. |

## 5. Seguranca
- Candidatos por nome: _migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/certificates/certificado-a1-nao-aparece.md, _migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/certificates/certificado-a3-token-smartcard.md, assets/legacy/Laravel/.env.example, assets/legacy/Laravel/app/Actions/Fortify/PasswordValidationRules.php, assets/legacy/Laravel/lang/en/passwords.php, assets/legacy/Laravel/tests/Feature/PasswordConfirmationTest.php, assets/legacy/Laravel/tests/Feature/PasswordResetTest.php
- Hits de conteudo: assets/legacy/Laravel/.env.example, assets/legacy/Laravel/app/Actions/Fortify/PasswordValidationRules.php, assets/legacy/Laravel/app/Actions/Fortify/UpdateUserPassword.php, assets/legacy/Laravel/app/Http/Kernel.php, assets/legacy/Laravel/app/Providers/FortifyServiceProvider.php, assets/legacy/Laravel/config/sanctum.php, assets/legacy/Laravel/tests/Feature/ApiTokenPermissionsTest.php, assets/legacy/Laravel/tests/Feature/DeleteApiTokenTest.php, assets/legacy/Laravel/tests/Feature/PasswordResetTest.php
- Conclusao: os matches sao falsos positivos de nome/conteudo em arquivos de legado; nao foi identificado segredo real versionado.

## 6. O que deve ser commitado nesta tarefa
- `docs/audit/untracked-final-triage/gitignore-final-check.txt`
- `docs/audit/untracked-final-triage/untracked-final-classification.tsv`
- `docs/audit/untracked-final-triage/untracked-final-dir-summary.txt`
- `docs/audit/untracked-final-triage/untracked-final-files.txt`
- `docs/audit/untracked-final-triage/untracked-final-large-files.txt`
- `docs/audit/untracked-final-triage/untracked-final-sensitive-candidates.txt`
- `docs/audit/untracked-final-triage/untracked-final-sensitive-content-hits.tsv`
- `docs/audit/untracked-final-triage/UNTRACKED_FINAL_TRIAGE_20260623.md`
- `docs/audit/untracked-final-triage/untracked-final-findings.json`

## 7. O que deve permanecer untracked
- `_migration_proposals/hermesops_selective_migration/**`
- `assets/legacy/**`
- `assets/static/**`
- `docs/audit/**` fora da pasta de triagem final
- `docs/apoema-visual-qa/**`
- `docs/hermesops/**`
- `docs/product/**`
- `docs/superpowers/**`
- `docs/*.md` avulsos fora da triagem final

## 8. Requer revisao manual
- `_migration_proposals/hermesops_selective_migration/**`

## 9. Arquivos representativos
### Migracao
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/AGENTS.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ARCHITECTURE.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ENVIRONMENT.hml.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ENVIRONMENT.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/PROJECT_CONTEXT.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/README.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/ROADMAP.md`
- `_migration_proposals/hermesops_selective_migration/docs/hermesops/SECURITY.md`

### Legado
- `assets/legacy/Laravel/.editorconfig`
- `assets/legacy/Laravel/.env.example`
- `assets/legacy/Laravel/.gitattributes`
- `assets/legacy/Laravel/.gitignore`
- `assets/legacy/Laravel/README.md`
- `assets/legacy/Laravel/app/Actions/Fortify/CreateNewUser.php`
- `assets/legacy/Laravel/app/Actions/Fortify/PasswordValidationRules.php`
- `assets/legacy/Laravel/app/Actions/Fortify/ResetUserPassword.php`

### Docs e auditoria
- `docs/audit/ARCHITECTURE_AUDIT.md`
- `docs/audit/AUDIT_ENVIRONMENT.md`
- `docs/audit/B4B2_VISUAL_SMOKE_MANUAL_CHECKLIST.md`
- `docs/audit/BACKEND_AUDIT.md`
- `docs/audit/BACKEND_FINDINGS.csv`
- `docs/audit/BASE44_VISUAL_RECOVERY_H3_EXECUTIVE_SUMMARY.md`
- `docs/audit/DATABASE_FINDINGS.csv`
- `docs/audit/DATABASE_MIGRATIONS_AUDIT.md`
- `docs/apoema-visual-qa/APOEMA_BROWSER_ERRORS.md`
- `docs/apoema-visual-qa/APOEMA_FUNCTIONAL_QA.md`
- `docs/apoema-visual-qa/APOEMA_QA_FINDINGS.json`
- `docs/apoema-visual-qa/APOEMA_VISUAL_QA.md`
- `docs/ADMIN_SUPPORT_PERMISSIONS.md`
- `docs/AI_CHAT_IMPLEMENTATION_REPORT.md`
- `docs/AI_CHAT_INTEGRATION_TODO.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md`
- `docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md`
- `docs/AI_CHAT_UX_REPORT.md`
- `docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md`
- `docs/IMPLEMENTATION_REPORT_UI_UX_QA.md`
- `docs/INVENTORY_COLLABORATORS_CRUD.md`
- `docs/QA_TEST_PLAN_INVENTORY.md`
- `docs/UI_UX_QA_INVENTORY_AUDIT.md`

## 10. Conclusao
A triagem foi concluida sem apagar nada e sem tocar em arquivos fora da pasta de triagem. O conjunto remanescente deve seguir untracked por ora, com revisao manual apenas para a arvore de propostas de migracao.
