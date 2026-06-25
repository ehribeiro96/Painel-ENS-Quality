# Apoema-only Phase 5H - AuthProvider Boot - 2026-06-23

## 1. Status
GO

## 2. Root cause
O boot autenticado falhava em Vite dev com React `StrictMode` porque a primeira execucao do efeito de auth abortava o `POST /api/v1/auth/refresh`. Mesmo abortada no browser, a chamada podia chegar ao backend e rotacionar o refresh cookie. A segunda execucao do boot usava o cookie antigo e recebia `401`; repeticoes seguintes podiam chegar a `429`, e o frontend tratava a ausencia de novo access token como logout.

## 3. Arquivos alterados
- `frontend/itam-platform/src/lib/auth.tsx`
- `frontend/itam-platform/src/lib/api.ts`
- `tests/test_authprovider_strictmode_boot_contract.py`
- `tests/test_login_frontend_contract.py`

## 4. AbortError/cancelamento tratado como neutro
Sim.

`AbortError` agora e repropagado sem `clearSession()`, sem `setUser(null)` e sem marcar o boot como anonimo.

## 5. ProtectedRoute aguarda checking
Sim.

`ProtectedRoute` ja renderizava `RouteLoading` enquanto `loading` era verdadeiro. A correcao preservou esse contrato e impediu que o boot fosse encerrado como anonimo por um refresh abortado.

## 6. Refresh com cookie valido preserva sessao
Sim.

Foi criado um `storageState` temporario em `/tmp/apoema-uat-auth-state.json`, validado com refresh `200`, e reutilizado na navegacao das rotas protegidas.

## 7. Rotas protegidas testadas
- `/apoema`
- `/apoema/chat`
- `/apoema/assets`
- `/apoema/assets/123`
- `/apoema/users`
- `/apoema/users/123`
- `/apoema/settings`

Resultado:

- `ROUTES_TESTED=7`
- `REDIRECTED_TO_LOGIN=0`
- `AUTHPROVIDER_BOOT_VALID=1`

## 8. Rotas que ainda redirecionam para login
Nenhuma das rotas testadas redirecionou para `/login` com `storageState` valido.

## 9. Backend alterado
Nao.

## 10. RBAC/Auth API alterado
Nao.

O contrato HTTP da API nao foi alterado.

## 11. storageState commitado
Nao.

O arquivo permaneceu em `/tmp/apoema-uat-auth-state.json`.

## 12. Credenciais/cookies/tokens em docs
Nao.

Os logs registram apenas status, contagens e paths. Valores de cookie, token, header e credencial nao foram gravados.

## 13. Validacoes executadas
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`: PASS
- `.venv/bin/python -m ruff check backend tests scripts`: PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: PASS
- `npm run build`: PASS
- `git diff --check`: PASS
- Playwright auth boot validation com `/tmp/apoema-uat-auth-state.json`: PASS

## 14. Limitacoes
A validacao autenticada usou credencial UAT local temporaria e `storageState` em `/tmp`. Nenhum artefato sensivel foi versionado.

## 15. Proxima fase recomendada
Reexecutar a Fase 5G autenticada completa usando:

```bash
export AUTH_MODE=EXISTING_STORAGE_STATE
export APOEMA_AUTH_STATE="/tmp/apoema-uat-auth-state.json"
```
