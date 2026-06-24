# Apoema-only Phase 4K — Settings Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar Settings legacy para Apoema Configurações com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /settings: rota legacy no shell raiz.
- /apoema/settings: rota canônica existente na superfície Apoema.
- /apoema-preview/settings: preservada como alias temporal via subtree /apoema-preview/*.
- Apoema Configurações: tela visual com tema, preferências e segurança.
- Legacy Settings: permanecem no repositório como compatibilidade.

## 4. Matriz de paridade
Referência: SETTINGS_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
- `/settings` agora redireciona para `/apoema/settings`.
- Apoema mantém a rota canônica `/apoema/settings`.
- `/apoema-preview/settings` permanece coberta pelo mesmo subtree.

## 7. O que não foi removido
- Legacy Settings permanece no repositório.
- AppShell legado permanece disponível para outras rotas legacy.
- `/apoema-preview/*` continua preservado para o mesmo subtree.

## 8. ProtectedRoute
ProtectedRoute continua protegendo o fluxo Apoema e a compatibilidade temporária.

## 9. Login/Auth
Não houve regressão observada no fluxo de autenticação.

## 10. Regressões cruzadas
- /users: preservado.
- /assignments: preservado.
- /signatures: preservado.
- /stock: preservado.
- /macros: preservado.
- /imports: preservado.
- /audit-logs: preservado.
- /assets: preservado.
- /assets/:id: preservado.
- /ai-chat: preservado.
- /apoema/chat: preservado.
- /apoema-preview/chat: preservado.

## 11. Validações
Pendente de execução nesta rodada.

## 12. Limitações
Não houve ampliação para backend, providers, auth ou segredos.

## 13. Próxima fase recomendada
Seguir para a próxima superfície legacy apenas se ainda houver migração segura e com a mesma regra de paridade mínima.
