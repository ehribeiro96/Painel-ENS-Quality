# CLOSE-ASSETDETAILS-DIRTY-H1 — AssetDetails Dirty File Report

## Status
GO_ASSETDETAILS_DIRTY_CLOSED

## Context
`frontend/itam-platform/src/pages/AssetDetailsPage.tsx` remained modified after the previous visual QA boundary and had to be reviewed in isolation before any further work.

## Diff classification
VISUAL_ONLY_ASSETDETAILS_CHANGE

## What changed
- Added a small formatter to display `last_login` more consistently when the source value is an Excel serial number.
- Kept page structure, API usage, auth, permissions, and movement/macro flows unchanged.

## What did not change
- No backend contract changes.
- No changes to `src/lib/*`.
- No changes to movement or macro generation/copy flows.
- No changes to package files, Docker, or migrations.

## Risk analysis
The change is localized to display formatting on AssetDetails and uses a safe fallback to the existing datetime formatter. It does not add new state or data paths.

## Validation
- Frontend build passed.
- Backend test suite passed.
- `git diff --check` passed.

## Decision
Commit the isolated AssetDetails visual adjustment.

## Next boundary
VISUAL-QA-FIX-H2 — continue page-specific visual repair
