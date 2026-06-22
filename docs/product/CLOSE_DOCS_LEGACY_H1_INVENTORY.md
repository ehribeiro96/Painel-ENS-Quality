# CLOSE-DOCS-LEGACY-H1 — Untracked / Legacy Inventory

## Status

GO_DOCS_LEGACY_CLASSIFIED

## Scope

Classify the pre-existing untracked and legacy artifact trees before continuing the Base44 import. Nothing in this boundary imports Base44 or changes runtime behavior.

## Summary counts

- Total untracked before .gitignore update: 614
- Cleanup manifest: 1
- Migration proposals: 280
- Legacy assets: 224
- Docs kept as documentation candidates: 41
- Docs/screenshots marked do-not-commit: 66
- Local runtime artifacts now ignored by .gitignore: `data/*.db-shm`, `data/*.db-wal`

## Groups

### Cleanup manifest

- `_cleanup_backup_manifest.md`

Classification: `KEEP_DOCS_CANDIDATE` for inventory purposes, but not committed in this boundary.

### Migration proposals

- `_migration_proposals/hermesops_selective_migration/**`

Classification: `MIGRATION_PROPOSAL`

Policy: keep out of this boundary; requires separate review before any decision about archival or commit.

### Legacy assets

- `assets/legacy/Laravel/**`

Classification: `ARCHIVE_REFERENCE_ONLY` / `LARGE_LEGACY_ASSET`

Policy: retained on disk as reference material, not committed in this boundary.

### Static assets

- `assets/static/**`

Classification: `ARCHIVE_REFERENCE_ONLY` / `LARGE_LEGACY_ASSET`

Policy: retained on disk as reference material, not committed in this boundary.

### Docs

- `docs/product/**` and `docs/audit/**` untracked documents outside the Base44 import scope
- `docs/audit/screenshots/**` audit images and manifest files

Classification:
- documentation text: `KEEP_DOCS_CANDIDATE`
- audit screenshots/manifests: `DO_NOT_COMMIT`

Policy: textual docs can be triaged in dedicated doc boundaries; screenshots remain out of Git unless explicitly authorized.

### Data/runtime artifacts

- `data/*.db-shm`
- `data/*.db-wal`
- `data/*.sqlite-shm`
- `data/*.sqlite-wal`

Classification: `LOCAL_RUNTIME_ARTIFACT`

Policy: ignored locally via `.gitignore`; not committed.

### Misc root-level files

- `_cleanup_backup_manifest.md`

Classification: inventory-only, not committed.

## Do not commit list

- `_migration_proposals/hermesops_selective_migration/**`
- `assets/legacy/Laravel/**`
- `assets/static/**`
- `docs/audit/screenshots/**`
- any `data/*.db-wal` / `data/*.db-shm` runtime database leftovers
- any file with a secret, token, credential, cookie, or storage state marker

## Candidate future boundaries

- `BASE44-FRONTONLY-H1`
- `LEGACY-ASSETS-H1`
- `MIGRATION-PROPOSALS-H1`

## Recommendation

Keep the documentation text for boundary planning, leave the large legacy trees on disk but out of Git, and continue to the Base44 visual import only after the worktree remains clean of tracked cross-boundary changes.
