# Apoema-only Phase 1 - 2026-06-23

## 1. Status
GO

## 2. Objetivo
Tornar o Apoema a superfície principal sem remover legados.

## 3. Decisão de rota
- `/`: redirect para `/apoema`
- `/apoema`: Apoema protegido e principal
- `/apoema-preview`: alias temporário protegido
- Rotas antigas: preservadas como compatibilidade temporária

## 4. O que mudou
- `frontend/itam-platform/src/App.tsx` passou a redirecionar a raiz para `/apoema`
- `ApoemaRoute` foi introduzido para centralizar a superfície principal protegida
- `tests/test_apoema_only_route_contract.py` foi adicionado para travar o contrato estático
- `tests/test_login_frontend_contract.py` foi atualizado para o novo roteamento Apoema-first

## 5. O que não mudou
- Backend
- Docker
- Migrations
- RBAC
- Contratos de API
- Frontends antigos
- Assets legados

## 6. ProtectedRoute
Preservado. Apoema continua protegido pelo mesmo fluxo de autenticação.

## 7. Login/Auth
Sem regressão observada. A suíte completa passou, incluindo o contrato de login frontend.

## 8. Apoema Chat fallback/auth
Sem regressão observada. O contrato de erro do Apoema e o build frontend continuam passando.

## 9. Rotas legacy preservadas
- `/ai-chat`
- `/assets`
- `/assets/:id`
- `/users`
- `/users/:id`
- `/assignments`
- `/stock`
- `/imports`
- `/macros`
- `/signatures`
- `/audit-logs`
- `/settings`

## 10. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` - PASS
- `.venv/bin/python -m ruff check backend tests scripts` - PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` - PASS
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` - PASS

## 11. Limitações
- Sem push nesta fase
- Untracked preexistentes preservados fora do escopo
- Smoke HTTP/browser não foi necessário para esta etapa

## 12. Próxima fase
Consolidar a remoção gradual da dependência do shell raiz legado, mantendo compatibilidade até a migração completar.
