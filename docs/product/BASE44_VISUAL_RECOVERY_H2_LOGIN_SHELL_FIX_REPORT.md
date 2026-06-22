# BASE44-VISUAL-RECOVERY-H2 — Login/Shell Fix Report

## Status

PARTIAL_LOGIN_SHELL_NEEDS_MANUAL_REVIEW

## Root cause

The login shell and authenticated shell were too dependent on CSS-only behavior. In the live browser, the desktop login entry point still read as a stacked block in H1, while the mobile shell needed a responsive path that could preserve readability without collapsing the design.

## Fixes applied

- Added explicit runtime-safe grid styles to `LoginPage.tsx` so the login composition always renders as the intended two-column desktop shell.
- Added explicit runtime-safe grid styles to `AppShell.tsx` so the authenticated shell keeps the Base44 sidebar/topbar structure stable.
- Switched the grid templates to CSS-variable-driven values so the mobile breakpoint can stack cleanly without fighting inline desktop styles.
- Updated the Base44 shell breakpoint rules in `styles.css` to set the responsive grid variables instead of replacing the inline layout.
- Preserved `NotFoundPage.tsx` and the Base44 surface components without changing auth or data behavior.

## Files changed

- `frontend/itam-platform/src/pages/LoginPage.tsx`
- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/styles.css`

## Visual score before/after

| Surface | Before | After | Status |
|---|---:|---:|---|
| /login desktop | 1 | 4 | IMPROVED |
| /login mobile | 2 | 3 | IMPROVED |
| shell desktop | 1 | 4 | IMPROVED |
| shell mobile | 1 | 3 | IMPROVED |
| not found | 1 | 2 | ACCEPTABLE |

## Screenshots

Temporary captures only, not versioned:

- `/tmp/base44_visual_recovery_h2/screenshots_before/desktop__login__before-login.png`
- `/tmp/base44_visual_recovery_h2/screenshots_before/mobile__login__before-login.png`
- `/tmp/base44_visual_recovery_h2/screenshots_after/desktop__login__before-login.png`
- `/tmp/base44_visual_recovery_h2/screenshots_after/mobile__login__before-login.png`
- `/tmp/base44_visual_recovery_h2/screenshots_after/desktop__root__authenticated-home.png`
- `/tmp/base44_visual_recovery_h2/screenshots_after/mobile__root__authenticated-home.png`
- `/tmp/base44_visual_recovery_h2/screenshots_after/desktop__not-found-test__404.png`
- `/tmp/base44_visual_recovery_h2/screenshots_after/mobile__not-found-test__404.png`

## Functional preservation

- Backend unchanged.
- Auth flow unchanged.
- RBAC/permissions unchanged.
- API client unchanged.
- Routes unchanged.
- No migrations or Docker changes.

## Build/test validation

- `npm run build` ✅
- `python -m unittest discover -s tests` ✅

## Remaining gaps

- The authenticated shell is visually stable on desktop, but the mobile experience is still dense and should be manually reviewed.
- The proxy-based 4180 path remained noisy with auth refresh failures, so the direct app path was the reliable validation source.

## Next boundary

BASE44-VISUAL-RECOVERY-H3 — targeted page-by-page visual repair
