# Audit Index

Este diretório concentra a documentação de auditoria ativa do projeto Painel ENS-Quality.

Boundary atual: `LEGACY-H2 — legacy assets and DOCX large artifact decision`.

## Leitura recomendada

1. `README.md` — este resumo.
2. `NEXT_BOUNDARY_DECISION.md` — próxima boundary recomendada.
3. `AUDIT_REPORT_INDEX_H2.md` — índice canônico dos relatórios ativos.
4. `LEGACY_H2_REMAINING_ASSETS_DECISION_REPORT.md` — decisão dos assets legados remanescentes e DOCX grande.
5. `LEGACY_H2_ASSET_REFERENCE_MATRIX.md` — matriz de referência/decisão dos assets LEGACY-H2.
6. `LEGACY_H2_EXTERNAL_REFERENCE_SCAN.md` — scan restrito de referências externas em legado.
7. `LEGACY_H2_ASSET_INVENTORY.csv` — inventário CSV por metadados.
8. `CI_H3_DOCKER_WORKFLOW_HARDENING_REPORT.md` — hardening do workflow Docker manual build-only.
9. `CI_H3_WORKFLOW_FINAL_REVIEW.md` — checklist final do workflow CI-H3.
10. `CI_H2_DOCKER_BUILD_PUSH_WORKFLOW_REVIEW.md` — revisão estática herdada do workflow Docker build/push.
11. `CI_H2_WORKFLOW_DECISION_MATRIX.md` — matriz de decisão CI-H2.
12. `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` — auditoria completa H1.
13. `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md` — triagem de untracked.
14. `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md` — triagem de artefatos sensíveis locais.
15. `IGNORE_H2_GITIGNORE_HYGIENE_REPORT.md` — hygiene de ignore para artefatos locais/sensíveis.
16. `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md` — validação runtime HTTP atual.

## Documentos ativos principais

| Documento | Status | Uso |
|---|---|---|
| `AUDIT_REPORT_INDEX_H2.md` | ACTIVE_INDEX | Índice claro dos relatórios ativos e da ordem de leitura |
| `AUDIT_DOCS_CONSOLIDATION_H2_REPORT.md` | ACTIVE_CURRENT | Relatório da consolidação documental DOCS-H2 |
| `IGNORE_H2_GITIGNORE_HYGIENE_REPORT.md` | ACTIVE_SECURITY | Relatório da hygiene de ignore para artefatos locais/sensíveis |
| `LEGACY_H2_REMAINING_ASSETS_DECISION_REPORT.md` | ACTIVE_CURRENT | Decisão conservadora sobre `assets/legacy/`, DOCX grande e ícones remanescentes |
| `LEGACY_H2_ASSET_REFERENCE_MATRIX.md` | ACTIVE_CURRENT | Matriz de referência/decisão dos assets remanescentes |
| `LEGACY_H2_EXTERNAL_REFERENCE_SCAN.md` | ACTIVE_CURRENT | Scan textual restrito de referências externas no legado |
| `LEGACY_H2_ASSET_INVENTORY.csv` | ACTIVE_CURRENT | Inventário CSV por metadados, sem abertura de binários |
| `CI_H3_DOCKER_WORKFLOW_HARDENING_REPORT.md` | ACTIVE_CURRENT | Hardening CI-H3 do workflow Docker para validação manual build-only |
| `CI_H3_WORKFLOW_FINAL_REVIEW.md` | ACTIVE_CURRENT | Checklist final e decisão de versionamento seguro CI-H3 |
| `CI_H2_DOCKER_BUILD_PUSH_WORKFLOW_REVIEW.md` | ACTIVE_REFERENCE | Auditoria estática herdada do workflow Docker build/push sem publicar |
| `CI_H2_WORKFLOW_DECISION_MATRIX.md` | ACTIVE_REFERENCE | Decisão CI-H2 que abriu a boundary CI-H3 |
| `SUPERSEDED_AUDIT_DOCS_H2.md` | ACTIVE_INDEX | Lista de documentos históricos/superseded/deferidos |
| `NEXT_BOUNDARY_DECISION.md` | ACTIVE_INDEX | Próximas boundaries recomendadas após LEGACY-H2 |
| `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` | ACTIVE_CURRENT | Relatório completo H1 |
| `HERMES_IMPROVEMENT_BACKLOG_H1.md` | ACTIVE_CURRENT | Backlog de melhoria H1 |
| `HERMES_DO_NOT_TOUCH_MAP_H1.md` | DO_NOT_TOUCH | Mapa de áreas que não devem ser alteradas sem boundary explícita |
| `HERMES_RISK_REGISTER_H1.md` | ACTIVE_CURRENT | Registro de riscos H1 |
| `HERMES_NEXT_BOUNDARIES_H1.md` | ACTIVE_CURRENT | Sequência sugerida pela H1 |
| `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md` | ACTIVE_CURRENT | Triagem dos untracked recentes |
| `GIT_H2_UNTRACKED_INVENTORY.csv` | ACTIVE_CURRENT | Inventário CSV dos untracked |
| `GIT_H2_UNTRACKED_DECISION_MATRIX.md` | ACTIVE_CURRENT | Matriz de decisão dos untracked |
| `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md` | ACTIVE_SECURITY | Triagem local de artefatos sensíveis |
| `SEC_H2_GITIGNORE_PROPOSAL.md` | ACTIVE_SECURITY | Proposta-base usada por IGNORE-H2 |
| `SEC_H2_MANUAL_ACTIONS.md` | ACTIVE_SECURITY | Ações manuais de segurança |
| `POST_COMMIT_VALIDATION_QA_C1_REPORT.md` | ACTIVE_VALIDATION | Validação parcial pós-commit |
| `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md` | ACTIVE_VALIDATION | Validação runtime HTTP com status GO |

