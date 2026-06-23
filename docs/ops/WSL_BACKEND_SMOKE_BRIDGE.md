# WSL Backend Smoke Bridge

## Objetivo

Documentar o caminho operacional de smoke do backend no WSL quando `127.0.0.1:8080` não responde, mas a bridge Docker/WSL responde.

## Base URL recomendada no WSL

Use:

`http://172.18.0.1:8080`

quando:

- `127.0.0.1:8080` retorna timeout;
- `localhost:8080` retorna timeout;
- `172.18.0.1:8080` responde.

## Sintoma conhecido

| Endereço | Resultado |
|---|---|
| `127.0.0.1:8080` | timeout |
| `localhost:8080` | timeout |
| `172.18.0.1:8080` | OK |
| `host.docker.internal:8080` | host não resolvido |
| `WSL IP:8080` | connect failed |

Causa provável:

`D_WSL_LOOPBACK_FORWARDING_ISSUE`

## Smoke básico

```bash
BASE_URL="http://172.18.0.1:8080"

curl --max-time 10 -i "$BASE_URL/health"
curl --max-time 10 -i "$BASE_URL/health/ready"
curl --max-time 10 -i "$BASE_URL/api/v1/ai-chat/providers"
```

## Resultado esperado

| Endpoint | Esperado |
|---|---|
| `/health` | `200 OK` |
| `/health/ready` | `200 OK` |
| `/api/v1/ai-chat/providers` sem token | `401 Unauthorized` com `missing_token` |

## Smoke de segurança

```bash
BASE_URL="http://172.18.0.1:8080"

curl --max-time 20 -i \
  -H "Content-Type: application/json" \
  -d '{"provider":"mock","model":"fallback-local","message":"teste sem token","mode":"assistente_n2","attachments":[],"context":{"route":"wsl-smoke"}}' \
  "$BASE_URL/api/v1/ai-chat/message"
```

Resultado esperado:

`401 Unauthorized`

## Metrics

```bash
BASE_URL="http://172.18.0.1:8080"

curl --max-time 10 -i "$BASE_URL/metrics"
```

Resultado observado no diagnóstico:

`503 Service Unavailable` com `metrics_disabled_without_token`

## Decisão atual

Para smoke local no WSL, usar:

`http://172.18.0.1:8080`

como base URL operacional até que exista uma tarefa específica para investigar `127.0.0.1:8080`, portproxy, firewall ou bind.
