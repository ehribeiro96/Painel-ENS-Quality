# Phase 4.1 Git Baseline Execution Report

## 1. Summary
- Phase 4.1 created a controlled local Git baseline for the HML workspace.
- The workspace was audited, backed up, and selectively staged before commit.

## 2. Final status
- `GO COM RESSALVAS`

## 3. State before Git
- The workspace had no usable Git metadata.
- `git rev-parse`, `git status`, and `git log` failed before initialization.

## 4. Backup created
- `_backup/selective_migration_phase4_1_git_baseline_20260608-104314`

## 5. `.gitignore` applied
- Root `.gitignore` was updated before the baseline add.
- It excludes secrets, caches, build output, exports, backups, and imported release baselines.

## 6. Git initialized
- `git init -b main` was executed locally.
- No remote was configured.

## 7. Files included
- `AGENTS.md`
- `HERMES.md`
- `README.md`
- `docs/hermesops/`
- `tools/hermesops_offline/`
- `tools/hmlops_cli/`
- `scripts/hmlops`
- `reports/hml_selective_migration_phase1/`
- `reports/hml_selective_migration_phase2/`
- `reports/hml_selective_migration_phase3/`
- `reports/hml_selective_migration_phase4/`
- `reports/hml_selective_migration_phase4_1_git_baseline/`

## 8. Files excluded
- `imports/`
- `_backup/`
- `exports/`
- `.env` and `.env.*`
- certificates and token material
- `.jsonl`
- `.log`
- virtualenvs and package caches

## 9. Stage audit
- No forbidden staged paths were found.
- No real secret was found in staged content.

## 10. Commit created
- Local baseline commit created successfully.

## 11. Tag created
- Local baseline tag created successfully.

## 12. HMLOps validation
- Post-commit `hmlops` validation passed.

## 13. Remainders
- Remote is absent.
- Baseline is local only.
- Runtime, Docker, Composio, and Desktop remain out of scope.

## 14. Rollback
- Restore from `_backup/selective_migration_phase4_1_git_baseline_20260608-104314`.
- Do not use `git reset --hard`.
- Do not use `git clean`.

## 15. Next phase recommended
- Continue only if a remote or release policy needs to be defined.
