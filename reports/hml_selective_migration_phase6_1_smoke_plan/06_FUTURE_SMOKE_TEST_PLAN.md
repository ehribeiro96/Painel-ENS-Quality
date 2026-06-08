# HermesOps HML Future Smoke Test Plan

## Status

Plano criado. Runtime ainda não autorizado.

## Pré-condições obrigatórias

- Aprovação humana explícita.
- Backup atualizado.
- Git limpo ou alterações revisadas.
- `.env.hml` presente e ignorado.
- `docker compose config` OK.
- Portas revisadas.
- Volumes revisados.
- Rollback revisado.
- Critérios de parada aceitos.

## Comando futuro de start, NÃO EXECUTAR NESTA FASE

cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/infra/hermesops
docker compose -f docker-compose.hml.yml --env-file .env.hml up -d

## Comandos futuros de observação

docker compose -f docker-compose.hml.yml --env-file .env.hml ps
docker compose -f docker-compose.hml.yml --env-file .env.hml logs --tail=120 --timestamps

## Smoke checks futuros

- Containers criados.
- Containers não reiniciando em loop.
- Postgres inicializado.
- Redis inicializado.
- Serviços principais respondendo, se houver endpoint.
- Logs sem stack trace crítico.
- Nenhuma chamada Composio executada.
- Nenhuma connected account criada.

## Tempo máximo sugerido

Primeira janela de observação: 10 minutos.

## Proibido sem aprovação separada

- `down -v`
- remoção de volumes
- Composio execute
- connected account
- push remoto
