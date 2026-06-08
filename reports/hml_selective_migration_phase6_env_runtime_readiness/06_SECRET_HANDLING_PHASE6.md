# Phase 6 Secret Handling

## Git handling
- `infra/hermesops/.env.hml` is ignored by Git.
- `infra/hermesops/.env.hml.example` remains versionable.

## Scan results
- The versionable-content scan returned only placeholder-sensitive matches.
- Allowed placeholders observed:
  - `POSTGRES_PASSWORD=CHANGE_ME_DO_NOT_COMMIT`
  - `COMPOSIO_API_KEY=DO_NOT_COMMIT_REAL_VALUE`

## Important note
- No real `.env.hml` values were printed.
- No real secret was introduced into tracked files.

## Conclusion
- Secret handling is acceptable for a runtime-ready local config, with the real env kept outside Git.
