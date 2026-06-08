# HermesOps HML Healthcheck Proposal

## Status atual

Containers estao `running`, `restart_count=0`, mas `health=none`.

## Objetivo

Adicionar healthchecks ao Compose em fase futura, com recriacao controlada dos containers, sem apagar volumes.

## Proposta Postgres

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U \"$${POSTGRES_USER}\" -d \"$${POSTGRES_DB}\""]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 20s
```

## Proposta Redis

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

## Proposta Qdrant

```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:6333/readyz || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 20s
```

## Observacao

Validar se a imagem do Qdrant possui `wget`. Se nao possuir, usar alternativa compativel com a imagem, ou healthcheck via endpoint externo no host em fase de observacao.

## Fase futura

Fase 7.2: aplicar healthchecks no Compose e recriar containers com `docker compose up -d` controlado, sem `down -v`.
