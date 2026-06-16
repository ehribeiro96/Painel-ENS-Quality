# HERMES_NEXT_BOUNDARIES_H1

## Ordem recomendada

1. `GIT-H2 — untracked safety triage`
2. `SEC-H2 — local sensitive artifact triage`
3. `DOCS-H2 — audit docs consolidation and index hygiene`
4. `TEST-H2 — pytest markers and validation command standardization`
5. `CI-H2 — GitHub Actions build/push review without publishing`
6. `LEGACY-H2 — legacy assets and external-reference inventory`
7. `BACKEND-H2 — exception handling and API contract hardening`
8. `FRONTEND-H2 — route UX/accessibility review with authenticated screenshots`
9. `OPS-H2 — health/readiness/runbook consolidation`
10. `DB-H2 — migration policy and validation checklist`

## 1. GIT-H2 — untracked safety triage
Objetivo: classificar os 631 untracked sem alterar conteúdo.
Escopo permitido: inventário, tamanho, tipo, agrupamento, recomendação commit/ignore/manual.
Fora de escopo: `git add`, `git clean`, deletar, mover, renomear.
Validações: `git status`, `git ls-files --others --exclude-standard`, classificação por grupo.
Critério de GO: tabela de decisão por grupo com aprovação humana pendente onde necessário.
Critério de NO-GO: segredo real confirmado ou stage não vazio.

## 2. SEC-H2 — local sensitive artifact triage
Objetivo: decidir com humano o que são `123`, `123.pub` e `imports/`.
Escopo permitido: inspeção local redigida, sem expor valores no chat.
Fora de escopo: commit, upload, impressão de conteúdo sensível, deleção sem confirmação.
Validações: classificação de sensibilidade.
Critério de GO: decisão humana documentada.
Critério de NO-GO: segredo real encontrado sem rotação/mitigação externa.

## 3. DOCS-H2 — audit docs consolidation and index hygiene
Objetivo: reduzir confusão documental sem apagar histórico.
Escopo permitido: README/index, status current/historical/superseded, links canônicos.
Fora de escopo: remover relatórios, reescrever fatos antigos, mexer em código.
Validações: links relativos/absolutos revisados; status sem conflito.
Critério de GO: índice curto e decisão de próxima boundary clara.
Critério de NO-GO: perda de rastreabilidade ou apagamento de relatório.

## 4. TEST-H2 — pytest markers and validation command standardization
Objetivo: separar unit/integration/smoke/operational.
Escopo permitido: markers, docs de comandos, ajustes mínimos de coleta se necessários.
Fora de escopo: reescrever lógica dos testes ou corrigir features.
Validações: collect-only e subset unit estáveis; compileall.
Critério de GO: comandos canônicos documentados.
Critério de NO-GO: coleta quebrada por mudança estrutural.

## 5. CI-H2 — GitHub Actions build/push review without publishing
Objetivo: avaliar workflow Docker antes de versionar.
Escopo permitido: revisão estática, dry-run conceitual, ajuste documental.
Fora de escopo: publicar imagem, configurar secrets, push.
Validações: lint YAML se disponível; revisão de permissions/triggers.
Critério de GO: workflow seguro ou decisão de manter untracked.
Critério de NO-GO: publish automático inseguro ou secrets indefinidos.

## 6. LEGACY-H2 — legacy assets and external-reference inventory
Objetivo: mapear assets legacy e referências externas.
Escopo permitido: inventário, dependency map, smoke legado se ambiente pronto.
Fora de escopo: remover CSP/unsafe-inline, deletar assets, converter DOCX.
Validações: `/admin` e `/assinaturas` smoke antes/depois se houver qualquer alteração futura.
Critério de GO: mapa de assets e decisão por grupo.
Critério de NO-GO: quebra de rota legacy ou dependência desconhecida.

## 7. BACKEND-H2 — exception handling and API contract hardening
Objetivo: revisar exceções amplas e DTOs críticos.
Escopo permitido: análise e patches mínimos com testes.
Fora de escopo: auth rewrite, imports, migrations, macro flow.
Validações: compileall, testes de rotas afetadas.
Critério de GO: logs melhores sem mudar contrato indevido.
Critério de NO-GO: mudança de contrato sem teste.

## 8. FRONTEND-H2 — route UX/accessibility review with authenticated screenshots
Objetivo: validar UX por rota sem refatoração ampla.
Escopo permitido: checklist, screenshots, pequenos ajustes se aprovados.
Fora de escopo: AppShell rewrite, CSS global amplo, dependências novas.
Validações: `npm run build`, smoke autenticado.
Critério de GO: evidência visual e build verde.
Critério de NO-GO: regressão visual ou alteração sem screenshot.

## 9. OPS-H2 — health/readiness/runbook consolidation
Objetivo: separar status de dependências, app, frontend e AI provider.
Escopo permitido: docs/runbook e comandos seguros.
Fora de escopo: alterar compose/volumes/portas.
Validações: `docker compose ps`, health endpoints se app estiver online.
Critério de GO: runbook reproduzível.
Critério de NO-GO: qualquer ação destrutiva.

## 10. DB-H2 — migration policy and validation checklist
Objetivo: documentar política segura de migrations.
Escopo permitido: checklist e validações não destrutivas.
Fora de escopo: editar migrations, upgrade em produção, SQL destrutivo.
Validações: `alembic heads/check` apenas em ambiente seguro.
Critério de GO: política clara.
Critério de NO-GO: risco de alteração de banco sem aprovação.
