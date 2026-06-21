# DB-RUNTIME-H1 - UAT Runtime Path

## Status

`GO_FASTAPI_BRIDGE_READY`

## Objetivo

Definir caminho operacional seguro para iniciar o FastAPI local no WSL enquanto `127.0.0.1` nao alcança as portas publicadas do Docker Compose.

## Caminho validado

1. Garantir containers locais:

```text
docker compose up -d postgres redis
```

2. Validar saude interna:

```text
docker compose exec -T postgres pg_isready
docker compose exec -T redis redis-cli ping
```

3. Descobrir IPs bridge com `docker inspect` limitado.

4. Iniciar FastAPI em processo local com override temporario de host para Postgres e Redis, sem imprimir URL completa e sem gravar `.env`.

5. Validar:

```text
GET /health -> HTTP 200
GET /login -> HTTP 200
```

## Evidencia do startup completo

```text
database_wait_ok
redis_wait_ok
migrations_ok
bootstrap_admin_ok
frontend_check_ok
startup_complete
```

## Regras de seguranca

- Nao imprimir DB URL.
- Nao imprimir Redis URL.
- Nao imprimir senha.
- Nao imprimir token.
- Nao imprimir cookie.
- Nao imprimir header Authorization.
- Nao gravar storage state.
- Nao versionar IP bridge como configuracao fixa.

## Limitacao

O caminho bridge e operacional para UAT local, mas os IPs podem mudar quando containers/rede Docker forem recriados.

## Recomendacao

Usar o bridge path apenas para desbloquear UAT autenticado local. Em paralelo, tratar a causa de infraestrutura em `WSL-DOCKER-NET-H1`.
