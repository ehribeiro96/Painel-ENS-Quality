# VISUAL-QA-FIX-H1 — Route Visual Audit

## Status

PARTIAL_VISUAL_AUDIT_ONLY

## Technical baseline

- Frontend build passed after the autocomplete fix.
- The macros route remained reachable at the local app URL.
- Browser automation for screenshot capture was blocked in this session by the browser runtime trust bridge, so full screenshot evidence was not collected here.

## Screenshot evidence

- Not captured in this session.
- Reason: in-app browser automation runtime was unavailable/trusted-bridge blocked.

## Route visual score before

| Route | Desktop score | Mobile score | Classification | Main visual bug | Priority |
|---|---:|---:|---|---|---|
| `/macros` | N/A | N/A | VISUAL_LAYOUT_MISMATCH | Autocomplete panel could be clipped by the Base44 panel overflow and used an unreadable light dropdown theme inside a dark workbench. | P1 |

## Classifications

- VISUAL_BROKEN
- VISUAL_PARTIAL_SKIN_ONLY
- VISUAL_LAYOUT_MISMATCH
- VISUAL_RESPONSIVE_BROKEN
- VISUAL_CLOSE_TO_BASE44
- FUNCTIONAL_REGRESSION_SUSPECTED

## Root causes

- The macro autocomplete dropdown was styled as a light floating box inside a dark Base44 panel.
- The surrounding Base44 macro panel used `overflow: hidden`, which can clip the dropdown.
- The autocomplete panel did not behave like a true dropdown overlay.

## P0 bugs

- None confirmed in this session.

## P1 bugs

- Autocomplete dropdown visibility and layering in `/macros`.

## P2 polish

- Further visual tuning of suggestion spacing and density after manual screenshot review.

## Fix plan

- Make the autocomplete dropdown overlay sit above the panel content.
- Use dark-theme dropdown styling consistent with the rest of the macros workspace.
- Keep autocomplete behavior, API contract, and generation flow unchanged.

## Do not change

- Backend autocomplete API.
- Macro generation flow.
- Copy-to-clipboard flow.
- Import, auth, permissions, and other routes.
