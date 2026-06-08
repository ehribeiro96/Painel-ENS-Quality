# Phase 4.1 Rollback

## Rollback path
- `_backup/selective_migration_phase4_1_git_baseline_20260608-104314`

## Safe rollback
- Preserve the backup.
- Restore the selective baseline snapshot if needed.
- Do not delete imports.
- Do not delete backups.
- Do not run `git reset --hard`.
- Do not run `git clean`.

## Git recovery note
- If the Git baseline must be disabled later, move `.git` aside only in a human-approved recovery step.
