# `.gitignore` Cache Policy

## Result

- Updated `.gitignore` to include the missing required Python cache patterns:
  - `*.py[cod]`
  - `*$py.class`
- Existing protections already covered `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, and `.ruff_cache/`.

## Evidence

- Git diff in the hygiene commit
