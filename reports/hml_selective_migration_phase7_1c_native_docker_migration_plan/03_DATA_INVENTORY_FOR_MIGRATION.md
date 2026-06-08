# Data Inventory for Migration

## Criticidade dos recursos

- PostgreSQL: estado persistente critico
- Qdrant: estado persistente critico se houver collections
- Redis: depende da politica de uso; pode ser cache ou persistente
- network: recriavel
- containers: recriaveis
- images: baixaveis/recriaveis

## Volumes

- `hermesops_hml_postgres_data`
- `hermesops_hml_qdrant_storage`
- `hermesops_hml_redis_data`

## Network

- `hermesops_hml_net`

## Mountpoints observados

- os volumes usam driver local no daemon atual

## Conclusao

O plano de migracao deve privilegiar backup lógico e restore validado, nao copia bruta de volumes.
