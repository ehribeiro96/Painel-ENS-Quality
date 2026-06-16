# HERMES_IMPROVEMENT_BACKLOG_H1

## H1-BACKLOG-001
ID: H1-BACKLOG-001
Área: Worktree/untracked
Prioridade: P1
Tipo: release
Evidência: 631 untracked observados no inventário completo; FASE 0 mostrou múltiplos grupos antigos.
Impacto: risco de commit acidental, mistura de boundaries, vazamento de dados ou regressão documental.
Recomendação: abrir boundary `GIT-H2 — untracked safety triage` somente leitura primeiro.
Boundary sugerida: `GIT-H2 — untracked safety triage`
Arquivos prováveis: `_migration_proposals/`, `assets/legacy/`, `docs/audit/`, `imports/`, `tests/`, `.github/workflows/docker-build-push.yml`, `frontend/package-lock.json`.
O que NÃO fazer: não rodar `git add .`, `git clean`, `git reset`, `git checkout` ou deletar arquivos.
Critério de GO: cada grupo classificado como commit/ignore/delete/manual-only com aprovação humana.

## H1-BACKLOG-002
ID: H1-BACKLOG-002
Área: CI/CD GitHub Actions
Prioridade: P1
Tipo: infra
Evidência: `.github/workflows/docker-build-push.yml` aparece untracked.
Impacto: workflow de build/push pode publicar imagem errada, exigir secrets ou alterar release sem controle.
Recomendação: revisar permissões, triggers, secrets e dry-run antes de versionar.
Boundary sugerida: `CI-H2 — GitHub Actions build/push review without publishing`
Arquivos prováveis: `.github/workflows/docker-build-push.yml`, docs de release.
O que NÃO fazer: não commitar workflow de push sem revisão humana; não configurar secrets durante auditoria.
Critério de GO: workflow documentado, sem publish automático inesperado, com gate manual ou branch controlado.

## H1-BACKLOG-003
ID: H1-BACKLOG-003
Área: Segurança/segredos
Prioridade: P1
Tipo: security
Evidência: `123`, `123.pub` untracked; `imports/` untracked; scanner não confirmou segredo real em tracked.
Impacto: arquivos podem ser chave, amostra sensível ou dado bruto; risco de exposição se commitados.
Recomendação: revisão humana local sem imprimir valores; se forem chaves, remover/rotacionar fora do chat.
Boundary sugerida: `SEC-H2 — local sensitive artifact triage`
Arquivos prováveis: `123`, `123.pub`, `imports/`.
O que NÃO fazer: não abrir conteúdo no chat; não commitar; não apagar sem confirmação.
Critério de GO: classificação manual concluída e ação segura decidida.

## H1-BACKLOG-004
ID: H1-BACKLOG-004
Área: Documentação
Prioridade: P2
Tipo: docs
Evidência: docs/audit contém muitos relatórios históricos, screenshots e status antigos; README já é extenso.
Impacto: dificuldade de saber qual relatório é canônico; risco de decisão baseada em status obsoleto.
Recomendação: criar índice H2 com status current/historical/superseded, sem apagar histórico.
Boundary sugerida: `DOCS-H2 — audit docs consolidation and index hygiene`
Arquivos prováveis: `docs/audit/README.md`, `docs/audit/NEXT_BOUNDARY_DECISION.md`, relatórios históricos.
O que NÃO fazer: não deletar docs antigos; não reescrever histórico funcional.
Critério de GO: índice curto com links canônicos e status por boundary.

## H1-BACKLOG-005
ID: H1-BACKLOG-005
Área: Testes
Prioridade: P2
Tipo: test
Evidência: 31 testes Python; compileall passou; testes cobrem muitos domínios, mas sem tier/markers documentados na auditoria.
Impacto: validações futuras podem rodar coisa demais, coisa de menos ou falhar por ambiente.
Recomendação: padronizar markers unit/integration/smoke/operational e comandos canônicos.
Boundary sugerida: `TEST-H2 — pytest markers and validation command standardization`
Arquivos prováveis: `tests/`, `pytest.ini` se existir/criar, docs/audit.
O que NÃO fazer: não reescrever testes de domínio junto; não rodar root pytest sem escopo se houver árvores copiadas.
Critério de GO: comandos documentados e coleta estável.

