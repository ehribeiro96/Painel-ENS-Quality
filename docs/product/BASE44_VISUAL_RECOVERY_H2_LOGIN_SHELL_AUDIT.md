# BASE44-VISUAL-RECOVERY-H2 — Login/Shell Audit

## Status

PARTIAL_LOGIN_SHELL_NEEDS_MANUAL_REVIEW

## Why release remains blocked

The release is still blocked until the login/shell recovery is visually confirmed by manual review. The desktop login entry point was the clearest regression from H1, so this boundary focused only on the foundational shell instead of page-by-page polishing.

## Evidence before fix

- H1 manual/browser evidence showed `/login` desktop as a stacked, low-fidelity shell instead of a clear two-column composition.
- H1 browser replay on the temporary proxy path was unstable, so the login shell had to be validated directly against the real app.
- In the H2 before pass, the proxy path at `http://127.0.0.1:4180` still showed a loading/refresh problem on `/login`, which confirmed the proxy path was not reliable for final visual judgment.

## Base44 source target

The Base44 source repository does not provide a dedicated login page. The visual target comes from the shell/layout primitives:

- `src/components/Layout.jsx`
- `src/components/Sidebar.jsx`
- `src/components/Topbar.jsx`
- `src/lib/PageNotFound.jsx`
- `src/components` shell cards and spacing patterns

So the target for this boundary is not a Base44 auth screen copy; it is the shell composition language: strong card hierarchy, left/right structure, dense dark command-center styling, and responsive stacking.

## Active implementation

- `LoginPage.tsx` already used Base44 wrappers, but the runtime composition still needed stronger enforcement of the desktop grid.
- `AppShell.tsx` already had the shell pieces, but the grid needed an explicit runtime-safe layout hook.
- `styles.css` already contained Base44 shell/login rules, but the responsive behavior needed a variable-driven override so the inline shell grid could remain explicit without breaking mobile.
- `NotFoundPage.tsx` already used the same Base44 surface language and did not need a separate rewrite.

## Root cause

1. The login shell was visually under-enforced at runtime; desktop fidelity depended too much on CSS-only behavior.
2. The shell layout needed explicit runtime-safe grid declarations so the browser could not collapse it into the stacked presentation seen in H1.
3. The mobile login shell needed a responsive override path that did not fight the desktop grid.
4. The authenticated shell also benefited from the same explicit grid treatment so the sidebar/topbar hierarchy stayed stable.

## Login desktop score

- Before: 1
- After: 4

## Login mobile score

- Before: 2
- After: 3

## Shell authenticated score

- Before: 1
- After: 4

## Required fixes

- Force the login shell grid at the component level.
- Keep the authenticated shell grid explicit at the component level.
- Preserve mobile stacking by using responsive CSS variables instead of hardcoding the mobile column behavior inline.
- Keep the 404 surface aligned with the same shell language.

## Fix boundaries

- LoginPage only for the login shell composition.
- AppShell only for the authenticated shell composition.
- styles.css only for shell/login responsive tokens and spacing.
- No API, auth, RBAC, routes, backend, migrations, or package file changes.

## Do not change

- `src/lib/api.ts`
- `src/lib/auth.tsx`
- `src/lib/permissions.ts`
- `src/lib/features.ts`
- backend
- migrations
- Docker/Compose
- package files
- route tree
- auth flow
- screenshots, traces, videos, storage state
- Base44 runtime imports or entities
