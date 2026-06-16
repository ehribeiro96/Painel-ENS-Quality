# PRODUCT-H1 — Roadmap funcional e técnico

Boundary: `PRODUCT-H1 — roadmap de evolução funcional do Painel ENS-Quality`
Modo: documentação/planejamento. Nenhuma feature implementada nesta boundary.

## Diagnóstico de maturidade funcional

O produto saiu da fase de higiene/auditoria e já possui base real para operação: rotas de ativos, movimentações, macros, imports, AI Chat, audit logs, auth/RBAC, frontend autenticado e legado montado. O fluxo alvo existe em peças funcionais, mas ainda precisa de UAT ponta-a-ponta e polimento operacional antes de ser tratado como MVP diário.

Evidências principais:
- Rotas backend: `backend/app/api/v1/router.py` inclui auth, users, assets, dashboard, imports, signatures, macros, movements macro endpoint, ai_chat, audit e search.
- Fluxo de ativo/movimentação: `backend/app/api/v1/routes/assets.py` expõe `/assets`, `/assets/{id}`, `/assets/{id}/move` e `/assets/{id}/history`.
- Macro pós-movimentação: `backend/app/api/v1/routes/macros.py` expõe `/movements/{movement_id}/suggested-macro`, `/macros/generate` e `/macros/generations/{generation_id}/copied`.
- Persistência/auditoria: `AssetService.move()` cria `AssetMovement`, atualiza `Asset` e grava `AuditAction.MOVE`; `MacroService.generate_for_movement()` cria `MacroGeneration` vinculada e registra auditoria.
- Frontend: `AssetDetailsPage` mostra detalhe/timeline e abre `MoveAssetDialog`; `MoveAssetDialog` chama movimentação, sugestão de macro e cópia; `AuditLogsPage` consulta auditoria.

Conclusão: maturidade `MVP-candidate`, não `release-ready`. A próxima etapa correta é UAT-H1 com cenários sintéticos reais, pois a maior incerteza agora é integração operacional, não arquitetura básica.

## Fase 1 — Consolidação operacional

Objetivo:
- Transformar o fluxo já existente em experiência operacional coerente e verificável, sem mexer em áreas estáveis sem necessidade.

Entregáveis:
- Mapa do fluxo Ativo → Movimentação → Macro → Histórico → Copiar macro → Auditoria.
- Checklist de inconsistências funcionais por rota/tela.
- Evidências de quais dados são reais, quais são derivados e quais são placeholders/UX incompleta.
- Decisão de UAT sintético antes de qualquer feature nova.

Critérios de aceite:
- Stage vazio no início e fim.
- Nenhuma alteração em backend/frontend/migrations/Docker.
- UAT-H1 definido como próxima boundary.
- Lacunas registradas em backlog pequeno.

Riscos:
- Confundir “existe endpoint” com “o operador consegue usar diariamente”.
- Corrigir bug durante planejamento e quebrar regra da boundary.
- Misturar release/push/legacy com evolução funcional.

Arquivos prováveis:
- `docs/product/PRODUCT_H1_*`
- `docs/audit/PRODUCT_H1_EXECUTIVE_SUMMARY.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`

O que não mexer:
- Código funcional, frontend, backend, migrations, Docker, workflow CI, lockfiles e assets.

## Fase 2 — UAT com cenários reais sintéticos

Objetivo:
- Provar o MVP operacional com dados fictícios mas próximos do trabalho N2.

Entregáveis:
- Roteiro UAT com 10 cenários mínimos.
- Massa sintética: ativo manual, ativo importado, usuário N2, usuário destino, planilha válida e planilha inválida.
- Evidências por cenário: screenshots/logs/IDs sem expor segredo ou dado real.
- Matriz GO/NO-GO por cenário.

Critérios de aceite:
- Cenários 1 a 7 passam ou têm bug documentado com repro claro.
- AI Chat é validado como assistivo, sem alteração de dados.
- Permissões são testadas para pelo menos ADMIN/TECHNICIAN/MANAGER quando aplicável.
- Nenhum dado produtivo usado.

Riscos:
- Ambiente local indisponível mascarar bug de produto.
- UAT exigir dados reais indevidamente.
- Falta de filtros de auditoria dificultar evidência.

Arquivos prováveis:
- `docs/product/PRODUCT_H1_UAT_SCENARIOS.md`
- Futuro relatório `docs/audit/UAT_H1_REPORT.md`
- Possíveis fixtures sintéticas em boundary futura, se autorizadas.

O que não mexer:
- ImportService, Ollama provider, CSP legado, Docker volumes e migrations.

## Fase 3 — Ativos e movimentações

Objetivo:
- Endurecer o detalhe do ativo e a criação de movimentação para uso diário.

Entregáveis:
- Correção/polimento do comportamento pós-movimentação se UAT confirmar que a macro fica oculta pelo fechamento do modal.
- Melhor exibição de nomes de usuário/responsável no histórico.
- Estados de loading/error/sucesso claros no detalhe do ativo.
- Validações de consistência status ↔ usuário ↔ localidade preservadas.

Critérios de aceite:
- Movimentação salva uma única vez.
- Histórico atualiza sem refresh manual.
- Antes/depois é legível para operador N2.
- Auditoria `MOVE` existe para cada movimentação.
- Teste backend e build frontend passam em boundary de implementação.

