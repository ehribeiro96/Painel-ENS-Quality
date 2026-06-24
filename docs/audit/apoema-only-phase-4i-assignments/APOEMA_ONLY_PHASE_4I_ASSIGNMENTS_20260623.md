# Apoema-only Phase 4I — Assignments Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar Assignments legacy para Apoema Movimentações com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /assignments: visão legacy de vínculos no shell raiz.
- /apoema/assignments: inexistente.
- /apoema-preview/assignments: inexistente como rota canônica.
- Apoema Movimentações: inexistente.
- Legacy Assignments: tabela operacional de vínculos atuais.

## 4. Matriz de paridade
Referência: ASSIGNMENTS_PARITY_MATRIX_20260623.md

## 5. Política escolhida
- POLICY_A_SAFE_REDIRECT

## 6. Mudança aplicada
- `/assignments` agora redireciona para `/apoema/assignments`.
- Apoema ganhou a rota canônica `/apoema/assignments`.
- A superfície nova combina vínculos atuais com histórico recente de movimentações.

## 7. O que não foi removido
- Legacy Assignments permanece no repositório.
- AppShell legado permanece disponível para outras rotas legacy.
- `/apoema-preview/*` continua preservado para o mesmo subtree.

## 8. ProtectedRoute
ProtectedRoute continua protegendo o fluxo Apoema e a compatibilidade temporária.

## 9. Login/Auth
Não houve regressão observada no fluxo de autenticação.

## 10. Regressões cruzadas
- /assets: preservado.
- /signatures: preservado.
- /stock: preservado.
- /macros: preservado.
- /imports: preservado.
- /audit-logs: preservado.
- /ai-chat: preservado.
- /apoema/chat: preservado.
- /apoema-preview/chat: preservado.

## 11. Validações
python -m unittest discover -s tests -v: pass (246 tests, 8 skipped)
ruff check backend tests scripts: pass
compileall backend/app backend/alembic tests scripts: pass
frontend build: pass
git diff --check: pass
Commit de código/teste: 0a5143d

## 12. Limitações
O histórico recente depende da disponibilidade real do backend.

## 13. Próxima fase recomendada
Seguir para a próxima superfície legacy com a mesma regra de paridade mínima e alias temporário.
