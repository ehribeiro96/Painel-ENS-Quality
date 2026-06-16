# DOCS-H2 — Audit Docs Consolidation

Boundary: `DOCS-H2 — audit docs consolidation and selective commit`

## Resumo executivo

Status: `GO` esperado se o scanner redigido não encontrar segredo real, o commit seletivo for criado e o stage final ficar vazio.

Stage inicial/final:

- Stage inicial: vazio em `main...origin/main [ahead 15]` na FASE 0.
- Stage final esperado: vazio após o commit seletivo DOCS-H2; validação final registrada no chat da boundary.

Arquivos ativos:

- H1: `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md`, `HERMES_IMPROVEMENT_BACKLOG_H1.md`, `HERMES_DO_NOT_TOUCH_MAP_H1.md`, `HERMES_RISK_REGISTER_H1.md`, `HERMES_NEXT_BOUNDARIES_H1.md`.
- GIT-H2: `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md`, `GIT_H2_UNTRACKED_INVENTORY.csv`, `GIT_H2_UNTRACKED_DECISION_MATRIX.md`.
- SEC-H2: `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md`, `SEC_H2_GITIGNORE_PROPOSAL.md`, `SEC_H2_MANUAL_ACTIONS.md`.
- QA-C1/QA-C2: `POST_COMMIT_VALIDATION_QA_C1_REPORT.md`, `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md`.
- DOCS-H2: `README.md`, `NEXT_BOUNDARY_DECISION.md`, `AUDIT_REPORT_INDEX_H2.md`, `SUPERSEDED_AUDIT_DOCS_H2.md`, `AUDIT_DOCS_CONSOLIDATION_H2_REPORT.md`.

Arquivos históricos:

- Listados em `SUPERSEDED_AUDIT_DOCS_H2.md` como `HISTORICAL_SUPERSEDED` ou `OLD_AUDIT_REVIEW`.

Arquivos deferidos:

- Screenshots antigas em `docs/audit/screenshots/`.
- Artefatos sensíveis/operacionais: `123`, `123.pub`, `imports/`, `_audit_findings/`, `_migration_proposals/`, `ai-lab/`, assets legados, package-lock e outputs de laboratório.

## Escopo

Esta boundary é somente documental/auditoria. O objetivo foi consolidar documentação recente, criar índice ativo, registrar documentos antigos como históricos/superseded/deferidos e preparar commit seletivo apenas dos documentos aprovados.

Não houve alteração funcional em backend, frontend, assets, Docker/Compose, migrations, package-lock, AI Chat/Ollama, imports, screenshots ou arquivos sensíveis.

## Documentos ativos consolidados

Os documentos ativos foram organizados no índice `AUDIT_REPORT_INDEX_H2.md` com tabela contendo boundary, status, finalidade, próxima ação, permissão de commit e observações.

Classificação principal:

- `ACTIVE_CURRENT`: H1, GIT-H2, relatório de consolidação DOCS-H2.
- `ACTIVE_SECURITY`: SEC-H2.
- `ACTIVE_VALIDATION`: QA-C1/QA-C2.
- `ACTIVE_INDEX`: README, NEXT_BOUNDARY, índice H2 e superseded H2.
- `DO_NOT_TOUCH`: mapa H1 de áreas sensíveis.

## Documentos de segurança

Documentos ativos de segurança/local sensitive:

- `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md`
- `SEC_H2_GITIGNORE_PROPOSAL.md`
- `SEC_H2_MANUAL_ACTIONS.md`
- `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md`
- `GIT_H2_UNTRACKED_INVENTORY.csv`
- `GIT_H2_UNTRACKED_DECISION_MATRIX.md`

Decisão: podem ser commitados seletivamente como documentação de auditoria, desde que o scanner redigido não encontre segredo real. A implementação da proposta `.gitignore` fica para `IGNORE-H2`.

## Documentos de validação

Documentos ativos de validação:

- `POST_COMMIT_VALIDATION_QA_C1_REPORT.md`: `PARTIAL` por backend HTTP indisponível.
- `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md`: `GO`.

Decisão: QA-C2 é a leitura preferencial de runtime HTTP atual; QA-C1 permanece preservado como registro parcial.

## Documentos históricos/superseded

`SUPERSEDED_AUDIT_DOCS_H2.md` lista documentos antigos encontrados em `docs/audit/` que não entram no pacote ativo desta boundary. Eles permanecem no worktree sem remoção, movimentação ou stage em massa.

Categorias usadas:

- `HISTORICAL_SUPERSEDED`
- `OLD_AUDIT_REVIEW`
- `SCREENSHOT_EVIDENCE_DEFER`
- `SENSITIVE_OR_OPERATIONAL_DEFER`
- `DO_NOT_TOUCH`

## Screenshots e evidências deferidas

Diretórios de screenshots foram inventariados por metadado, sem abrir imagens e sem OCR:

- `docs/audit/screenshots/b4c/`
- `docs/audit/screenshots/b4d/`
- `docs/audit/screenshots/b4e/`
- `docs/audit/screenshots/b4e-legacy-csp/`
- `docs/audit/screenshots/b5b-ollama-lan/`
- `docs/audit/screenshots/b5c-ollama-lan/`
- `docs/audit/screenshots/b5d2-same-origin-ai-chat/`

Decisão: `SCREENSHOT_EVIDENCE_DEFER`; não commitar nesta boundary.

## Arquivos que NÃO foram tocados

- Código funcional de backend e frontend.
- Migrations.
- Docker/Compose.
- `.gitignore` e `.dockerignore`.
- `frontend/package-lock.json`.
- Assets, imports, samples e outputs de laboratório.
- `123` e `123.pub`.
- Screenshots antigas.
- Docs antigos não revisados, exceto serem citados por nome no arquivo de superseded.

## Arquivos que NÃO devem ser commitados nesta boundary

- `docs/audit/screenshots/` e subdiretórios.
- Docs antigos não revisados listados em `SUPERSEDED_AUDIT_DOCS_H2.md`.
- `123`, `123.pub`, `imports/`.
- `_audit_findings/`, `_migration_proposals/`, `ai-lab/`.
- `assets/legacy/` e `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`.
- `frontend/package-lock.json`.
- Workflows CI, testes untracked e arquivos fora do pacote documental autorizado.

## Próximas boundaries recomendadas

1. `IGNORE-H2 — gitignore hygiene for local artifacts`.
2. `CI-H2 — GitHub Actions docker build/push review`.
3. `LEGACY-H2 — legacy assets and DOCX large artifact decision`.
4. `TEST-H2 — pytest markers and validation standardization`.
5. `SEC-H3 — manual sensitive artifact remediation`, somente se revisão humana confirmar necessidade.

## Decisão final

`GO` para commit seletivo dos documentos aprovados do DOCS-H2 se:

- o scanner redigido dos candidatos não identificar segredo real;
- o stage seletivo contiver somente os paths autorizados;
- `git diff --cached --check` passar;
- o commit for criado;
- o stage final ficar vazio.

`NO-GO` se o stage inicial não estiver vazio, se segredo real for encontrado ou se arquivo fora de escopo entrar no stage.
