# Apoema-only Phase 4G — Stock Migration — 2026-06-23

## 1. Status
GO

## 2. Objetivo
Migrar Stock legacy para Apoema Estoque com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /stock: rota legacy sob compatibilidade.
- /apoema/stock: superfície Apoema criada nesta fase.
- /apoema-preview/stock: coberta pelo alias do preview.
- Apoema Estoque: superfície canônica para a operação.
- Legacy Stock: mantido como compatibilidade temporária.

## 4. Matriz de paridade
Referência: STOCK_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
`/stock` passou a apontar para `/apoema/stock`, e o conteúdo de estoque foi exposto dentro da experiência Apoema sem chamar provider direto.

## 7. O que não foi removido
- Shell legado.
- Rotas legacy restantes.
- Página legacy de stock no disco para compatibilidade.

## 8. ProtectedRoute
Preservado.

## 9. Login/Auth
Sem regressão observada nos contratos existentes.

## 10. Regressões cruzadas
- /macros: preservado.
- /imports: preservado.
- /audit-logs: preservado.
- /assets: preservado.
- /assets/:id: preservado.
- /ai-chat: preservado como alias Apoema.
- /apoema/chat: preservado.
- /apoema-preview/chat: preservado.

## 11. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` passou.
- `.venv/bin/python -m ruff check backend tests scripts` passou.
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` passou.
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` passou.
- `git diff --check` passou.
- Smoke HTTP em `127.0.0.1:18088` respondeu `200` para `/`, `/apoema`, `/apoema/stock`, `/apoema-preview/stock`, `/stock`, `/macros`, `/imports`, `/audit-logs`, `/assets`, `/assets/123`, `/ai-chat` e `/login`.

## 12. Limitações
A visão de estoque continua sendo um resumo operacional baseado em `assetsByStatus`; não houve expansão para um módulo transacional novo.

## 13. Próxima fase recomendada
Consolidar a próxima superfície legacy com a mesma política de alias seguro, se houver paridade comprovada.
