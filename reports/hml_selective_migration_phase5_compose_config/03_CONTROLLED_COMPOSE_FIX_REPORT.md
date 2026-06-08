# Phase 5 Controlled Compose Fix Report

## Destination
- `infra/hermesops/docker-compose.hml.yml`

## Fixes applied
- Quoted the host port mappings.
- Removed direct `env_file: .env.hml` dependency from the controlled copy.
- Replaced blank Postgres environment entries with safe defaults.
- Fixed the malformed Redis command list by replacing the empty YAML item with an empty-string argument.

## Example env
- Added `infra/hermesops/.env.hml.example`
- The file contains placeholders only and no real secret values.

## Diff summary
- `env_file` removed from all services in the controlled copy.
- Postgres now uses `${VAR:-default}` fallbacks.
- Redis command is valid YAML and valid Compose syntax.
