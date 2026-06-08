# Docker Compose

## Objective
Multi-service local stack

## Recommended structure
- compose.yaml
- services/
- docs/

## Build
```text
docker compose config
```

## Test
```text
docker compose ps
```

## Lint
```text
docker compose config
```

## Common risks
- volumes/env drift
- service dependency loops

## Debugging
- Check entrypoints and config.
- Reproduce with minimal input.
- Validate logs and error paths.

## Rollback
- Revert the last patch.
- Restore the previous known-good config.

## Best practices
- Keep changes minimal.
- Prefer explicit configuration.
- Avoid secrets in Git.

## Validation criteria
- Compiles or runs in dry-run mode.
- Tests pass or at least reproduce the target failure.
- No prohibited actions introduced.
