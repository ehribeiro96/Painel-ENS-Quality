# WSL Backend Smoke Bridge Note — 2026-06-23

## Status

GO

## Decisão

Documentar `172.18.0.1:8080` como bridge operacional de smoke no WSL.

## Base técnica

Diagnóstico anterior:

- `d908ee7 docs(audit): document wsl backend access diagnostic`

Resultados:

| Base URL | Resultado |
|---|---|
| `127.0.0.1:8080` | timeout |
| `localhost:8080` | timeout |
| `172.18.0.1:8080` | OK |
| `host.docker.internal:8080` | host não resolvido |
| `WSL IP:8080` | connect failed |

## Endpoints validados via bridge

| Endpoint | Resultado |
|---|---|
| `/health` | `200 OK` |
| `/health/ready` | `200 OK` |
| `/api/v1/ai-chat/providers` sem token | `401 Unauthorized` |
| `/metrics` sem token | `503 Service Unavailable` |

## Risco

Não é bloqueador de aplicação. É uma diferença operacional local do WSL.

## Próxima ação

Usar `docs/ops/WSL_BACKEND_SMOKE_BRIDGE.md` como runbook operacional até que haja uma tarefa específica para investigar portproxy/firewall/bind.
