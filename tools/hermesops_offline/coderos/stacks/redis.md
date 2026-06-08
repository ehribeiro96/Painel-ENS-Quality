# Redis

## Objective
Caching/queue component

## Recommended structure
- src/
- tests/
- compose.yaml

## Build
```text
redis-cli ping
```

## Test
```text
pytest
```

## Lint
```text
lint scripts
```

## Common risks
- eviction surprises
- TTL mistakes

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
