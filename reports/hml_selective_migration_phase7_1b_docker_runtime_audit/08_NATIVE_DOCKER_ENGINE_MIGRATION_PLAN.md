# Plano Futuro - Migracao para Docker Engine Nativo no WSL/Linux

## Status

Plano documental. Nenhuma migracao executada nesta fase.

## Pre-condicoes

- aprovacao humana explicita
- stack atual parado de forma controlada ou janela de manutencao
- backup logico do PostgreSQL
- backup/export do Qdrant, se necessario
- estrategia para Redis definida
- `docker context ls` revisado
- Docker Desktop e Docker Engine nativo nao confundidos
- portas livres no daemon alvo

## Estrategia recomendada

1. Nao migrar volumes Docker brutos entre daemons como primeira opcao.
2. Preferir export logico:
   - PostgreSQL: `pg_dump`/`pg_restore`
   - Qdrant: snapshot/export compativel ou dump conforme suporte validado
   - Redis: avaliar persistencia RDB/AOF ou tratar como cache, se aplicavel
3. Instalar Docker Engine nativo somente em fase separada.
4. Criar contexto claro:
   - `desktop-linux`
   - `wsl-native`
5. Validar com `docker context show`.
6. Subir stack no daemon nativo somente com Compose ja validado.
7. Comparar probes.
8. So depois desativar stack antigo.

## Comandos futuros proibidos nesta fase

```text
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker
docker context use ...
docker compose up -d
docker compose down
```