Riscos:
- Quebrar `MoveAssetDialog`, área sensível do fluxo alvo.
- Introduzir retorno de model SQLAlchemy cru sem DTO explícito.
- Alterar idempotência ou imutabilidade de `AssetMovement`.

Arquivos prováveis:
- `backend/app/api/v1/routes/assets.py`
- `backend/app/domains/assets/service.py`
- `backend/app/domains/movements/schemas.py`
- `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`
- `frontend/itam-platform/src/components/MoveAssetDialog.tsx`
- testes de assets/movements.

O que não mexer:
- Import pipeline, IA/Ollama, legacy, Docker, migrations.

## Fase 4 — Macros ITIL e histórico

Objetivo:
- Garantir que a macro oficial seja persistida, auditável, copiável e vinculada ao movimento correto.

Entregáveis:
- UX de macro pós-movimentação robusta.
- Exibição de campos pendentes antes de copiar.
- Evidência clara de `generation_id`, `movement_id`, template e estado `copied`.
- Histórico cruzável: ativo → movimento → macro → auditoria.

Critérios de aceite:
- Macro não é gerada antes da movimentação salva.
- Copiar macro chama endpoint de `copied` e registra auditoria.
- Reabrir/consultar o fluxo permite localizar macro gerada recentemente.
- Template `ativos-atualizar-inventario` continua sendo fonte oficial para movimentação.

Riscos:
- Gerar macro duplicada por retry ou refresh.
- Permitir cópia de macro não persistida.
- Ocultar campos pendentes do operador.

Arquivos prováveis:
- `backend/app/api/v1/routes/macros.py`
- `backend/app/domains/macros/service.py`
- `backend/app/domains/macros/models.py`
- `frontend/itam-platform/src/pages/MacrosPage.tsx`
- `frontend/itam-platform/src/components/MoveAssetDialog.tsx`
- testes de macros/audit.

O que não mexer:
- Templates oficiais sem revisão humana; migrations sem boundary DB; provider IA.

## Fase 5 — IA local assistiva

Objetivo:
- Usar IA para apoiar leitura, revisão e explicação sem executar alterações operacionais.

Entregáveis:
- Prompts/atalhos assistivos: explicar macro, revisar clareza, apontar campos faltantes, sugerir checklist de atendimento.
- Política clara: IA não salva, não movimenta, não aplica import e não altera template sem aprovação humana.
- Tratamento de indisponibilidade do Ollama LAN como status operacional.

Critérios de aceite:
- AI Chat funciona same-origin via backend.
- Provider `ollama-lan` e baseline `qwen3:1.7b-64k` preservados.
- Sanitização `<think>` preservada.
- Nenhum endpoint operacional é chamado pela IA automaticamente.

Riscos:
- Usuário interpretar sugestão de IA como decisão oficial.
- Regressão para mock silencioso.
- Expor IP LAN ou detalhes sensíveis no frontend.

Arquivos prováveis:
- `backend/app/domains/ai_chat/*`
- `backend/app/api/v1/routes/ai_chat.py`
- `frontend/itam-platform/src/pages/AiChatPage.tsx`
- componentes `frontend/itam-platform/src/components/ai-chat/*`

O que não mexer:
- Provider/modelo/sanitização sem boundary AI explícita.

## Fase 6 — Relatórios e dashboards

Objetivo:
- Dar visibilidade operacional sem interferir no fluxo crítico.

Entregáveis:
- Dashboard de ativos por status/tipo/localidade.
- Movimentações recentes com filtros básicos.
- Pendências de importação/conflito.
- Exportação inicial segura, se priorizada.

Critérios de aceite:
- Dashboard usa dados reais do PostgreSQL.
- Não executa ações destrutivas.
- Export não vaza campos sensíveis além do necessário.
- Performance aceitável para volume operacional inicial.

Riscos:
- Criar métricas bonitas mas irrelevantes para N2.
- Exportar dados pessoais sem regra.
- Consultas sem paginação/filtros pesarem no banco.

Arquivos prováveis:
- `backend/app/api/v1/routes/dashboard.py`
- `backend/app/domains/dashboard/service.py`
- `frontend/itam-platform/src/pages/DashboardPage.tsx`
- possíveis docs de relatório.

O que não mexer:
- Fluxo de movimentação/macro durante dashboard; Docker volumes; migrations sem plano.

## Fase 7 — Release/produção

Objetivo:
- Sair de validação local para pacote operacional publicável com checklist conservador.

Entregáveis:
- Checklist release: backend tests, frontend build, migrations check, Docker compose config, health/readiness, CSP/legacy smoke, AI Chat smoke opcional.
- Decisão sobre push pendente fora desta boundary.
- Política de rollback.
- Release notes com do-not-touch e riscos conhecidos.

Critérios de aceite:
- Stage limpo ou stage explicitamente allowlisted.
- Sem secrets em docs/logs/artefatos.
- CI manual-only preservado até decisão de publish.
- UAT-H1 GO ou riscos aceitos formalmente.

Riscos:
- Publicar worktree com untracked indevidos.
- Misturar release com limpeza de legado/assets.
- Rodar migrations no banco errado.

Arquivos prováveis:
- `docs/audit/*RELEASE*`
- workflow CI apenas em boundary dedicada.
- scripts de validação apenas se aprovados.

O que não mexer:
- `git push`, GitHub Actions publish, Docker volumes, secrets, `.env*`, assets legados sem decisão humana.
