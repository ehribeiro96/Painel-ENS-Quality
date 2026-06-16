# Superseded / Historical Audit Docs — H2

Boundary: `DOCS-H2 — audit docs consolidation and selective commit`

Este arquivo registra documentos antigos ou deferidos encontrados em `docs/audit/` durante a consolidação. Nenhum arquivo listado aqui foi apagado, movido, renomeado ou stageado por inclusão em massa. Qualquer uso futuro exige boundary própria e revisão explícita.

## Regra de leitura

- Não usar estes arquivos como fonte atual sem comparar contra `AUDIT_REPORT_INDEX_H2.md`.
- Não commitar documentos antigos não revisados dentro de DOCS-H2.
- Não abrir screenshots antigas ou binários como parte desta classificação.
- Tratar caminhos que apontem para imports, screenshots, segredos, assets ou evidências operacionais apenas como metadado até revisão humana.

## HISTORICAL_SUPERSEDED

| Documento | Status sugerido | Motivo | Ação recomendada |
|---|---|---|---|
| `AMBIGUOUS_REMAINDERS_GIT_C3_REPORT.md` | histórico | Boundary GIT-C3 anterior já documentada | Manter como histórico; não usar como fonte atual |
| `LEGACY_ASSETS_TRIAGE_GIT_C5_REPORT.md` | histórico | Boundary GIT-C5 anterior já fechada | Consultar apenas em boundary LEGACY-H2 |
| `SELECTIVE_COMMITS_GIT_C2_REPORT.md` | histórico | Boundary GIT-C2 anterior já fechada | Manter para rastreabilidade |
| `WORKTREE_BOUNDARY_COMMIT_PLAN_GIT_C1.md` | histórico | Plano antigo de commit boundary | Não reaplicar sem nova revisão |
| `HIGH_FIX_ROUND3_REPORT.md` | histórico | Relatório de rodada antiga de correções | Revisar antes de usar como estado atual |

## OLD_AUDIT_REVIEW

Estes arquivos foram encontrados em `docs/audit/` e não fazem parte do pacote ativo H1/GIT-H2/SEC-H2/QA-C1/QA-C2/DOCS-H2. Devem ser revisados em boundary própria antes de qualquer commit seletivo novo.

| Documento | Status sugerido | Ação recomendada |
|---|---|---|
| `ARCHITECTURE_AUDIT.md` | revisar antes de commit | Consolidar ou superseder em boundary documental futura |
| `AUDIT_ENVIRONMENT.md` | revisar antes de commit | Validar se ambiente ainda é atual |
| `B4B2_VISUAL_SMOKE_MANUAL_CHECKLIST.md` | revisar antes de commit | Pode estar superseded por validações B4-C/B4-D/B5-D |
| `BACKEND_AUDIT.md` | revisar antes de commit | Comparar com H1 antes de promover |
| `BACKEND_FINDINGS.csv` | revisar antes de commit | Evidência antiga; checar escopo e sensibilidade |
| `DATABASE_FINDINGS.csv` | revisar antes de commit | Evidência antiga; não alterar migrations |
| `DATABASE_MIGRATIONS_AUDIT.md` | revisar antes de commit | Boundary própria se envolver migrations |
| `DESKTOP_APP_AUDIT.md` | revisar antes de commit | Validar escopo; Painel não é app desktop |
| `DEVOPS_RELEASE_AUDIT.md` | revisar antes de commit | Boundary infra/release própria |
| `FILE_CLASSIFICATION.csv` | revisar antes de commit | Pode listar paths sensíveis; revisar redigido |
| `FILE_INVENTORY.md` | revisar antes de commit | Pode conter inventário amplo; revisar redigido |
| `FRONTEND_AUDIT.md` | revisar antes de commit | Não misturar com frontend funcional |
| `FRONTEND_FINDINGS.csv` | revisar antes de commit | Evidência antiga; revisar antes de versionar |
| `FULL_PROJECT_AUDIT_REPORT.md` | revisar antes de commit | Superseded parcialmente por `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` |
| `GAP_ANALYSIS.md` | revisar antes de commit | Comparar com backlog H1 |
| `PROJECT_TREE.txt` | revisar antes de commit | Pode conter árvore ampla; validar sensibilidade |
| `RELEASE_HYGIENE_FINDINGS.csv` | revisar antes de commit | Boundary release/hygiene própria |
| `SCRIPTS_OPS_AUDIT.md` | revisar antes de commit | Pode tocar tooling operacional |
| `SCRIPTS_OPS_FINDINGS.csv` | revisar antes de commit | Revisar antes de versionar |
| `SECURITY_AUDIT.md` | revisar antes de commit | Superseded parcialmente por SEC-H2 para sensíveis locais |
| `SECURITY_FINDINGS.csv` | revisar antes de commit | Revisar redigido antes de commit |
| `TESTING_AUDIT.md` | revisar antes de commit | Boundary TEST-H2 própria |
| `TEST_RESULTS.md` | revisar antes de commit | Validar se resultados ainda são atuais |

## SCREENSHOT_EVIDENCE_DEFER

Diretórios de screenshots encontrados por metadado e não abertos:

- `docs/audit/screenshots/`
- `docs/audit/screenshots/b4c/`
- `docs/audit/screenshots/b4c/after/`
- `docs/audit/screenshots/b4c/before/`
- `docs/audit/screenshots/b4d/`
- `docs/audit/screenshots/b4d/after-polish/`
- `docs/audit/screenshots/b4d/authenticated/`
- `docs/audit/screenshots/b4e/`
- `docs/audit/screenshots/b4e-legacy-csp/`
- `docs/audit/screenshots/b4e-legacy-csp/after/`
- `docs/audit/screenshots/b4e-legacy-csp/before/`
- `docs/audit/screenshots/b4e/before/`
- `docs/audit/screenshots/b5b-ollama-lan/`
- `docs/audit/screenshots/b5c-ollama-lan/`
- `docs/audit/screenshots/b5d2-same-origin-ai-chat/`

Status: `SCREENSHOT_EVIDENCE_DEFER`.

Ação recomendada: não commitar em DOCS-H2; abrir boundary própria de evidências visuais se houver necessidade de retenção.

## SENSITIVE_OR_OPERATIONAL_DEFER

Arquivos/diretórios fora do pacote documental ativo que devem permanecer fora do commit DOCS-H2:

- `123`
- `123.pub`
- `imports/`
- `_audit_findings/`
- `_migration_proposals/`
- `ai-lab/`
- `assets/legacy/`
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`
- `frontend/package-lock.json`
- samples e outputs de laboratório na raiz (`docx_sample.md`, `docx_template_output.md`, `pptx_sample.md`, `pptx_template_output.md`)

Status: `SENSITIVE_OR_OPERATIONAL_DEFER` ou `DO_NOT_TOUCH`, conforme o caso.

Ação recomendada: revisão humana ou boundary específica; não abrir conteúdo sensível e não stagear em DOCS-H2.

## Decisão

Os documentos ativos estão em `AUDIT_REPORT_INDEX_H2.md`. Todo material listado aqui permanece preservado no worktree, fora do commit seletivo desta boundary, até uma decisão explícita futura.
