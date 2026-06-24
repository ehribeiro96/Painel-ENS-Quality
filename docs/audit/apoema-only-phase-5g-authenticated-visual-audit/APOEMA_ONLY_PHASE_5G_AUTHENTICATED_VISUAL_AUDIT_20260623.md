# Apoema-only Phase 5G — Authenticated Visual Audit — 2026-06-23

## 1. Status
PARTIAL-GO

## 2. Objetivo
Auditoria visual autenticada do Apoema com sessão UAT/local segura, sem vazar credenciais.

## 3. Estado antes
- Fase 5F: PARTIAL-GO por ausência de sessão segura.
- Limitação anterior: rotas protegidas só puderam ser avaliadas via redirect de login.
- Auth mode: NO_AUTH_AVAILABLE.

## 4. Segurança de autenticação
- StorageState: ausente.
- Credenciais: ausentes.
- Sessão/cabeçalhos: não exportados nem registrados.
- Secrets: não encontrados.

## 5. Ambiente
- Porta Vite: 18094.
- Backend: disponível em 127.0.0.1:8080 e 172.18.0.1:8080.
- Playwright: disponível via npx/playwright.
- Viewports: 390x844, 768x1024, 1366x768, 1440x900, 1920x1080.
- Rotas auditadas: /, /login, /apoema, /apoema/chat, /apoema/assets, /apoema/assets/123, /apoema/audit-logs, /apoema/imports, /apoema/macros, /apoema/stock, /apoema/signatures, /apoema/assignments, /apoema/users, /apoema/users/123, /apoema/settings, /apoema-preview, /apoema-preview/chat.

## 6. Sumário executivo visual autenticado
A sessão segura não estava disponível. O baseline visual abriu corretamente e o login renderizou, mas todas as rotas protegidas voltaram para /login. Não houve P0/P1 visuais nem erros de console ou page error.

## 7. Matriz por rota
Referência: authenticated-visual-route-matrix.tsv

## 8. Findings visuais autenticados
Referência: authenticated-visual-findings.tsv

## 9. Screenshots autenticados
Não houve screenshots autenticados. Foram criadas capturas baseline sem sessão segura para documentar o estado de redirecionamento.

## 10. Chat autenticado
Não executado sem sessão segura.

## 11. Ativos e detalhe
Não executado sem sessão segura; redirecionou para login.

## 12. Movimentações e Macros
Não executado sem sessão segura; redirecionou para login.

## 13. Usuários e detalhe
Não executado sem sessão segura; redirecionou para login.

## 14. Configurações
Não executado sem sessão segura; redirecionou para login.

## 15. Mobile autenticado
GO_WITH_RESERVATION no baseline de login; sem sessão segura para validar conteúdo protegido.

## 16. Desktop autenticado
GO_WITH_RESERVATION no baseline de login; sem sessão segura para validar conteúdo protegido.

## 17. Console/runtime
Sem console errors e sem page errors nos testes de navegador.

## 18. Segurança frontend
Nenhum provider direto foi encontrado. O scan encontrou apenas usos legítimos de token/secret/password em código e testes, e arquivos .env.example já versionados.

## 19. Validações
Todos os gates técnicos executados passaram. O smoke visual autenticado não foi executado porque não havia auth segura.

## 20. Limitações
Sem AUTH_MODE válido, sem storageState seguro e sem credenciais UAT locais. A auditoria autenticada não pôde ser concluída.

## 21. Próxima fase recomendada
Fornecer uma sessão segura temporária fora do repositório, então repetir a captura autenticada para as rotas protegidas.
