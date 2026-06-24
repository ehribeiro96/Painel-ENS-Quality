# Apoema-only Phase 4J — Users Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar Users legacy para Apoema Usuários com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /users: rota legacy no shell raiz.
- /apoema/users: rota canônica criada na superfície Apoema.
- /apoema-preview/users: preservada como alias temporal via subtree /apoema-preview/*.
- Apoema Usuários: superfície Base44 com lista, busca, formulário e detalhe.
- Legacy Users: permanecem no repositório como compatibilidade.

## 4. Matriz de paridade
Referência: USERS_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
- `/users` agora redireciona para `/apoema/users`.
- `/users/:id` agora redireciona para `/apoema/users/:id`.
- Apoema ganhou a rota canônica `/apoema/users` e o detalhe `/apoema/users/:id`.

## 7. O que não foi removido
- Legacy Users permanece no repositório.
- AppShell legado permanece disponível para outras rotas legacy.
- `/apoema-preview/*` continua preservado para o mesmo subtree.

## 8. ProtectedRoute
ProtectedRoute continua protegendo o fluxo Apoema e a compatibilidade temporária.

## 9. Login/Auth
Não houve regressão observada no fluxo de autenticação. A suíte de contratos e o smoke HTTP permaneceram verdes.

## 10. Regressões cruzadas
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
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`: pass (254 tests, 8 skipped)
- `.venv/bin/python -m ruff check backend tests scripts`: pass
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: pass
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`: pass
- `git diff --check`: pass
- Smoke HTTP em `http://127.0.0.1:18086`: pass
- Commit de código/teste: 859efa5

## 12. Limitações
O histórico recente depende da disponibilidade real do backend.

## 13. Próxima fase recomendada
Seguir para a próxima superfície legacy com a mesma regra de paridade mínima e alias temporário.
