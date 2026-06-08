# Next.js

## Objective
Next.js app / hybrid web app

## Recommended structure
- app/ or pages/
- components/
- tests/

## Build
```text
npm run build
```

## Test
```text
npm test
```

## Lint
```text
npm run lint
```

## Common risks
- SSR mismatch
- environment leaks

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
