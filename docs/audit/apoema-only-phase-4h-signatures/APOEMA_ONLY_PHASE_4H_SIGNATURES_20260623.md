# Apoema-only Phase 4H — Signatures Migration — 2026-06-23

## 1. Status
GO

## 2. Objetivo
Migrar Signatures legacy para Apoema Assinaturas com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /signatures: rota legacy sob compatibilidade.
- /apoema/signatures: superfície Apoema criada nesta fase.
- /apoema-preview/signatures: coberta pelo alias do preview.
- Apoema Assinaturas: superfície canônica para geração e preview.
- Legacy Signatures: mantido como compatibilidade temporária.

## 4. Matriz de paridade
Referência: SIGNATURES_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
`/signatures` passou a apontar para `/apoema/signatures`, e o fluxo de assinatura foi exposto dentro da experiência Apoema sem chamar provider direto.

## 7. O que não foi removido
- Shell legado.
- Rotas legacy restantes.
- Página legacy de assinatura no disco para compatibilidade.

## 8. ProtectedRoute
Preservado.

## 9. Login/Auth
Sem regressão observada nos contratos existentes.

## 10. Regressões cruzadas
- /stock: preservado.
- /macros: preservado.
- /imports: preservado.
- /audit-logs: preservado.
- /assets: preservado.
- /assets/:id: preservado.
- /ai-chat: preservado como alias Apoema.
- /apoema/chat: preservado.
- /apoema-preview/chat: preservado.

## 11. Validações
Executadas nesta fase após a migração.

## 12. Limitações
A experiência de assinatura segue sendo baseada em preview HTML; não houve expansão para um fluxo transacional novo.

## 13. Próxima fase recomendada
Consolidar a próxima superfície legacy com a mesma política de alias seguro, se houver paridade comprovada.
