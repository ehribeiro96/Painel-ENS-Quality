# P0/P1 Security Hardening — 2026-06-23

## 1. Objetivo
Corrigir os achados P0/P1 prioritários da auditoria técnica com mudanças pequenas, seguras e cobertas por testes.

## 2. Itens implementados
| Item | Status | Arquivos | Testes |
|---|---|---|---|
| Apoema AI auth | Implementado | `backend/app/api/v1/routes/ai_chat.py`, `tests/test_ai_chat_api.py`, `tests/test_ai_chat_hardening.py`, `tests/test_apoema_ai_chat_backend.py` | Dependências RBAC e 401 sem token |
| Metrics protection | Implementado | `backend/app/main.py`, `backend/app/core/config/settings.py`, `tests/test_metrics_hardening.py` | 401/503 fora de local |
| Apoema route guard | Implementado | `frontend/itam-platform/src/App.tsx` | Rotas `Apoema` atrás de `ProtectedRoute` |
| JWT secret hardening | Implementado | `backend/app/core/config/settings.py`, `backend/app/core/startup.py`, `tests/test_startup_diagnostics.py` | Rejeição de secret fraco fora de local |
| Docker compose exposure | Implementado | `docker-compose.yml` | Bind local para Postgres/Redis; senha hardcoded removida |
| APP_AUTO_MIGRATE | Implementado | `backend/app/core/config/settings.py`, `.env.example`, `docker-compose.yml` | Default seguro fora de local |
| Menu por role | Implementado | `frontend/itam-platform/src/components/AppShell.tsx` | Links restritos por papel |
| Upload accept | Implementado | `frontend/itam-platform/src/pages/ImportsPage.tsx` | Frontend alinhado ao backend (`.csv`, `.xlsx`) |
| Vite proxy | Implementado | `frontend/itam-platform/vite.config.ts` | Proxy ajustado para `8080` |
| Testes RBAC | Implementado | `tests/test_ai_chat_api.py`, `tests/test_ai_chat_hardening.py`, `tests/test_apoema_ai_chat_backend.py` | Endpoints Apoema incluídos na proteção |

## 3. Segurança
- Secrets:
  - `JWT_SECRET_KEY` fraco passa apenas em local.
  - `METRICS_TOKEN` protege `/metrics` fora de local.
- `.env`:
  - `APP_AUTO_MIGRATE=false` por padrão no exemplo.
  - `METRICS_TOKEN` documentado como placeholder local.
- Metrics:
  - `/metrics` exige token interno fora de local.
- AI endpoints:
  - `GET /api/v1/ai-chat/providers` e `POST /api/v1/ai-chat/message` exigem auth/RBAC.
- Rotas SPA:
  - `/apoema/*` e `/apoema-preview/*` agora exigem autenticação.

## 4. Validações executadas
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`: OK
- `.venv/bin/python -m ruff check backend tests scripts`: OK
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: OK
- `cd frontend/itam-platform && npm run build`: OK
- `docker compose config`: OK
- `git diff --check`: OK

## 5. Limitações
- `/metrics` fora de local depende de `METRICS_TOKEN` configurado.
- `APP_AUTO_MIGRATE` pode ser explicitamente sobrescrito em ambientes não-local; o default foi tornado seguro.

## 6. Próximos itens fora do escopo
- Refatoração ampla do frontend.
- Alterações de migrations.
- Composio real.
- Mudanças de negócio fora da auditoria P0/P1.
