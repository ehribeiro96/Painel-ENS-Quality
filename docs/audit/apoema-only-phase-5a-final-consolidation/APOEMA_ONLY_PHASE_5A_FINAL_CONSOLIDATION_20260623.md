# Apoema-only Phase 5A — Final Consolidation Audit — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Auditar a consolidação Apoema-only depois das migrações 4A-4K, sem remover legado.

## 3. Sumário executivo
- Frontend alvo: Apoema
- Rotas Apoema canônicas: /apoema, /apoema/*, /apoema-preview, /apoema-preview/*, /login
- Rotas legacy que viraram alias: /ai-chat, /assets, /assets/:id, /audit-logs, /imports, /macros, /stock, /signatures, /assignments, /users, /users/:id, /settings, /
- Rotas legacy ainda ativas: nenhuma na árvore de rotas atual
- AppShell legado: ainda presente no código, sem rota legacy ativa atualmente
- CSS global: presente e com risco moderado/alto por seletores genéricos compartilhados
- Componentes candidatos a remoção futura: AppShell e as páginas legacy em src/pages exceto Login/NotFound
- Riscos restantes: CSS global compartilhado, AppShell ainda importado como boundary, ausência de smoke browser nesta fase, legado externo /assinaturas no link do shell

## 4. Rotas
Veja `remaining-legacy-routes.tsv`.

## 5. AppShell legado
Veja `remaining-appshell-dependencies.tsv`.

## 6. Componentes legacy remanescentes
Veja `remaining-legacy-components.tsv`.

## 7. CSS e risco visual
`frontend/itam-platform/src/styles.css` continua importado globalmente em `src/main.tsx`. Ele ainda contém seletores amplos e utilitários compartilhados como `.shell`, `.sidebar`, `.main`, `.topbar`, `.toolbar`, `.content`, `.grid`, `.search-results`, `.table-*` e estados de loading/empty. O `apoema.css` isola a experiência Apoema visualmente, mas o CSS global ainda pode interferir em formulários, tabelas, busca e layout do shell legado. Os estilos que devem permanecer globais por enquanto são variáveis de tema, utilitários de layout e blocos compartilhados. A remoção de CSS legacy agora teria risco alto e precisa de visual QA completo.

## 8. Imports/dependências
Os imports mostram que `App.tsx` só carrega `LoginPage`, `NotFoundPage`, `ApoemaApp`, `AppShell` e `RouteLoading`; as páginas legacy em `src/pages/*.tsx` não são importadas pelo runtime, exceto `LoginPage` e `NotFoundPage`. `AppShell` permanece como wrapper de legacy route, mas a lista `legacyCompatibilityRoutes` está vazia. O risco principal é a permanência de componentes mortos em disco e o acoplamento histórico em testes e documentação.

## 9. Segurança frontend
Não foram encontradas chamadas diretas a provider em `frontend/itam-platform/src/apoema`. Também não apareceu segredo real nos scans textuais feitos nesta fase. O front usa a API central e o `Settings` atual é leitura/visual seguro.

## 10. Cobertura de testes
Existem contratos para as rotas migradas (`test_apoema_*_parity_contract.py`), boundary do shell (`test_apoema_shell_boundary_contract.py`, `test_apoema_legacy_surface_contract.py`, `test_apoema_only_route_contract.py`), login (`test_login_frontend_contract.py`) e regressão de chamadas diretas/erro de IA (`test_apoema_frontend_error_contract.py`, `test_apoema_ai_chat_parity_contract.py`). O que falta antes de remover componentes legacy é um smoke browser focado em redirects reais, uma verificação visual de que o shell legado não aparece mais em nenhum fluxo e uma validação de que a remoção de `AppShell` e páginas legacy não quebra a navegação por favoritos/links externos.

## 11. Smoke HTTP
Executado com Vite em `127.0.0.1:18086`. As rotas canônicas e os aliases retornaram `200 OK` com a SPA do Vite, incluindo `/`, `/login`, `/apoema`, `/apoema/chat`, `/apoema/assets`, `/apoema/assets/123`, `/apoema/audit-logs`, `/apoema/imports`, `/apoema/macros`, `/apoema/stock`, `/apoema/signatures`, `/apoema/assignments`, `/apoema/users`, `/apoema/users/123`, `/apoema/settings` e os aliases legacy equivalentes.

## 12. O que está pronto para fase futura de remoção
Alias de rota para `/ai-chat`, `/assets`, `/assets/:id`, `/audit-logs`, `/imports`, `/macros`, `/stock`, `/signatures`, `/assignments`, `/users`, `/users/:id` e `/settings`.

## 13. O que NÃO pode ser removido ainda
`/login`, `/apoema`, `/apoema/*`, `/apoema-preview`, `/apoema-preview/*`, `LoginPage`, `NotFoundPage`, o CSS global e a boundary de AppShell enquanto não houver validação browser/visual específica.

## 14. Plano recomendado para Fase 5B
Remover apenas aliases com cobertura completa de contrato e smoke. Em seguida retirar componentes legacy não roteados, reduzir `AppShell`, isolar CSS legacy e terminar com uma auditoria visual final antes de qualquer checklist pré-push.

## 15. Validações
A fase roda `unittest`, `ruff`, `compileall`, `npm run build` e `git diff --check`. O smoke HTTP fica como validação recomendada adicional.

## 16. Limitações
Esta auditoria não remove nada. O estado final ainda depende de compatibilidade histórica, do shell legado, de CSS global compartilhado e de validação browser para remoção futura.
