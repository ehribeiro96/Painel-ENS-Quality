# Python FastAPI

## Objective
FastAPI API service

## Recommended structure
- app/main.py
- routers/
- tests/

## Build
```text
python -m uvicorn app.main:app --reload
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
- unhandled exceptions
- dependency drift

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
