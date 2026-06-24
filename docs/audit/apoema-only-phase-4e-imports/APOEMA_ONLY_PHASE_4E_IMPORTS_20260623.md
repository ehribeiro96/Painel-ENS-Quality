# Apoema-only Phase 4E — Imports Migration — 2026-06-23

## 1. Status
GO

## 2. Objetivo
Migrar Imports legacy para Apoema Imports com paridade mínima comprovada, sem remover compatibilidade.

## 3. Estado antes
- /imports: rota legacy com shell antigo.
- /apoema/imports: experiência Apoema adicionada.
- /apoema-preview/imports: coberta pelo alias do preview.
- Apoema Imports: nova superfície Apoema.
- Legacy Imports: mantido apenas como compatibilidade temporária.

## 4. Matriz de paridade
Referência: IMPORTS_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
`/imports` foi promovido para alias compatível com `/apoema/imports`, e a experiência operacional passou a viver dentro do shell Apoema.

## 7. O que não foi removido
- Shell legado.
- Rotas legacy restantes.
- Fluxo real de upload, preview, staging, validação, aplicação e cancelamento.

## 8. ProtectedRoute
Preservado.

## 9. Login/Auth
Sem regressão observada nos contratos existentes.

## 10. Regressões cruzadas
- /assets: preservado.
- /assets/:id: preservado.
- /ai-chat: preservado como alias Apoema.
- /apoema/chat: preservado.
- /apoema-preview/chat: preservado pelo bloco preview.

## 11. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`: OK
- `.venv/bin/python -m ruff check backend tests scripts`: OK
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: OK
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`: OK
- `git diff --check`: OK
- Smoke HTTP em `127.0.0.1:18086` e `127.0.0.1:18087`: OK

## 12. Limitações
Dependências preexistentes de preview e roteamento nested continuam sendo tratadas como compatibilidade temporária.

## 13. Próxima fase recomendada
Consolidar as últimas superfícies legacy restantes que tenham paridade comprovada.
