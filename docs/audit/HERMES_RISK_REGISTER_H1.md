# HERMES_RISK_REGISTER_H1

## H1-RISK-001
ID: H1-RISK-001
Risco: Worktree grande e misto com 631 untracked.
Área: Git/release
Probabilidade: Alta
Impacto: Alto
Severidade: Alta
Evidência: FASE 0 e inventário completo posterior.
Mitigação: triagem por grupo antes de qualquer feature.
Boundary recomendada: `GIT-H2 — untracked safety triage`.

## H1-RISK-002
ID: H1-RISK-002
Risco: Arquivos untracked possivelmente sensíveis (`123`, `123.pub`, `imports/`).
Área: Segurança/dados
Probabilidade: Média
Impacto: Alto
Severidade: Alta
Evidência: listagem untracked; conteúdo não aberto por regra de segurança.
Mitigação: revisão humana local sem imprimir valores.
Boundary recomendada: `SEC-H2 — local sensitive artifact triage`.

## H1-RISK-003
ID: H1-RISK-003
Risco: Workflow Docker build/push untracked pode publicar artefatos sem controle.
Área: CI/CD
Probabilidade: Média
Impacto: Alto
Severidade: Alta
Evidência: `.github/workflows/docker-build-push.yml` untracked.
Mitigação: revisar triggers, permissões e secrets antes de commit.
Boundary recomendada: `CI-H2 — GitHub Actions build/push review without publishing`.

## H1-RISK-004
ID: H1-RISK-004
Risco: `main` ahead 15.
Área: Git/release
Probabilidade: Alta
Impacto: Médio
Severidade: Média
Evidência: `git status --short --branch`.
Mitigação: decidir push/PR/backup depois de triagem; não fazer durante auditoria.
Boundary recomendada: `RELEASE-H2 — local branch publication decision`.

## H1-RISK-005
ID: H1-RISK-005
Risco: `assets/legacy/` volumoso e não triado.
Área: Legacy/assets
Probabilidade: Alta
Impacto: Médio
Severidade: Média
Evidência: grupo untracked grande; GIT-C5 deixou para boundary própria.
Mitigação: inventariar dependências antes de commit/delete.
Boundary recomendada: `LEGACY-H2 — legacy assets inventory`.

## H1-RISK-006
ID: H1-RISK-006
Risco: DOCX grande do guia ilustrado sem decisão.
Área: Legacy/docs/assets
Probabilidade: Média
Impacto: Médio
Severidade: Média
Evidência: `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` untracked.
Mitigação: decidir se vai para Git LFS, release artifact, storage externo ou ignore.
Boundary recomendada: `LEGACY-H2 — large DOCX decision`.

## H1-RISK-007
ID: H1-RISK-007
Risco: Referência externa remanescente no legado.
Área: Legacy/security/privacy
Probabilidade: Média
Impacto: Médio
Severidade: Média
Evidência: busca legacy encontrou URL externa em template hero.
Mitigação: mapear e substituir somente com asset local aprovado e smoke legado.
Boundary recomendada: `LEGACY-H2 — external reference removal`.

## H1-RISK-008
ID: H1-RISK-008
Risco: Exceções genéricas no backend.
Área: Backend/observability
Probabilidade: Média
Impacto: Médio
Severidade: Média
Evidência: FASE 3 contou 15 `except Exception`.
Mitigação: revisar por fluxo, manter logs e testes.
Boundary recomendada: `BACKEND-H2 — exception handling review`.

## H1-RISK-009
ID: H1-RISK-009
Risco: Falta de tiers/markers formais de testes.
Área: Testes/release
Probabilidade: Média
Impacto: Médio
Severidade: Média
Evidência: muitos testes por domínio; auditoria não encontrou padronização de markers como decisão canônica.
Mitigação: criar comandos unit/integration/smoke/operational.
Boundary recomendada: `TEST-H2 — pytest markers and validation commands`.

## H1-RISK-010
ID: H1-RISK-010
Risco: Documentação histórica volumosa pode gerar decisão obsoleta.
Área: Documentação
Probabilidade: Alta
Impacto: Médio
Severidade: Média
Evidência: FASE 11 encontrou muitos relatórios com GO/PARTIAL/NEXT e README extenso.
Mitigação: índice canônico current/historical/superseded.
Boundary recomendada: `DOCS-H2 — audit docs consolidation`.

## H1-RISK-011
ID: H1-RISK-011
Risco: Alterar AI Chat/Ollama sem necessidade.
Área: AI Chat
Probabilidade: Média
Impacto: Alto
Severidade: Alta
Evidência: provider e baseline recém-validados.
Mitigação: marcar `DO_NOT_TOUCH`.
Boundary recomendada: `AI-H2 — controlled provider benchmark/change`.

## H1-RISK-012
ID: H1-RISK-012
Risco: Alterar Docker volumes ou migrations em cleanup.
Área: Infra/DB
Probabilidade: Baixa
Impacto: Crítico
Severidade: Alta
Evidência: regras do projeto e presença de volumes Postgres/app.
Mitigação: proibir prune/down -v/reset; exigir aprovação humana e backup.
Boundary recomendada: `OPS-H2` ou `DB-H2` específica.
