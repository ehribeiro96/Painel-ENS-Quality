# Windows AD / GPO

## Objective
Windows domain management

## Recommended structure
- scripts/
- policies/
- docs/

## Build
```text
gpupdate /force
```

## Test
```text
Pester or dry-run checks
```

## Lint
```text
static checks
```

## Common risks
- wide blast radius
- unreviewed policy changes

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
