# Python Data Tools

## Objective
Data processing / ETL scripts

## Recommended structure
- src/
- data/
- tests/

## Build
```text
python scripts/tool.py --dry-run
```

## Test
```text
pytest
```

## Lint
```text
python -m py_compile **/*.py
```

## Common risks
- large-file memory use
- silent data loss

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
