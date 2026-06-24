# Apoema-only Phase 5F — Final Visual Audit — 2026-06-23

## 1. Status
PARTIAL-GO

## 2. Objetivo
Auditoria visual final pós-redução de CSS, sem nova remoção estrutural.

## 3. Estado antes
- CSS global: reduzido parcialmente na Fase 5E, ainda presente como base mínima.
- AppShell: ausente.
- Páginas legacy: ausentes.
- Rotas canônicas: presentes.
- Aliases legacy: ausentes do `App.tsx`.

## 4. Ambiente
- Porta Vite: 18093
- Playwright: disponível
- Viewports: 390x844, 768x1024, 1366x768, 1440x900, 1920x1080
- Rotas auditadas: /, /login, /apoema, /apoema/chat, /apoema/assets, /apoema/assets/123, /apoema/audit-logs, /apoema/imports, /apoema/macros, /apoema/stock, /apoema/signatures, /apoema/assignments, /apoema/users, /apoema/users/123, /apoema/settings, /apoema-preview, /apoema-preview/chat

## 5. Sumário executivo visual
A auditoria encontrou um bloqueio real de renderização no primeiro passo: o `App.tsx` usava um componente wrapper inválido dentro de `<Routes>`, o que deixava a UI em tela vazia. Corrigi isso de forma mínima, trocando o wrapper por um `Fragment` direto dentro de `<Routes>`, e refiz a coleta.

Depois da correção, a superfície de login renderizou corretamente em desktop e mobile, com hierarquia legível, cards estáveis e sem overflow crítico. Como não havia credencial UAT segura disponível, todas as rotas protegidas retornaram ao login. Isso limita a auditoria visual às rotas públicas e ao comportamento de gate.

## 6. Matriz por rota
Referência: `visual-route-matrix.tsv`

## 7. Findings visuais
Referência: `visual-findings.tsv`

## 8. Screenshots
Capturas reais foram geradas em `screenshots/` e contact sheets em `contact-sheet-*.jpg`. A inspeção manual confirmou o login em desktop e mobile sem quebra grosseira de layout.

## 9. Login
GO. A tela de login ficou legível em desktop e mobile, com card principal, hero lateral em desktop e stack em mobile. O banner de backend indisponível apareceu de forma explícita quando a sessão não pôde ser restaurada.

## 10. Apoema desktop
GO_WITH_RESERVATION. O caminho protegido redireciona para login por falta de credencial segura, então a experiência principal do Apoema não pôde ser revisada autenticada nesta rodada.

## 11. Apoema mobile
GO. O layout do login em 390x844 permaneceu utilizável, sem overflow horizontal severo e sem colapso visual.

## 12. Chat
GO_WITH_RESERVATION. O roteamento de chat está estável, mas a tela real não foi atingida sem sessão autenticada.

## 13. Tabelas/listas
GO_WITH_RESERVATION. As superfícies de listas protegidas não foram alcançadas por falta de autenticação segura.

## 14. Detalhes de ativo/usuário
GO_WITH_RESERVATION. As rotas existem e redirecionam para o login sem crash, mas o conteúdo real não ficou acessível nesta execução.

## 15. Configurações
GO_WITH_RESERVATION. A rota carrega o gate corretamente, mas a página autenticada não foi aberta sem credenciais.

## 16. Console/runtime
Sem erros JS críticos após o ajuste do `App.tsx`. As falhas observadas no navegador foram requisições de refresh abortadas pelo fluxo de navegação e não indicam regressão visual.

## 17. Segurança frontend
Nenhuma chamada direta a provider foi encontrada. Nenhum secret real foi identificado.

## 18. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` PASS
- `.venv/bin/python -m ruff check backend tests scripts` PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` PASS
- `npm run build` PASS
- `git diff --check` PASS

## 19. Limitações
Não havia credencial UAT segura nem sessão autenticada reaproveitável. Por isso, o conteúdo protegido ficou limitado ao comportamento de gate para login.

## 20. Próxima fase recomendada
Se o objetivo for revisar o Apoema pós-login de ponta a ponta, a próxima boundary correta é restaurar uma sessão UAT segura ou um caminho de autenticação local controlado e refazer a mesma matriz visual autenticada.
