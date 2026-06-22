# BASE44-VISUAL-RECOVERY-H1 — Fix Report

## Status

PARTIAL_VISUAL_RECOVERY_NEEDS_MANUAL_REVIEW

## Root cause confirmed

The desktop login shell was not presenting the intended Base44 two-column composition during visual validation. The runtime capture showed the hero and form stacked as a single block, which made the imported shell look generic and incomplete.

## Fixes applied

- Tightened the login/not-found shell CSS so the intended centered layout is forced in the final bundle.
- Added a width constraint to the login shell to keep the desktop composition from stretching too far.
- Preserved all backend/auth/API/permission behavior unchanged.

## Files changed

- `frontend/itam-platform/src/styles.css`
- `docs/product/BASE44_VISUAL_RECOVERY_H1_AUDIT.md`
- `docs/product/BASE44_VISUAL_RECOVERY_H1_FIX_REPORT.md`
- `docs/audit/BASE44_VISUAL_RECOVERY_H1_EXECUTIVE_SUMMARY.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`

## Visual score before/after

| Route | Before | After | Status |
|---|---:|---:|---|
| `/login` | 1 | 1 | PARTIAL |
| `/` | 0 | 0 | NOT_REVALIDATED |
| `/assets` | 0 | 0 | NOT_REVALIDATED |
| `/audit-logs` | 0 | 0 | NOT_REVALIDATED |
| `/imports` | 0 | 0 | NOT_REVALIDATED |
| `/settings` | 0 | 0 | NOT_REVALIDATED |
| `/macros` | 0 | 0 | NOT_REVALIDATED |
| `/users` | 0 | 0 | NOT_REVALIDATED |
| `/signatures` | 0 | 0 | NOT_REVALIDATED |
| `/ai-chat` | 0 | 0 | NOT_REVALIDATED |
| `404` | 1 | 1 | PARTIAL |

## Functional preservation

- Backend untouched.
- Auth untouched.
- RBAC/permissions untouched.
- API client untouched.
- Routes unchanged.
- No migrations or Docker changes.

## Build/test validation

- `npm run build` ✅
- `python -m unittest discover -s tests` ✅

## Browser smoke

- Direct authenticated smoke on `http://127.0.0.1:18086` had already passed earlier in this boundary.
- Temporary screenshot replay on the proxy path remained blocked by auth/API errors, so the visual recovery remains partial and needs manual review.

## Remaining gaps

- Authenticated route screenshots were not stable enough to complete the route-by-route visual comparison.
- The proxy-based browser replay needs a follow-up validation pass.

## Next boundary

BASE44-VISUAL-RECOVERY-H2 — targeted page-by-page visual repair
