# PRODUCT-H1 — Feature Backlog em boundaries

Regra geral: cada boundary deve começar com stage vazio, operar em escopo pequeno, preservar do-not-touch e terminar com validação objetiva. Nenhuma boundary abaixo autoriza `git add`, commit ou push automaticamente.

## UAT-H1 — end-to-end operational scenario validation

Tipo: UAT / validação funcional
Prioridade: P0
Valor operacional: Prova se o produto já suporta rotina N2 real antes de implementar novas features.
Descrição: Executar cenários sintéticos ponta-a-ponta cobrindo ativo manual, ativo importado, movimentação, macro, cópia, histórico, auditoria, AI Chat assistivo, erro de importação e RBAC.
Arquivos prováveis: `docs/audit/UAT_H1_REPORT.md`, `docs/product/PRODUCT_H1_UAT_SCENARIOS.md`; se necessário, fixtures sintéticas em boundary futura.
O que não mexer: backend, frontend, migrations, Docker, provider IA, ImportService, legacy, assets, package-lock.
Critérios de aceite: 10 cenários executados ou bloqueios documentados; GO/NO-GO por cenário; evidência sem dado real; bugs viram boundaries específicas.
Validações: `git status --short --branch`, `git diff --cached --name-status`, runtime local quando disponível, screenshots/logs redigidos.
Riscos: ambiente local offline; falta de massa sintética; auditoria sem filtros dificultar evidência.
Status recomendado: próxima boundary.

## ASSET-H1 — asset detail and lifecycle hardening

Tipo: Produto + backend/frontend
Prioridade: P1
Valor operacional: Aumenta confiança na CMDB operacional e reduz movimentações baseadas em dado ambíguo.
Descrição: Endurecer criação/detalhe/lista de ativos, legibilidade de usuário/local/status, estados de erro e consistência operacional.
Arquivos prováveis: `backend/app/api/v1/routes/assets.py`, `backend/app/domains/assets/service.py`, `backend/app/domains/assets/schemas.py`, `frontend/itam-platform/src/pages/AssetsPage.tsx`, `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`, testes de assets.
O que não mexer: import pipeline, migrations, AI/Ollama, legacy, Docker, package-lock.
Critérios de aceite: ativo manual criado com identidade mínima; detalhe mostra dados reais; inconsistências são visíveis; auditoria de create/update/delete preservada.
Validações: testes de assets, compileall, build frontend se tocar frontend.
Riscos: mudar contrato API sem atualizar TS types; retornar model cru; poluir UX com campos demais.
Status recomendado: após UAT-H1.

## MOV-H1 — movement creation and validation hardening

Tipo: Produto crítico / fluxo operacional
Prioridade: P1
Valor operacional: Garante que a mudança de usuário/status/local seja confiável e auditável.
Descrição: Fortalecer criação de movimentação, confirmação explícita, legibilidade do antes/depois e comportamento pós-submit.
Arquivos prováveis: `backend/app/api/v1/routes/assets.py`, `backend/app/domains/assets/service.py`, `backend/app/domains/movements/schemas.py`, `frontend/itam-platform/src/components/MoveAssetDialog.tsx`, `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`, testes de movement/assets.
O que não mexer: `AssetMovement` imutável sem teste; imports; macros fora do vínculo pós-movimentação; migrations sem plano.
Critérios de aceite: movimento salvo uma vez; valida status IN_USE exige usuário; histórico atualiza; evento `MOVE` em audit log.
Validações: teste unitário/integrado do move; UAT cenário 3; build frontend.
Riscos: modal fechar antes da macro ser vista; duplicidade por retry; falha de concorrência se remover lock.
Status recomendado: após UAT-H1 se cenário 3/4 falhar ou ficar frágil.

## MACRO-H1 — ITIL macro generation polish

Tipo: Produto crítico / macros
Prioridade: P1
Valor operacional: Reduz tempo N2 e padroniza comunicação ITIL.
Descrição: Polir geração de macro oficial pós-movimentação, preview, pendências, cópia e rastreabilidade de `generation_id`.
Arquivos prováveis: `backend/app/api/v1/routes/macros.py`, `backend/app/domains/macros/service.py`, `backend/app/domains/macros/schemas.py`, `frontend/itam-platform/src/pages/MacrosPage.tsx`, `frontend/itam-platform/src/components/MoveAssetDialog.tsx`, testes de macros.
O que não mexer: templates oficiais sem revisão; IA provider; migrations; import pipeline.
Critérios de aceite: macro só depois do movimento salvo; cópia exige geração persistida; auditoria `macro_generated`/`macro_copied`; campos pendentes visíveis.
Validações: testes de macros/audit, UAT cenários 4 e 5, build frontend.
Riscos: gerar macro duplicada; ocultar pendências; marcar copied sem clipboard bem-sucedido.
Status recomendado: após UAT-H1, em paralelo conceitual com MOV-H1 mas implementação separada.

## HISTORY-H1 — history and audit traceability

