# Phase 6.1 Compose Topology Audit

## Services
- `postgres`
  - image: `postgres:16-alpine`
  - ports: `127.0.0.1:7433:5432`
  - volumes: `hermesops_hml_postgres_data:/var/lib/postgresql/data`
- `qdrant`
  - image: `qdrant/qdrant:latest`
  - ports: `127.0.0.1:7333:6333`, `127.0.0.1:7334:6334`
  - volumes: `hermesops_hml_qdrant_storage:/qdrant/storage`
- `redis`
  - image: `redis:7-alpine`
  - ports: `127.0.0.1:7380:6379`
  - volumes: `hermesops_hml_redis_data:/data`

## Top-level volumes
- `hermesops_hml_postgres_data`
- `hermesops_hml_qdrant_storage`
- `hermesops_hml_redis_data`

## Top-level networks
- `hermesops_hml_net`

## Compose enumeration
- `docker compose config --volumes`: `OK`

## Conclusion
- The topology is local-only and matches the canonical HML config.
