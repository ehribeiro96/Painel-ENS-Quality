# PowerShell 7

## Objective
PowerShell automation script

## Recommended structure
- scripts/
- tests/
- README.md

## Build
```text
pwsh -File script.ps1 -WhatIf
```

## Test
```text
PSScriptAnalyzer
```

## Lint
```text
PSScriptAnalyzer
```

## Common risks
- destructive cmdlets
- credential handling

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
