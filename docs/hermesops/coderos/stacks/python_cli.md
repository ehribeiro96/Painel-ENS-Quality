# Python CLI

## Objective
Python command-line tool

## Recommended structure
- src/
- tests/
- README.md

## Build
```text
python -m yourtool --help
```

## Test
```text
pytest
```

## Lint
```text
ruff check .
```

## Common risks
- argparse misuse
- unsafe file writes

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
