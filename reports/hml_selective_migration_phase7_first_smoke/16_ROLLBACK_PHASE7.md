# Rollback da Fase 7

## Rollback leve

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml stop
```

## Rollback de containers sem apagar volumes

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
- baseline Git
- imports
