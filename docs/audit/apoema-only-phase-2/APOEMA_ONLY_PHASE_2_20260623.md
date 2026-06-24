# Apoema-only Phase 2 - 2026-06-23

## 1. Status
GO

## 2. Objetivo
Reduzir dependência do shell raiz legado sem remover rotas antigas.

## 3. Estado antes
- `/`: redirect para `/apoema`
- `/apoema`: superfície principal protegida
- `/apoema-preview`: alias temporário protegido
- shell legado: ainda ativo para compatibilidade
- rotas legacy: preservadas

## 4. Mudança aplicada
- `App.tsx` foi reorganizado em blocos explícitos de `ApoemaRoutes` e `LegacyRoutes`
- `LegacyShellRoute` passou a nomear com clareza o shell antigo
- a composição principal agora expressa a separação entre entrada Apoema-first e compatibilidade temporária
- o contrato de boundary ganhou um teste estático novo

## 5. Boundary Apoema-first
- `/`
- `/apoema`
- `/apoema-preview`
- login
- fallback/not found

## 6. Boundary Legacy compatibility
- `/assets`
- `/assets/:id`
- `/users`
- `/users/:id`
- `/assignments`
- `/stock`
- `/imports`
- `/macros`
- `/ai-chat`
- `/signatures`
- `/audit-logs`
- `/settings`

## 7. O que não foi removido
- rotas legacy
- shell legacy
- AppShell
- ProtectedRoute
- Lazy loading/Suspense
- Apoema chat fallback/auth

## 8. ProtectedRoute
Preservado. Apoema continua protegido e o shell legado continua com o mesmo guard.

## 9. Login/Auth
Sem regressão observada. O contrato de login frontend passou junto com a suíte completa.

## 10. Apoema Chat fallback/auth
Sem regressão observada. O contrato de erro do Apoema continua intacto e o build frontend passou.

## 11. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` - PASS
- `.venv/bin/python -m ruff check backend tests scripts` - PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` - PASS
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` - PASS
- `git diff --check` - PASS

## 12. Limitações
- Não houve push
- Untracked preexistentes permaneceram preservados
- Shell legado ainda existe por boundary temporária

## 13. Próxima fase recomendada
Continuar removendo dependências visuais e de navegação que ainda apontam para o shell antigo, sem apagar rotas até a migração ter paridade completa.
