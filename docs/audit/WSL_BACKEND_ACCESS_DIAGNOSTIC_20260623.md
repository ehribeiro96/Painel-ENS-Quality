# WSL Backend Access Diagnostic — 2026-06-23

## 1. Status
PARTIAL-GO

## 2. Contexto
- Último smoke runtime: `609d59f docs(audit): add backend runtime smoke report`
- Bridge funcional: `172.18.0.1:8080`
- `127.0.0.1:8080` timeout no WSL nesta sessão

## 3. Ambiente
- WSL: Linux/WSL2 na sessão atual
- Docker: disponível e com `postgres`/`redis` saudáveis
- Rotas: `172.18.0.0/16` presente como rede de bridge do Docker
- IPs:
  - WSL IP observado: `172.16.0.2`
  - Bridge do Docker observada: `172.18.0.1`

## 4. Portas
- `ss` 8080: processo Python ouvindo em `0.0.0.0:8080`
- `docker ps`: `postgres` e `redis` publicados em `127.0.0.1:5432` e `127.0.0.1:6379`
- `docker compose ps`: ambos saudáveis

## 5. Matrix de curl
| Base URL | /health | /health/ready | /api/v1/ai-chat/providers sem token |
|---|---|---|---|
| `127.0.0.1:8080` | timeout | timeout | timeout |
| `localhost:8080` | timeout | timeout | timeout |
| `172.18.0.1:8080` | `200 OK` | `200 OK` | `401 Unauthorized` (`missing_token`) |
| `host.docker.internal:8080` | host não resolvido | host não resolvido | host não resolvido |
| `WSL_IP:8080` (`172.16.0.2`) | connect failed | connect failed | connect failed |

## 6. Causa provável
Classificação: `D_WSL_LOOPBACK_FORWARDING_ISSUE`

Base da classificação:
- o backend responde normalmente pela bridge do Docker;
- `127.0.0.1` e `localhost` expiraram nesta sessão;
- `host.docker.internal` não está resolvendo no WSL;
- o IP do WSL também não alcançou a porta 8080;
- não houve indício de falha funcional no backend, apenas de caminho de acesso local.

## 7. Decisão recomendada
- Documentar `172.18.0.1:8080` como bridge operacional no WSL para smoke local.

## 8. Riscos
- O caminho `127.0.0.1:8080` permanece não confiável nesta sessão WSL.
- Mudanças de rede do WSL/Docker podem alterar o IP da bridge.
- A recomendação operacional depende de o backend continuar exposto via bridge do Docker.

## 9. Próxima fase
- Criar documentação operacional de smoke no WSL com uso explícito da bridge `172.18.0.1:8080`.
- Se for desejado normalizar `127.0.0.1:8080`, abrir tarefa separada para rede/port forward do ambiente, não para código de produto.
