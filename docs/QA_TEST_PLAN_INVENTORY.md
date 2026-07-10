# QA Test Plan - Inventory and Collaborators

## Build and Runtime Checks

- [x] `npm run build` passes with Linux Node in WSL.
- [x] Local runtime responds on `/`, `/assets`, and `/users`.

## Inventory Test Cases

1. Verify `/assets` renders summary cards.
2. Verify `/assets` shows permission banner for write and read-only roles.
3. Verify filter bar still works with search, status, type, location and availability.
4. Verify empty table shows actionable empty state.
5. Verify create/edit buttons remain hidden for read-only users.
6. Verify delete action remains visible only for `ADMIN`.
7. Verify row actions still include detail, edit, move, stock and history.

## Collaborator Test Cases

1. Verify `/users` renders summary cards.
2. Verify `/users` shows consultation notice for read-only users.
3. Verify search still filters the list.
4. Verify empty table shows a CTA to clear the search or create a collaborator.
5. Verify edit/delete actions respect role.
6. Verify manual creation does not expose authentication or role editing controls.

## Accessibility Checks

- Confirm page headers remain readable on narrow viewports.
- Confirm summary cards do not overlap filter controls.
- Confirm empty states still provide keyboard-focusable buttons.
- Confirm topbar access mode chip is visible but not noisy.

## Regression Checks

- Shell navigation remains intact.
- Global search remains available.
- `/macros`, `/imports`, `/audit-logs`, `/settings` remain unaffected by this round.
