# Apoema-only Phase 4F — Macros Migration — 2026-06-23

## 1. Status
GO

## 2. Objetivo
Migrar Macros legacy para Apoema Macros ITIL com paridade mínima comprovada, sem remover compatibilidade.

## 3. Estado antes
- /macros: rota legacy sob shell antigo.
- /apoema/macros: experiência Apoema adicionada.
- /apoema-preview/macros: coberta pelo alias do preview.
- Apoema Macros ITIL: nova superfície Apoema.
- Legacy Macros: mantido apenas como compatibilidade temporária.

## 4. Matriz de paridade
Referência: MACROS_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
`/macros` foi promovido para alias compatível com `/apoema/macros`, e a experiência de macros passou a viver dentro do shell Apoema.

## 7. O que não foi removido
- Shell legado.
- Rotas legacy restantes.
- Fluxo real de consulta, geração, preview e cópia.

## 8. ProtectedRoute
Preservado.

## 9. Login/Auth
Sem regressão observada nos contratos existentes.

## 10. Regressões cruzadas
- /imports: preservado.
- /audit-logs: preservado.
- /assets: preservado.
- /assets/:id: preservado.
- /ai-chat: preservado como alias Apoema.

## 11. Validações
Pendentes de execução nesta etapa.

## 12. Limitações
Controle de papel segue aplicado no próprio page component do Apoema Macros ITIL.

## 13. Próxima fase recomendada
Consolidar as últimas superfícies legacy restantes que tenham paridade comprovada.
