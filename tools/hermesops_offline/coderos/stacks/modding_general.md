# Safe modding

## Objective
Game/application modding with safety boundaries

## Recommended structure
- modding/
- docs/
- tests/

## Build
```text
offline validation
```

## Test
```text
manifest checks
```

## Lint
```text
prohibited-action checks
```

## Common risks
- license bypass
- anti-cheat bypass

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