## H1-BACKLOG-006
ID: H1-BACKLOG-006
Área: Backend
Prioridade: P2
Tipo: tech-debt
Evidência: busca FASE 3 contou 15 ocorrências de `except Exception` e 1 de `logger.exception` no escopo backend/tests.
Impacto: tratamento genérico pode mascarar causa-raiz, confundir observabilidade ou esconder erro operacional.
Recomendação: revisar por fluxo crítico e trocar por exceções específicas onde seguro.
Boundary sugerida: `BACKEND-H2 — exception handling review`
Arquivos prováveis: `backend/app/core/startup.py`, routes e services indicados pela busca.
O que NÃO fazer: não alterar contrato de erro sem testes; não mexer em auth/imports/macros junto.
Critério de GO: exceções críticas mapeadas, logs preservados, testes verdes.

## H1-BACKLOG-007
ID: H1-BACKLOG-007
Área: Legacy `/admin` e `/assinaturas`
Prioridade: P2
Tipo: security
Evidência: FASE 7 encontrou templates/JS/hero/DOCX e referências externas legadas; CSP validada recentemente.
Impacto: referência externa remanescente pode afetar privacidade, disponibilidade ou CSP futura.
Recomendação: inventariar referências externas e assets, sem remover em massa.
Boundary sugerida: `LEGACY-H2 — legacy assets and external-reference inventory`
Arquivos prováveis: `assets/templates/`, `assets/static/`, `assets/legacy/`.
O que NÃO fazer: não mexer em CSP, fonts, whitespace ou assets runtime sem smoke legado.
Critério de GO: mapa de dependências e decisão humana por asset.

## H1-BACKLOG-008
ID: H1-BACKLOG-008
Área: Frontend React
Prioridade: P2
Tipo: ux
Evidência: build passou; shell validado; CSS/global e rotas têm superfície ampla.
Impacto: regressão visual pode passar despercebida se alteração ampla for feita sem screenshot autenticado.
Recomendação: review por rota com screenshots, estados loading/empty/error e acessibilidade básica.
Boundary sugerida: `FRONTEND-H2 — route UX/accessibility review`
Arquivos prováveis: `frontend/itam-platform/src/pages/`, `components/`, `styles.css`.
O que NÃO fazer: não refatorar CSS global sem evidência; não tocar AppShell sem necessidade.
Critério de GO: screenshots e checklist por rota, build verde.

## H1-BACKLOG-009
ID: H1-BACKLOG-009
Área: Infra/Docker/ops
Prioridade: P2
Tipo: infra
Evidência: Docker nativo WSL e Postgres/Redis healthy; app container não estava listado em `docker compose ps` da auditoria.
Impacto: operação local pode confundir status de dependências com status da aplicação.
Recomendação: runbook health/readiness com serviços esperados por cenário.
Boundary sugerida: `OPS-H2 — health/readiness/runbook consolidation`
Arquivos prováveis: docs/runbook, docs/audit.
O que NÃO fazer: não alterar volumes, compose ou portas sem plano.
Critério de GO: comandos seguros documentados e critérios app/deps separados.

## H1-BACKLOG-010
ID: H1-BACKLOG-010
Área: Database/migrations
Prioridade: P3
Tipo: docs
Evidência: migrations existem e estão cobertas por testes; regra do projeto proíbe alteração nesta boundary.
Impacto: migrations manuais erradas podem quebrar Postgres canônico.
Recomendação: documentar política de criação/validação de migrations em boundary própria se houver demanda.
Boundary sugerida: `DB-H2 — migration policy and validation checklist`
Arquivos prováveis: `backend/alembic/`, docs.
O que NÃO fazer: não editar migrations existentes; não rodar upgrade em banco produtivo.
Critério de GO: checklist sem alteração destrutiva.
