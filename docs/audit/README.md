# Audit Index

Este diretório concentra a documentação de auditoria ativa do projeto Painel ENS-Quality.

Boundary atual: `DOCS-H2 — audit docs consolidation and selective commit`.

## Leitura recomendada

1. `README.md` — este resumo.
2. `NEXT_BOUNDARY_DECISION.md` — próxima boundary recomendada.
3. `AUDIT_REPORT_INDEX_H2.md` — índice canônico dos relatórios ativos.
4. `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` — auditoria completa H1.
5. `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md` — triagem de untracked.
6. `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md` — triagem de artefatos sensíveis locais.
7. `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md` — validação runtime HTTP atual.

## Documentos ativos principais

| Documento | Status | Uso |
|---|---|---|
| `AUDIT_REPORT_INDEX_H2.md` | ACTIVE_INDEX | Índice claro dos relatórios ativos e da ordem de leitura |
| `AUDIT_DOCS_CONSOLIDATION_H2_REPORT.md` | ACTIVE_CURRENT | Relatório desta consolidação documental |
| `SUPERSEDED_AUDIT_DOCS_H2.md` | ACTIVE_INDEX | Lista de documentos históricos/superseded/deferidos |
| `NEXT_BOUNDARY_DECISION.md` | ACTIVE_INDEX | Próximas boundaries recomendadas após DOCS-H2 |
| `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` | ACTIVE_CURRENT | Relatório completo H1 |
| `HERMES_IMPROVEMENT_BACKLOG_H1.md` | ACTIVE_CURRENT | Backlog de melhoria H1 |
| `HERMES_DO_NOT_TOUCH_MAP_H1.md` | DO_NOT_TOUCH | Mapa de áreas que não devem ser alteradas sem boundary explícita |
| `HERMES_RISK_REGISTER_H1.md` | ACTIVE_CURRENT | Registro de riscos H1 |
| `HERMES_NEXT_BOUNDARIES_H1.md` | ACTIVE_CURRENT | Sequência sugerida pela H1 |
| `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md` | ACTIVE_CURRENT | Triagem dos untracked recentes |
| `GIT_H2_UNTRACKED_INVENTORY.csv` | ACTIVE_CURRENT | Inventário CSV dos untracked |
| `GIT_H2_UNTRACKED_DECISION_MATRIX.md` | ACTIVE_CURRENT | Matriz de decisão dos untracked |
| `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md` | ACTIVE_SECURITY | Triagem local de artefatos sensíveis |
| `SEC_H2_GITIGNORE_PROPOSAL.md` | ACTIVE_SECURITY | Proposta para boundary futura IGNORE-H2 |
| `SEC_H2_MANUAL_ACTIONS.md` | ACTIVE_SECURITY | Ações manuais de segurança |
| `POST_COMMIT_VALIDATION_QA_C1_REPORT.md` | ACTIVE_VALIDATION | Validação parcial pós-commit |
| `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md` | ACTIVE_VALIDATION | Validação runtime HTTP com status GO |

## Segurança e do-not-touch

- Não abrir `123`, `123.pub`, `.env*`, dumps, bancos locais, tokens, credenciais, `imports/`, screenshots antigas ou binários grandes.
- Não alterar `.gitignore`, `.dockerignore`, package-lock, migrations, Docker/Compose, AI Chat/Ollama, frontend/backend/assets ou código funcional nesta trilha documental.
- Para áreas sensíveis, consultar primeiro `HERMES_DO_NOT_TOUCH_MAP_H1.md`.

## Documentos antigos

Documentos antigos em `docs/audit/` não foram apagados, movidos ou commitados em massa. Eles estão classificados em `SUPERSEDED_AUDIT_DOCS_H2.md` como históricos, superseded, pendentes de revisão ou evidências deferidas.

## Próxima boundary

A próxima boundary recomendada é `IGNORE-H2 — gitignore hygiene for local artifacts`, seguida por `CI-H2`, `LEGACY-H2`, `TEST-H2` e eventualmente `SEC-H3` somente se revisão humana confirmar necessidade.
