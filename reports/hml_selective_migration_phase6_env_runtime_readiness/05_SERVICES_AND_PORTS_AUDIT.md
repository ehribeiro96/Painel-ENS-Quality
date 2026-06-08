# Phase 6 Services And Ports Audit

## Services
- `postgres`
  - image: `postgres:16-alpine`
  - ports: `127.0.0.1:7433:5432`
- `qdrant`
  - image: `qdrant/qdrant:latest`
  - ports: `127.0.0.1:7333:6333`, `127.0.0.1:7334:6334`
- `redis`
  - image: `redis:7-alpine`
  - ports: `127.0.0.1:7380:6379`

## Conclusion
- The candidate exposes the expected local-only ports and the services align with the canonical config.
