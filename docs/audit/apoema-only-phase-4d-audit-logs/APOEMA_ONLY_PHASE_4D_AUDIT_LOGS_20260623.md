# Apoema-only Phase 4D — Audit Logs Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar Audit Logs legacy para Apoema Logs de Auditoria com paridade comprovada, sem remover compatibilidade.

## 3. Estado antes
- /audit-logs: rota legacy no shell antigo.
- /apoema/audit-logs: criada nesta fase.
- /apoema-preview/audit-logs: preservada via alias do subtree Apoema.
- Apoema Logs de Auditoria: inexistente antes desta fase.
- Legacy Audit Logs: mantido como compatibilidade temporária.

## 4. Matriz de paridade
Referência: `AUDIT_LOGS_PARITY_MATRIX_20260623.md`

## 5. Política escolhida
- `POLICY_A_SAFE_REDIRECT`

## 6. Mudança aplicada
`/audit-logs` agora redireciona para `/apoema/audit-logs`, e o módulo canônico de auditoria passou a viver no `ApoemaApp`.

## 7. O que não foi removido
- `frontend/itam-platform/src/pages/AuditLogsPage.tsx`
- rotas legacy restantes do shell antigo

## 8. ProtectedRoute
O alias e a rota canônica continuam protegidos.

## 9. Login/Auth
Sem regressão observada nesta fase.

## 10. Regressões cruzadas
- `/assets`: continua apontando para Apoema Ativos.
- `/assets/:id`: continua apontando para Apoema Detalhe.
- `/ai-chat`: continua apontando para Apoema Chat.
- `/apoema/chat`: preservado.
- `/apoema-preview/chat`: preservado.

## 11. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` - PASS
- `.venv/bin/python -m ruff check backend tests scripts` - PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` - PASS
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` - PASS
- `git diff --check` - PASS
- Smoke HTTP em `http://127.0.0.1:18086` - PASS

## 12. Limitações
O conjunto de filtros e paginação segue o contrato da API existente; a migração aqui é de rota e superfície, não de backend.

## 13. Próxima fase recomendada
Continuar migrando as superfícies legacy remanescentes apenas onde houver equivalente claro e estável em Apoema.
