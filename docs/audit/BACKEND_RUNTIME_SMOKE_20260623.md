# Backend Runtime Smoke — 2026-06-23

## 1. Status
PARTIAL-GO

## 2. Contexto
Último release readiness:
- 5bcbebc docs(audit): add local release readiness report

## 3. Runtime
- Comando backend: `.venv/bin/python run.py`
- Porta: `8080`
- Dependências: Postgres e Redis via Docker Compose
- Backend subiu: sim
- Backend encerrado: sim, após o smoke

Observações de ambiente:
- `127.0.0.1:8080` permaneceu inacessível no WSL durante as tentativas de smoke.
- A mesma API respondeu pela bridge local do Docker em `172.18.0.1:8080`.
- O backend foi iniciado sem alterar código, usando overrides de ambiente somente para runtime local:
  - `ENVIRONMENT=staging`
  - `APP_STARTUP_CHECKS=false`
  - `APP_AUTO_MIGRATE=false`
  - `APP_HOST=0.0.0.0`
  - `DATABASE_URL` e `REDIS_URL` apontando para os IPs dos containers locais do Compose

## 4. Health
| Endpoint | Status | Observação |
|---|---|---|
| `/health` | 200 OK | Respondeu em `172.18.0.1:8080`; `127.0.0.1` timeout no WSL. |
| `/health/ready` | 200 OK | Respondeu com `postgres`, `redis`, `frontend_ready` e migrations OK. |

## 5. AI Chat auth smoke
| Endpoint | Sem token | Resultado esperado | Status |
|---|---|---|---|
| `GET /api/v1/ai-chat/providers` | 401 Unauthorized (`missing_token`) | 401 | PASS |
| `POST /api/v1/ai-chat/message` | 401 Unauthorized (`missing_token`) | 401 | PASS |

## 6. Metrics
- `/metrics` sem token: `503 Service Unavailable`
- environment local: o endpoint responde com `metrics_disabled_without_token`
- observação: comportamento restritivo e explícito, sem expor token

## 7. Apoema SPA via backend
- `/apoema-preview`: `200 OK` com shell SPA
- `/apoema`: `200 OK` com shell SPA

Validação complementar:
- As rotas do frontend passam por `ProtectedRoute` em `frontend/itam-platform/src/App.tsx`, então o backend serve o shell e a proteção efetiva fica no cliente.

## 8. Limitações
- Credencial autenticada: não disponível nesta sessão.
- `127.0.0.1:8080` não respondeu no WSL; usei a bridge local `172.18.0.1:8080` para concluir o smoke.
- Ollama: não foi exercitado nesta rodada.
- Dependências: Postgres/Redis precisaram estar ativos via Compose.

## 9. Decisão
PARTIAL-GO

## 10. Próxima fase recomendada
- Investigar e padronizar a rota de acesso local ao backend no WSL para tornar `127.0.0.1:8080` responsivo, ou documentar oficialmente a bridge local como caminho operacional válido.
