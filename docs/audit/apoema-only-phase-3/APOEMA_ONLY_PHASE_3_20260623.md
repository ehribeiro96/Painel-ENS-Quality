# Apoema-only Phase 3 — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Reduzir a superfície legacy remanescente sem remover compatibilidade.

## 3. Estado antes
- Apoema-first: ativo
- Legacy compatibility: ativo
- Shell legado: preservado
- Rotas legacy: preservadas

## 4. Mudança aplicada
`App.tsx` passou a declarar a superfície legacy como uma lista estruturada de rotas com metadados de migração para Apoema, mantendo o `AppShell` apenas no boundary legado.

## 5. Boundary legacy compatibility
As rotas antigas continuam funcionando sob uma superfície explícita de compatibilidade temporária. A composição de `App.tsx` ficou separada entre Apoema-first, compatibilidade legacy e fallback not found.

## 6. Mapa de migração legacy -> Apoema
- `/assets` -> `apoema:assets`
- `/assets/:id` -> `apoema:assets`
- `/users` -> `apoema:users`
- `/users/:id` -> `apoema:users`
- `/assignments` -> `apoema:movements`
- `/stock` -> `apoema:stock`
- `/imports` -> `apoema:imports`
- `/macros` -> `apoema:macros`
- `/ai-chat` -> `apoema:chat`
- `/signatures` -> `apoema:signatures`
- `/audit-logs` -> `apoema:audit-logs`
- `/settings` -> `apoema:settings`

## 7. O que não foi removido
- rotas legacy
- `AppShell`
- `ProtectedRoute`
- `RouteLoading`
- lazy loading/Suspense
- Apoema chat fallback/auth

## 8. ProtectedRoute
Preservado. O Apoema continua protegido e a superfície legacy mantém a guarda atual.

## 9. Login/Auth
Sem regressão observada. A suíte completa passou.

## 10. Apoema Chat fallback/auth
Sem regressão observada. A suíte completa passou.

## 11. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` - PASS
- `.venv/bin/python -m ruff check backend tests scripts` - PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` - PASS
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` - PASS
- `git diff --check` - PASS

## 12. Limitações
- Não houve push
- Untracked preexistentes permanecem preservados
- A superfície legacy continua existindo por compatibilidade temporária

## 13. Próxima fase recomendada
Continuar migrando módulos legacy já mapeados para superfícies Apoema equivalentes antes de considerar qualquer remoção de rota.
