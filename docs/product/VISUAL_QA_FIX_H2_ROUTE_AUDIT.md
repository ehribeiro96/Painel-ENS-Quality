# VISUAL-QA-FIX-H2 — Route Visual Audit

## Status
RELEASE_BLOCKED_BY_VISUAL_QA

## Technical baseline
- `npm run build`: OK
- `python -m unittest discover -s tests`: OK
- `git diff --check`: OK

## Screenshot evidence before
- Evidence captured under `/tmp/visual_qa_fix_h2/screenshots_before`.
- Mobile pages showed an oversized stacked shell with decorative blocks and footer content consuming too much vertical space before the main route content.
- Desktop pages were generally coherent and close to the Base44 aesthetic.

## Route visual score before

| Route | Desktop score | Mobile score | Classification | Main visual bug | Priority |
|---|---:|---:|---|---|---|
| `/login` | 4 | 4 | VISUAL_CLOSE_TO_BASE44 | Login shell readable and consistent | P2 |
| `/` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Mobile shell too tall; content pushed below fold | P1 |
| `/assets` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Mobile shell too tall; inventory content too far down | P1 |
| `/audit-logs` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/imports` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/settings` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/macros` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/users` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/signatures` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/stock` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `/ai-chat` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |
| `404` | 4 | 4 | VISUAL_CLOSE_TO_BASE44 | Not-found state is clean | P2 |
| `/assets/<id>` | 4 | 3 | VISUAL_LAYOUT_MISMATCH | Same mobile shell crowding | P1 |

## Root causes
- The Base44 shell stacked into a full-height column on small screens, which left decorative hero/footer blocks above the actual page content.
- The mobile sidebar kept shell accent and footer sections that duplicated information already present in the top bar.

## P0 bugs
- None confirmed.

## P1 bugs
- Mobile shell consumed too much vertical space and pushed actual page content too far below the fold across the main authenticated routes.

## P2 polish
- Desktop shell and login surfaces were already coherent.

## Fix plan
- Reduce mobile shell vertical weight.
- Remove duplicated decorative footer/accent sections on smaller screens.
- Preserve desktop layout and all functional contracts.

## Do not change
- Backend, auth, API, permissions, imports, macro generation/copy, migrations, package files, or any route contract.
