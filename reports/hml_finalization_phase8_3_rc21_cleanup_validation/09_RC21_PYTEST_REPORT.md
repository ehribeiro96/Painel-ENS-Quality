# RC2.1 Pytest Report

## Result

- Exit code: `1`
- Cause: the isolated venv could not fetch `ruff==0.11.13` from the network, and `pytest` was therefore not installed in the venv.
- This is an environment/dependency resolution issue, not a confirmed product regression.

## Classification

- `GO COM RESSALVAS`

## Evidence

- `evidence/20_rc21_pytest_cleanroom.txt`
- `evidence/20_rc21_pytest_cleanroom.rc`
