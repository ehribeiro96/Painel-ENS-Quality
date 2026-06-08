# Checklist de Segurança para UAT

| Controle | Como validar | Status | Evidência |
|---|---|---|---|
| `ADMIN_PASSWORD` não está versionado | Buscar em `README.md`, `docs`, `tests`, `scripts`, `.env.example`, `docker-compose.yml` | Passou | Sem senha real identificada; placeholders mantidos |
| `.env` não deve ser commitado | Conferir `.gitignore` | Passou | `.gitignore` criado com `.env` e `.env.*` |
| `.env.example` usa placeholder | Abrir `.env.example` | Passou | `ADMIN_PASSWORD=<DEFINIR_LOCALMENTE_NO_ENV>` |
| Refresh cookie não fica exposto em JS | Validar comportamento no navegador/API | Pendente |  |
| Logs não exibem senha | Revisar logs de startup/login | Pendente |  |
| `JWT_SECRET_KEY` forte fora de local | Conferir env UAT | Pendente |  |
| CORS coerente | Revisar env/config | Pendente |  |
| Upload com limite | Validar importação inválida/maliciosa | Pendente |  |
| CSV injection bloqueado | Usar fixture com `=`, `+`, `@` | Pendente |  |
| VIEWER não escreve | UAT-017/regressão | Passou | Suíte operacional |
| Sem token retorna 401 | Smoke `/api/v1/assets` | Passou | Start UAT e restore |
| Permissão insuficiente retorna 403 | Regressão RBAC | Passou | Suíte operacional |

## Observação

UAT local controlado pode usar segredos locais temporários. Produção exige secret manager ou mecanismo equivalente e rotação formal.
