# Apoema-only Phase 4C — Asset Detail Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar detalhe e ações de ativos legacy para Apoema com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- `/assets`: compatibilidade já apontando para Apoema Ativos.
- `/assets/:id`: detalhe ainda preso ao shell legacy.
- `/apoema/assets`: console de ativos já validado.
- `/apoema/assets/:id`: rota canônica criada nesta fase.
- `/apoema-preview/assets`: preservado.
- `/apoema-preview/assets/:id`: alias preservado.
- Apoema Detalhe: inexistente antes desta fase.
- Legacy Asset Detail: ainda existia como rota antiga.

## 4. Matriz de paridade
Referência: `ASSET_DETAIL_PARITY_MATRIX_20260623.md`

## 5. Política escolhida
- `POLICY_A_SAFE_DYNAMIC_REDIRECT`

## 6. Mudança aplicada
`/assets/:id` agora redireciona para `/apoema/assets/:id`, e o detalhe canônico foi exposto dentro do `ApoemaApp`.

## 7. O que não foi removido
- `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- rotas legacy restantes do shell antigo

## 8. ProtectedRoute
O detalhe novo continua protegido.

## 9. Login/Auth
Sem regressão observada nesta fase.

## 10. Regressões cruzadas
- `/assets`: continua apontando para Apoema Ativos.
- `/ai-chat`: continua apontando para Apoema Chat.
- `/apoema/chat`: preservado.
- `/apoema-preview/chat`: preservado.

## 11. Validações
Pendentes de execução.

## 12. Limitações
O detalhamento usa a API existente; a interface local do Apoema segue como console principal de navegação.

## 13. Próxima fase recomendada
Migrar a superfície legada restante apenas se houver equivalente claro no Apoema.
