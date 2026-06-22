# BASE44-VISUAL-RECOVERY-H1 — Visual Audit

## Status

RELEASE_BLOCKED_BY_MANUAL_VISUAL_VALIDATION

## Technical baseline

- Frontend build passed before and after the visual fix.
- Python test suite passed before and after the visual fix.
- `npm run build` completed successfully.
- `python -m unittest discover -s tests` completed successfully.
- Runtime smoke on the local app already showed route reachability on `http://127.0.0.1:18086`, but manual visual inspection still found the UI broken.

## Evidence captured

Temporary evidence was written only under `/tmp/base44_visual_recovery_h1/`:

- screenshots: `/tmp/base44_visual_recovery_h1/screenshots`
- DOM snapshots: `/tmp/base44_visual_recovery_h1/dom`
- logs: `/tmp/base44_visual_recovery_h1/logs`

Representative captures reviewed:

- `desktop__login__before-login.png`
- `mobile__login__before-login.png`
- `desktop__root__authenticated.png`
- `mobile__root__authenticated.png`

Notes:

- The login desktop capture showed the hero and form stacked as a single block, not as the intended two-column Base44 composition.
- The mobile login capture was more coherent than desktop, but still looked visually washed and low-fidelity versus the intended Base44 shell.
- Browser replay against the temporary 4174 proxy remained blocked by auth/API errors during screenshot collection, so the strongest evidence is the direct 18086 visual capture plus source inspection.

## Route visual score

| Route | Desktop score | Mobile score | Classification | Main issue | Fix priority |
|---|---:|---:|---|---|---|
| `/login` | 1 | 2 | VISUAL_IMPORTED_BUT_BROKEN | Desktop login shell rendered as a stacked block; hero/card hierarchy was weak | P0 |
| `/` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Route smoke existed, but visual capture was blocked by auth/proxy errors | P1 |
| `/assets` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked; route smoke existed | P1 |
| `/assets/<id>` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Asset detail capture was not obtained in the final visual pass | P1 |
| `/audit-logs` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P1 |
| `/imports` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P1 |
| `/settings` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P1 |
| `/macros` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P1 |
| `/users` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P1 |
| `/signatures` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P1 |
| `/ai-chat` | 0 | 0 | NOT_VISUALLY_REVALIDATED | Visual capture blocked | P2 |
| `404` | 1 | 1 | VISUAL_PARTIAL_SKIN_ONLY | Basic shell exists but still reads as a generic empty page | P2 |

## Base44 source comparison

- The app already had a Base44 component layer and Base44 page wrappers in place.
- The login page used `Base44Surface`, `Base44PageHeader`, `Base44ShellAccent`, and `Base44StatusBadge`, but the resulting layout still presented as a vertically stacked block in the browser capture.
- The global stylesheet contained the Base44 visual layer, but the runtime visual result showed the login shell not behaving like the intended Base44 two-column composition.
- Route-level Base44 wrappers on the main pages were present; the audit did not find evidence that the base API/auth/permissions contracts were replaced.

## Active implementation findings

- `AppShell` already renders the Base44 sidebar/topbar layout for authenticated routes.
- Main pages already use reusable Base44 wrappers for metrics, cards, panels, and empty states.
- The visible regression was concentrated in the shell composition and login presentation, not in backend logic.

## Root causes

1. Desktop login composition was visually broken in the runtime capture: the hero and form did not appear as a strong two-column Base44 entry screen.
2. The shell hierarchy was too dependent on CSS/layout behavior that the served runtime was not honoring cleanly during validation.
3. The temporary proxy path used for browser replay hit auth/API errors, so the visual validation path was not fully reliable for route-by-route confirmation.

## P0 visual regressions

- Login shell composition on desktop.
- Insufficient visual separation between hero and form.
- Stacked/flat presentation that undermined the Base44 import fidelity.

## P1 visual gaps

- Route-by-route visual replay could not be completed on the proxy path.
- Authenticated route screenshots were not stable enough to compare visually.

## P2 polish

- Login card density and spacing can still be refined after the shell is fully stable.
- 404 page can be made more intentionally branded once the shell is fully trusted.

## Do not change

- Backend/API contracts.
- Auth logic.
- RBAC/permissions.
- Feature flags.
- Routes.
- Database/migrations.
- Docker/Compose.
- Package files.
- Base44 runtime imports or entity JSON files.

## Correction plan

1. Force the login/not-found shell composition to honor the intended layout in the served CSS bundle.
2. Rebuild the frontend and retest the visual shell in the browser.
3. If the proxy path remains unstable, keep the real backend/app behavior unchanged and continue with targeted visual-only repairs page by page.
4. Re-check the authenticated routes once the login shell is visually stable.
