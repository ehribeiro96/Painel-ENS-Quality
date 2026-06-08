# Rollback da Fase 7.1

Nenhuma mudanca de runtime foi aplicada nesta fase.

## Se precisar parar o stack futuramente

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml stop
```

## Se precisar remover containers sem apagar volumes

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml down
```

## Proibido sem aprovacao

- `docker compose down -v`
- `docker volume rm`
- `docker system prune`

## Preservar

- volumes
- `.env.hml`
- reports
- backups
- Git baseline
- imports
