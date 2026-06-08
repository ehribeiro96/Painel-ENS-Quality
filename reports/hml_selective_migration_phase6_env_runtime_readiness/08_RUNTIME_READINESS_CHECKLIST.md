# HermesOps HML Runtime Readiness Checklist

## Status

Ainda sem runtime.

## Antes de qualquer docker compose up

- [ ] Aprovação humana explícita
- [ ] Backup atualizado
- [ ] Git status revisado
- [x] .env.hml presente e ignorado
- [x] docker compose config OK
- [x] ports revisados
- [x] volumes revisados
- [x] rollback revisado
- [x] Composio disabled/read-only
- [x] connected accounts não automáticas
- [ ] logs planejados
- [ ] smoke test definido
- [ ] critério de parada definido

## Comandos proibidos sem aprovação

docker compose up
docker compose down
docker compose down -v
docker volume rm
docker system prune
