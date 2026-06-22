# UI-UAT-H2 — Authenticated Browser Smoke

## Status

`GO_UI_AUTHENTICATED_SMOKE_OK`

## Base URL

- Smoke runner executed against `http://127.0.0.1:4174`
- The validation used a temporary same-origin local proxy over the built frontend dist to avoid cross-origin API issues.
- The requested `4173` preview port was not usable in this session because a stale local process was already bound there.

## API bridge

- Bridge health: `http://127.0.0.1:18086/health` → `200`
- Login endpoint: `POST /api/v1/auth/login` → `200`
- No secret values were printed.

## Credential handling

- File: `/tmp/painel_runtime_h5_credentials.txt`
- Mode: `0600`
- The credential file was consumed by the runner only; no password, token, cookie, or storage state was written to the repository.

## Routes checked

- `/`
- `/assets`
- `/audit-logs`
- `/imports`
- `/settings`
- `/macros`
- `/users`
- `/signatures`
- `/ai-chat`
- Asset detail under `/assets/<id>`
- `/stock` was skipped because it was not present in the visible menu

## Results

- Login completed successfully and redirected away from `/login`.
- All checked routes rendered non-empty content.
- Asset detail opened successfully for the first visible asset link.
- No blank pages were observed.
- No render-blocking page exceptions were observed.

## Console/page errors

- None classified as critical.
- The runner ignored the expected initial unauthenticated refresh noise and only treated real browser/runtime issues as failures.

## Skips

- `/stock` → `not_in_menu`

## Risks

- The `4173` preview port was unavailable during this boundary, so the smoke used a same-origin temporary proxy on `4174` over the built dist.
- No backend, migration, Docker, or auth logic was changed to make the smoke pass.

## Next boundary

`RELEASE-H2 — final release sign-off after UI smoke`
