# RBAC & Security Audit — Deep Project Audit 2026-06-23

## Resumo

| Controle | Status | Notas |
|----------|--------|-------|
| Apoema SPA em ProtectedRoute | PASS | `App.tsx` linhas 63–64 |
| AI `/providers` e `/message` com RBAC | PASS | `ai_chat.py` usa `ai_chat_user` |
| `/metrics` protegido fora de local | PASS | `_require_metrics_access` + testes `test_metrics_hardening.py` |
| Menu lateral filtra por role | PASS | `AppShell.tsx` `visibleNav` |
| Upload accept alinhado | PASS | `.csv,.xlsx` |
| Frontend chama backend para IA | PASS | Sem URLs Ollama/Hermes diretas (teste estático) |
| Settings claramente visual | PARTIAL | Badge existe; conteúdo ainda sugere configuração |
| Runtime smoke WSL | SKIPPED | Backend `172.18.0.1:8080` indisponível |

## Matriz RBAC (estática)

| Endpoint / Rota | ADMIN | TECH | MANAGER | VIEWER | Evidência |
|-----------------|-------|------|---------|--------|-----------|
| `/imports` UI | ✓ | ✓ | ✗ | ✗ | `RoleGuard` |
| `/macros` UI | ✓ | ✓ | ✗ | ✗ | `RoleGuard` |
| `/audit-logs` UI | ✓ | ✗ | ✓ | ✗ | `RoleGuard` |
| `/settings` UI | ✓ | ✗ | ✗ | ✗ | `RoleGuard` |
| `POST /imports/*` | ✓ | ✓ | ✗ | ✗ | `require_role` |
| `GET /imports` | ✓ | ✓ | ✓ | ✓ | `get_current_user` |
| `POST /assets` | ✓ | ✓ | ✗ | ✗ | `require_role` |
| `DELETE /assets` | ✓ | ✗ | ✗ | ✗ | `require_role` |
| `POST /users` (role≠VIEWER se TECH) | ✓ | ✓* | ✗ | ✗ | `users.py` |
| AI Chat (principal + Apoema) | ✓ | ✓ | ✓ | ✓ | `ai_chat_user` |
| Assinaturas generate | ✓ | ✓ | ✓ | ✓ | `get_current_user` apenas |

\* TECHNICIAN só pode criar usuários com role VIEWER.

## Achados de segurança funcional

### SEC-001 — Apoema fallback UX mascara 401 (P1)
Ver BUG-001/BUG-002. Backend exige auth; frontend não propaga falha.

### SEC-002 — `/metrics` aberto em `environment=local` (INFO/P3)
Comportamento intencional para dev. Documentar em runbook de produção.

### SEC-003 — Rate limit API em memória (P2)
Ver BUG-007.

### SEC-004 — Legado Flask `/admin` e `/assinaturas` (P2 remanescente)
CSP com `unsafe-inline` em scripts; auth SQLite separada. Isolar em rede interna.

### SEC-005 — Health expõe `startup`, `legacy_mounts` (P3)
`GET /health` retorna estado interno. Aceitável em dev; restringir em prod.

### SEC-006 — Arquivos sensíveis versionados
`git ls-files` não inclui `.env` real — apenas `.env.example` variants. PASS.

## Testes de segurança executados

- `tests/test_metrics_hardening.py` — incluído no unittest gate
- `tests/test_apoema_ai_chat_backend.py::test_apoema_routes_require_auth_dependency`
- `tests/test_ai_chat_hardening.py` — RBAC em rotas de conversação
- `tests/test_security_headers.py` — CSP SPA vs legado

## Recomendações antes de produção

1. Corrigir fallback Apoema para não mascarar 401/403 (P1).
2. Configurar `METRICS_TOKEN` e `ENVIRONMENT=staging|production`.
3. Validar smoke runtime com backend ativo.
4. Executar UAT por perfil (KI-003).
5. Monitorar acesso ao legado Flask.

## Comandos sugeridos de validação (operador)

```bash
BASE_URL=http://172.18.0.1:8080
curl -i "$BASE_URL/api/v1/ai-chat/providers"          # esperado 401
curl -i "$BASE_URL/metrics"                          # local: 200; staging: 401/503
curl -i -H "x-metrics-token: <token>" "$BASE_URL/metrics"  # staging: 200
```
