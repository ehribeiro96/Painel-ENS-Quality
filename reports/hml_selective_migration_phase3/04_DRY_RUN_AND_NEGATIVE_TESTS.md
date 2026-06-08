# Phase 3 Dry-Run and Negative Test Report

## Allowlisted dry-runs
- `validators/coderos/validation_runner.py` passed.
- `validators/office/office_safety_validator.py` passed.
- `validators/ingest/sanitize_document.py` passed.
- `auditors/localization/ptbr_prompt_audit.py` passed against the isolated sample directory.
- `auditors/coderos/code_review_checker.py` passed.
- `validators/memory/memory_conflict_check.py` passed.

## Allowlisted dry-run notes
- `sanitize_document.py` processed 46 markdown files and reported 4 findings in the corpus.
- `ptbr_prompt_audit.py` was pointed at a controlled sample with the required fields:
  - papel
  - entrada
  - saída
  - regras
  - bloqueios
  - preservar comandos

## Negative tests
- `offline-dry-run --tool ../../etc/passwd` was rejected.
- `offline-dry-run --tool /etc/passwd` was rejected.
- `offline-dry-run --tool validators/coderos/stack_detector.py` was rejected because it is not allowlisted for Phase 3 dry-run.

## Security scan
- Executable surfaces scanned cleanly after cleanup.
- No forbidden files remained in the Phase 3 additions.
- No real secret pattern was found in the scanned surfaces.
