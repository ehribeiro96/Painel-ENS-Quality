# MACRO-H1B — Build and Runtime Revalidation

## Context

- Date/time: `2026-06-16T22:37:00-03:00`
- Branch: `main`
- Boundary: `MACRO-H1B — frontend build/runtime unblock and revalidation`
- Scope: unblock frontend build/runtime validation after `8241f00 fix(macros): keep post-movement macro copy flow visible`

## What was revalidated

- The active shell was not using a Linux `node` executable by default.
- A Linux Node.js runtime was available via `~/.nvm/versions/node/v22.22.3/bin/node`.
- The frontend dependencies were reinstalled with `npm ci` using the Linux Node runtime.
- `package-lock.json` remained unchanged.
- The frontend build completed successfully.
- The backend served the freshly built bundle from `frontend/itam-platform/dist`.

## Build result

- `npm ci`: passed
- `npm run build`: passed
- Output bundle generated under `frontend/itam-platform/dist`

## Runtime revalidation result

- The login page rendered correctly in a local headless Chrome session.
- The root route redirected to `/login` when no authenticated session was present.
- The authenticated macro flow could not be fully repeated in this boundary because no local admin session was available in the current environment.
- No secret values were printed or recorded.

## Limitations observed

- The Windows Chrome headless session could be started with DevTools, but the runtime lacked an authenticated session cookie.
- `ADMIN_PASSWORD` was not present in the current shell environment.
- The macro visibility and copy flow remain functionally fixed in the committed frontend code, but this boundary only revalidated the build and the unauthenticated runtime surface.

## Conclusion

The frontend build/runtime unblock succeeded at the environment level. The UI runtime recheck is only partial because the authenticated UAT flow could not be replayed in this session.
