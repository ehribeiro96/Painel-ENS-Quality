# Apoema-only Phase 4A — AI Chat Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar AI Chat legacy para Apoema Chat com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /ai-chat: rota legacy protegida
- /apoema/chat: disponível e protegida
- /apoema-preview/chat: disponível e protegida
- Apoema Chat: possui composer, mensagens, provedores, anexos e fallback explícito
- Legacy AI Chat: permanece no código como compatibilidade histórica

## 4. Matriz de paridade
Referência: `AI_CHAT_PARITY_MATRIX_20260623.md`

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
`/ai-chat` passou a ser um alias protegido que redireciona para `/apoema/chat`, mantendo compatibilidade enquanto a superfície principal fica no Apoema.

## 7. O que não foi removido
- rota legacy `/ai-chat` como compatibilidade
- `AiChatPage` legacy em disco
- AppShell legado para as demais rotas
- rotas `Apoema` existentes

## 8. ProtectedRoute
Preservado. O alias de compatibilidade também passa pelo mesmo guard.

## 9. Login/Auth
Sem regressão observada na validação executada.

## 10. Apoema Chat fallback/auth
Sem regressão observada. `401` e `403` seguem como erro explícito; fallback local continua restrito a rede/offline.

## 11. Validações
Registros consolidados em `apoema-only-phase-4a-ai-chat-gates.log`.

## 12. Limitações
- Não houve push
- Untracked preexistentes permanecem preservados
- Algumas ações avançadas do legacy, como copy/regenerate, seguem como evolução futura do Apoema

## 13. Próxima fase recomendada
Evoluir os detalhes de UX do Apoema Chat restantes e então mapear o próximo módulo legacy seguro para alias/redirect.
