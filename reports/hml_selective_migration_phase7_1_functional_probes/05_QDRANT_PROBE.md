# Qdrant Probe

## Endpoints testados

- `http://127.0.0.1:7333/readyz`
- `http://127.0.0.1:7333/healthz`
- `http://127.0.0.1:7333/collections`

## Resultado

- `/readyz`: `all shards are ready`
- `/healthz`: `healthz check passed`
- `/collections`: retorno OK com lista vazia

## Conclusao

Qdrant respondeu corretamente em modo read-only.
