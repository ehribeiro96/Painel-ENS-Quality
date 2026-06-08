# Phase 6.1 Env HML Sanitized Review

## Metadata
- Permission: `600`
- Owner: `estevaoqualityadm`
- Group: `estevaoqualityadm`

## Git ignore
- `infra/hermesops/.env.hml` is ignored by Git.
- `infra/hermesops/.env.hml.example` remains versionable.

## Variable presence
- Required keys present:
  - `COMPOSE_PROJECT_NAME`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `REDIS_HOST`
  - `REDIS_PORT`
  - `COMPOSIO_ENABLED`
  - `COMPOSIO_MODE`

## Conclusion
- The local env is ready for planning, and no values were printed.
