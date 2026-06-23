# Legacy and Artifact Boundary — 2026-06-23

## Status
PARTIAL_GO

## Objective
Definir uma boundary final para legado, evidências, exports e relatórios locais sem apagar, mover ou mascarar arquivos manualmente.

## Inputs reviewed
- Triagem anterior de untracked risk
- Sanitization plan for P0 candidates
- Current `.gitignore`
- Post-boundary untracked inventory

## Before / after snapshot
- Untracked before this boundary: 714
- Untracked after ignore update: 625
- Trackable risk reduced by ignore rules, but legacy/reference inventory remains intentionally visible for review.

## Policy summary by group

| Group | Classification | Runtime needed | Versioning policy | Boundary action |
|---|---|---:|---|---|
| `_migration_proposals/` | MIGRATION_PROPOSAL | no | MANUAL_REVIEW | Keep untracked until a human approves promotion |
| `assets/legacy/Laravel/` | LEGACY_REFERENCE | yes | TRACK_SANITIZED | Keep as reference; do not auto-delete or auto-ignore the whole tree |
| `assets/legacy/*.map`, `assets/legacy/*.js.map` | SOURCE_MAP | no | IGNORE_LOCAL | Ignore generated source maps in legacy assets |
| `exports/`, `data/exports/` | LOCAL_EXPORT | no | IGNORE_LOCAL | Ignore local export dumps |
| `_validation/` | LOCAL_VALIDATION | no | IGNORE_LOCAL | Ignore validation outputs |
| `reports/` | LOCAL_REPORT | no | IGNORE_LOCAL | Ignore local report outputs |
| `docs/audit/screenshots/`, `docs/apoema-visual-qa/screenshots/` | VISUAL_EVIDENCE | no | IGNORE_LOCAL | Ignore transient screenshot evidence in repo workspace |
| `docs/apoema-visual-qa/*.pid` | CACHE | no | IGNORE_LOCAL | Ignore helper process markers |
| `docs/audit/*.csv`, `docs/audit/PROJECT_TREE.txt`, `docs/audit/FILE_CLASSIFICATION.csv` | LOCAL_REPORT | no | TRACK_SANITIZED | Review before versioning; keep sanitized if promoted |
| `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` | LARGE_BINARY_ASSET | no | EXTERNAL_STORAGE | Keep out of Git unless explicitly sanitized and approved |
| `_cleanup_backup_manifest.md`, `*_backup_manifest.md` | LOCAL_BACKUP_MANIFEST | no | IGNORE_LOCAL | Ignore backup manifests |

## `.gitignore` changes made
- `_cleanup_backup_manifest.md`
- `*_backup_manifest.md`
- `data/exports/`
- `docs/audit/screenshots/`
- `docs/apoema-visual-qa/screenshots/`
- `docs/apoema-visual-qa/*.pid`

## Validation result
- The added ignore rules correctly match local dummy validation paths and the intended artifact directories.
- Legacy env-example files remain intentionally visible for manual review due to the existing `.env.example` exception.
- The policy intentionally does not auto-delete any legacy or artifact file.

## Remaining risk
- `assets/legacy/Laravel/` still contains many files that may be intentionally versionable as historical reference.
- Large binary evidence such as `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` remains untracked and should be moved to external storage only if the team approves that workflow.
- `_migration_proposals/` remains a review queue and should not be auto-promoted.

## Recommendation
Keep the current ignore additions, do not broaden them to the full legacy tree, and review versioning decisions directory by directory when human approval is available.

## Next phase
Human review of legacy reference promotion and explicit decision on whether docs/audit CSVs and static binary evidence should be versioned or kept outside Git.
