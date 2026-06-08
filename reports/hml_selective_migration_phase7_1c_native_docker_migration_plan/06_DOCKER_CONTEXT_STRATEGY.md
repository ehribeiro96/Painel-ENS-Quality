# Estratégia de Docker Contexts - HermesOps HML

## Estado atual

Runtime atual usa Docker Desktop WSL integration.

## Objetivo futuro

Ter contexts claros, sem ambiguidade:

- `desktop-linux` ou equivalente: Docker Desktop
- `wsl-native` ou equivalente: Docker Engine nativo

## Regras

1. Não usar `docker context use` sem aprovação.
2. Preferir comandos explícitos com `--context` durante testes.
3. Registrar `docker context show` antes e depois de qualquer mudança.
4. Nunca executar `up -d` no daemon errado.
5. Nunca executar `down -v` como rollback automático.

## Comandos futuros, NÃO EXECUTAR NESTA FASE

```bash
docker context ls
docker context create wsl-native --docker host=unix:///var/run/docker.sock
docker --context wsl-native compose -f docker-compose.hml.yml --env-file .env.hml config
```
