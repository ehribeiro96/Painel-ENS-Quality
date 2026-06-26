# Vite stable port selection — Apoema frontend

Status: GO

## 1. Status
- Vite runtime stabilized on a single dev port in WSL.
- Selected canonical temporary port: 5175.
- WSL validation passed.
- Windows validation passed for `/apoema` and returned expected auth status for refresh.

## 2. Portas testadas
- 5174
- 5175
- 5176

## 3. Porta selecionada
- 5175

## 4. Target proxy usado
- `http://[::1]:8080`

## 5. Resultado /apoema por porta
- 5174: listener up, Vite ready, but `curl http://127.0.0.1:5174/apoema` timed out.
- 5175: `HTTP/1.1 200 OK` with HTML shell.
- 5176: `HTTP/1.1 200 OK` with HTML shell.

## 6. Resultado /api/v1/auth/refresh por porta
- 5174: `curl` timed out; no ECONNRESET observed in the captured run, but the port was not usable for the required path checks.
- 5175: `HTTP/1.1 401 Unauthorized` with `{"detail":"missing_refresh_token"}`.
- 5176: `HTTP/1.1 401 Unauthorized` with `{"detail":"missing_refresh_token"}`.

## 7. Resultado /api/v1/auth/login por porta
- 5174: `curl` timed out.
- 5175: `HTTP/1.1 422 Unprocessable Entity` for invalid email payload.
- 5176: `HTTP/1.1 422 Unprocessable Entity` for invalid email payload.

## 8. Resultado Windows para porta selecionada
- `Test-NetConnection 127.0.0.1 -Port 5175` -> `TcpTestSucceeded=True`
- `Invoke-WebRequest http://127.0.0.1:5175/apoema` -> `200 OK`
- `Invoke-WebRequest http://127.0.0.1:5175/api/v1/auth/refresh -Method POST` -> `401 Unauthorized` (expected without cookie)

## 9. Processos Vite antigos encerrados
- Sim. The stale frontend Vite process on 5173 was stopped, and the temporary test instances on 5174/5176 were killed after validation.

## 10. Helper criado
- Sim

## 11. Arquivos alterados
- `scripts/dev-apoema-vite.sh`
- `docs/audit/vite-stable-port-selection/VITE_STABLE_PORT_SELECTION_20260625.md`
- `docs/audit/vite-stable-port-selection/vite-stable-port-findings.json`
- `docs/audit/vite-stable-port-selection/vite-stable-port-gates.log`

## 12. Código app alterado
- Não

## 13. Backend alterado
- Não

## 14. Docker alterado
- Não

## 15. Próxima fase recomendada
- Use `scripts/dev-apoema-vite.sh` with `APOEMA_VITE_PORT=5175` for the temporary stable Vite launcher while the migration work continues.
- If Windows/browser forwarding regresses again, re-run the same 5175 checks before changing app code.
