# Phase 4 Rollback

## Rollback path
- `_backup/selective_migration_phase4_20260608-103657`

## To revert Phase 4 only
- Restore the backed-up migration-state snapshot.
- Remove Phase 4 reports if needed.

## Do not do
- Do not delete imports.
- Do not delete `_backup`.
- Do not run `git reset --hard`.
- Do not run `docker compose down -v`.

## Intent
- Keep Phase 1, Phase 2, and Phase 3 intact.
- Roll back only the provenance audit layer if necessary.
