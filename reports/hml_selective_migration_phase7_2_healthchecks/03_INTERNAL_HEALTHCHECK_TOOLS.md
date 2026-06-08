# Internal Healthcheck Tools

- PostgreSQL container exposes `pg_isready` and `psql`.
- Redis container exposes `redis-cli`.
- Qdrant container did not expose `curl`, `wget`, `python3`, or `python` in the internal tool check, so no Qdrant healthcheck was applied.
- Selected Qdrant health tool: `none`
- Evidence: `reports/hml_selective_migration_phase7_2_healthchecks/evidence/03_internal_healthcheck_tools.txt`

