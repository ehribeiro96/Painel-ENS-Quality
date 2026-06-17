# MACRO-H1B — UAT Recheck

## Scope

Recheck the post-movement macro flow after the frontend build was revalidated.

## Result

- The frontend served the updated build successfully.
- The login page loaded normally.
- The unauthenticated root route redirected to `/login`.
- The asset flow could not be re-run end-to-end because the local environment did not provide an authenticated UAT session.

## Evidence collected

- `http://127.0.0.1:8000/login` rendered with the expected Sentinel login surface.
- `http://127.0.0.1:8000/` redirected to `/login` when accessed without a session.
- No session cookies were present in the headless browser profile used for the check.

## Blocker

- The current shell environment did not expose the local admin password.
- Without an authenticated session, the movement modal, macro visibility, and copy button could not be exercised again in this boundary.

## Decision

`PARTIAL_RUNTIME_RECHECK_BLOCKED`
