# Office automation

## Objective
Office file workflows

## Recommended structure
- enterprise_office_skills/
- tools/office/
- reports/

## Build
```text
python -m py_compile tools/office/*.py
```

## Test
```text
offline JSON validation
```

## Lint
```text
schema validation
```

## Common risks
- fidelity loss
- CSV overuse

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