## Segurança e do-not-touch

- Não abrir `123`, `123.pub`, `.env*`, dumps, bancos locais, tokens, credenciais, `imports/`, screenshots antigas ou binários grandes.
- `IGNORE-H2` protegeu via ignore somente artefatos locais/sensíveis já classificados: `123`, `123.pub`, `imports/`, extensões sensíveis, outputs locais e `frontend/package-lock.json`.
- `CI-H2` analisou `.github/workflows/docker-build-push.yml` sem versionar, sem executar publish, sem usar secrets e sem chamar GitHub API.
- `CI-H3` reescreveu e versionou `.github/workflows/docker-build-push.yml` como workflow manual-only/build-only, sem publish, sem GHCR, sem `latest`, sem login e sem `packages: write`.
- `LEGACY-H2` inventariou `assets/legacy/`, DOCX grande e ícones por metadados; não abriu DOCX/imagens, não usou OCR e não stageou assets.
- Não usar ignore para esconder candidatos de boundaries futuras: assets legados, DOCX grande, testes pendentes, docs históricos e screenshots antigas continuam fora do escopo de ignore em massa até decisão humana.
- Para áreas sensíveis, consultar primeiro `HERMES_DO_NOT_TOUCH_MAP_H1.md`.

## Documentos antigos

Documentos antigos em `docs/audit/` não foram apagados, movidos ou commitados em massa. Eles estão classificados em `SUPERSEDED_AUDIT_DOCS_H2.md` como históricos, superseded, pendentes de revisão ou evidências deferidas.

## Próxima boundary

A próxima boundary recomendada é `TEST-H2 — pytest markers and validation standardization`. `LEGACY-H3 — legacy archive/manual artifact handling` só deve ocorrer se houver decisão humana sobre archive/commit/ignore dos assets remanescentes. `CI-H4 — publish workflow design` só deve ocorrer se houver decisão humana explícita para publicar imagem; `SEC-H3` só deve ocorrer se revisão humana confirmar necessidade.
