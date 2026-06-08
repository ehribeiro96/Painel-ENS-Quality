# Qdrant RAG

## Objective
Vector retrieval and metadata filters

## Recommended structure
- schemas/
- indexes/
- tests/

## Build
```text
offline schema checks
```

## Test
```text
offline evals
```

## Lint
```text
metadata validation
```

## Common risks
- secret indexing
- bad filters

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