Tipo: Produto + auditoria
Prioridade: P1
Valor operacional: Permite investigar quem fez o quê, quando e por quê.
Descrição: Melhorar rastreabilidade de ativo/movimento/macro/auditoria, com filtros e IDs úteis para suporte.
Arquivos prováveis: `backend/app/api/v1/routes/audit.py`, `backend/app/domains/audit/schemas.py`, `backend/app/domains/audit/service.py`, `frontend/itam-platform/src/pages/AuditLogsPage.tsx`, `AssetDetailsPage.tsx`.
O que não mexer: dados históricos, migrations sem necessidade, auth/RBAC sem plano.
Critérios de aceite: localizar eventos por entidade/ação/ID/período; timeline mostra nomes úteis; auditoria preserva request/correlation id.
Validações: testes audit/log filters, UAT cenários 6 e 7, RBAC checks.
Riscos: expor dados sensíveis nos logs; consultas sem paginação; quebrar acesso ADMIN/MANAGER.
Status recomendado: após MOV-H1/MACRO-H1 ou se UAT evidenciar bloqueio de auditoria.

## AI-H1 — AI assisted macro explanation and suggestion

Tipo: IA assistiva / produto
Prioridade: P2
Valor operacional: Ajuda N2 a entender e revisar texto sem delegar decisão à IA.
Descrição: Criar uso assistivo para explicar macro, sugerir clareza e apontar campos pendentes, mantendo aprovação humana.
Arquivos prováveis: `backend/app/domains/ai_chat/*`, `backend/app/api/v1/routes/ai_chat.py`, `frontend/itam-platform/src/pages/AiChatPage.tsx`, componentes `ai-chat`.
O que não mexer: provider `ollama-lan`, baseline `qwen3:1.7b-64k`, sanitização `<think>`, endpoints operacionais.
Critérios de aceite: IA não altera dados; indisponibilidade mostra status claro; respostas não incluem `<think>`; prompts não vazam segredo.
Validações: testes AI Chat existentes, smoke Ollama LAN quando ambiente disponível, UAT cenário 8.
Riscos: automação indevida; usuário confiar cegamente; provider offline.
Status recomendado: depois do fluxo operacional estar GO.

## REPORT-H1 — operational dashboard and export

Tipo: Relatórios / operação
Prioridade: P2
Valor operacional: Dá visibilidade de estoque, uso, manutenção, importações e movimentações.
Descrição: Evoluir dashboard/export com métricas acionáveis, filtros e export seguro.
Arquivos prováveis: `backend/app/api/v1/routes/dashboard.py`, `backend/app/domains/dashboard/service.py`, `frontend/itam-platform/src/pages/DashboardPage.tsx`, `ImportsPage.tsx`.
O que não mexer: fluxo move/macro; dados produtivos; imports apply; Docker.
Critérios de aceite: métricas vêm do PostgreSQL; filtros não degradam performance; export respeita campos permitidos.
Validações: testes dashboard, build frontend, checagem de paginação/performance básica.
Riscos: KPI sem valor operacional; vazamento por export; consultas pesadas.
Status recomendado: após UAT e fluxo crítico estabilizado.

## UX-H1 — route-level usability polish

Tipo: UX incremental
Prioridade: P2
Valor operacional: Reduz erro humano e acelera adoção sem redesign amplo.
Descrição: Polir rotas individualmente com loading/empty/error, microcopy N2, foco de teclado e acessibilidade básica.
Arquivos prováveis: `frontend/itam-platform/src/pages/*`, `frontend/itam-platform/src/components/*`, `frontend/itam-platform/src/styles.css`.
O que não mexer: AppShell sem necessidade; CSS global amplo sem screenshot; backend; package-lock.
Critérios de aceite: checklist por rota; screenshots antes/depois; build verde; sem regressão de navegação.
Validações: `npm run build`, smoke manual autenticado, screenshots.
Riscos: refatoração estética sem valor; quebrar classes; aumentar CSS sem controle.
Status recomendado: contínuo, mas depois de UAT-H1 apontar dores reais.

## RELEASE-H1 — production readiness checklist

Tipo: Release / governança
Prioridade: P1
Valor operacional: Evita publicar estado local misto ou inseguro.
Descrição: Consolidar checklist para produção: testes, build, migrations, health/readiness, secrets, CI manual-only, rollback, UAT GO.
Arquivos prováveis: `docs/audit/RELEASE_H1_CHECKLIST.md`, docs de runbook, workflow somente se boundary futura autorizar.
O que não mexer: `git push`, publish Docker, secrets, `.env*`, Docker volumes, assets legacy.
Critérios de aceite: checklist executável; critérios GO/NO-GO; nenhum segredo exposto; untracked classificados ou ignorados conforme decisão.
Validações: compileall, unittest/pytest selecionado, frontend build, docker compose config, health/readiness quando ambiente disponível.
Riscos: release com commits locais não publicados; CI publish indevido; migrations em banco errado.
Status recomendado: depois de UAT-H1 e correções P1.

## IMPORT-UAT-H1 — import-to-asset operational acceptance

Tipo: UAT/importação
Prioridade: P1
Valor operacional: Garante que ativo importado entra no mesmo ciclo operacional do ativo manual.
Descrição: Validar que uma planilha sintética cria/atualiza ativo de forma segura e que o ativo resultante pode ser movimentado e auditado.
Arquivos prováveis: docs UAT/report; fixtures sintéticas se aprovado.
O que não mexer: ImportService validado, normalizers, merge policy, dados reais.
Critérios de aceite: upload, preview, staging, conflitos, apply seguro e consulta do ativo resultante comprovados.
Validações: testes imports existentes, UAT cenários 2 e 9.
Riscos: usar arquivo real; sobrescrever campo crítico; confundir PREVIEW_ONLY com apply.
Status recomendado: embutido em UAT-H1 ou boundary curta derivada.
