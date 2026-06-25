# Vite proxy IPv6 fix — 2026-06-25

## 1. Status
PARTIAL-GO

## 2. Causa raiz confirmada
O target dev do proxy Vite não estava apontando para o caminho IPv6 funcional do host local. O backend responde via `localhost`/`[::1]` no WSL, enquanto `127.0.0.1` para o backend em 8080 foi confirmado como `ECONNRESET`.

## 3. Target proxy antes
`http://127.0.0.1:8080`

## 4. Target proxy depois
`http://[::1]:8080`

## 5. Backend 127.0.0.1:8080
Falha com `ECONNRESET`.

## 6. Backend localhost:8080
OK no WSL. `/health/ready` retornou 200.

## 7. Backend [::1]:8080
OK no WSL. `/health/ready` retornou 200.

## 8. Vite proxy /api/v1/auth/refresh antes/depois
Antes: `ECONNRESET` ao chamar via Vite.
Depois: no port 5175 com o target IPv6, a chamada via Vite deixou de resetar e respondeu `401 Unauthorized` com `missing_refresh_token`.

## 9. Vite proxy /api/v1/auth/login antes/depois
Antes: `ECONNRESET` ao chamar via Vite.
Depois: no port 5175 com o target IPv6, a chamada via Vite respondeu `422 Unprocessable Entity` para payload inválido.

## 10. Windows 5173/8080
`Test-NetConnection` mostrou TCP aberto, mas as requisições via `Invoke-WebRequest` falharam com conexão fechada no lado subjacente. Isso sugere um problema de forwarding/acesso externo separado do proxy Vite.

## 11. Arquivos alterados
- `frontend/itam-platform/vite.config.ts`
- `docs/audit/vite-proxy-ipv6-fix/VITE_PROXY_IPV6_FIX_20260625.md`
- `docs/audit/vite-proxy-ipv6-fix/vite-proxy-ipv6-findings.json`
- `docs/audit/vite-proxy-ipv6-fix/vite-proxy-ipv6-gates.log`

## 12. Código de app alterado
Não.

## 13. Backend alterado
Não.

## 14. Validações
- `git diff --check`
- `PYTHONPATH=backend .venv/bin/python -m pytest`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`
- Smoke tests de backend direto e Vite proxy

## 15. Próxima fase recomendada
Investigar o problema externo que ainda afeta o acesso Windows/WSL no port 5173, sem mexer em backend, RBAC ou contrato da API. Se necessário, validar um ajuste de porta/dev-host separado do proxy.