# Compose Healthcheck Patch

- `infra/hermesops/docker-compose.hml.yml` updated.
- PostgreSQL healthcheck added with `pg_isready`.
- Redis healthcheck added with `redis-cli ping`.
- Qdrant left unchanged because no internal HTTP tool was validated.
- Evidence diff: `reports/hml_selective_migration_phase7_2_healthchecks/evidence/04_compose_healthcheck_diff.txt`

