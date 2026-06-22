# CLOSE-DOCS-LEGACY-H1 — Executive Summary

## Status

GO_DOCS_LEGACY_CLASSIFIED

## What was classified

The repository's pre-existing untracked trees were split into documentation, migration proposals, legacy assets, static assets, and local runtime artifacts.

## What was not committed

- `_migration_proposals/hermesops_selective_migration/**`
- `assets/legacy/Laravel/**`
- `assets/static/**`
- `docs/audit/screenshots/**`
- `data/*.db-shm`
- `data/*.db-wal`
- `_cleanup_backup_manifest.md`

## Gitignore changes

Updated `.gitignore` to cover local runtime database leftovers and browser/test state patterns:
- `*.db-shm`
- `*.db-wal`
- `data/*.db-shm`
- `data/*.db-wal`
- `data/*.sqlite-shm`
- `data/*.sqlite-wal`
- `**/storageState*.json`
- `**/storage-state*.json`
- `**/.auth/`
- `**/playwright-report/`
- `**/test-results/`

## Risks

- Large legacy and migration-proposal trees remain on disk and out of Git.
- Audit screenshots remain local-only and are intentionally not committed.
- Base44 import remains pending and should only start after the tracked tree stays boundary-clean.

## Next boundary

`BASE44-FRONTONLY-H1`
