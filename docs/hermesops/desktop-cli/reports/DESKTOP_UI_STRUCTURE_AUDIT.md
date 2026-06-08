# Desktop UI Structure Audit

## What the audit looked at

- `apps/desktop/src/app/settings/index.tsx`
- `apps/desktop/src/app/settings/types.ts`
- `apps/desktop/src/app/settings/primitives.tsx`
- `apps/desktop/src/app/settings/mcp-settings.tsx`
- `apps/desktop/src/app/settings/providers-settings.tsx`
- `apps/desktop/src/app/command-center/index.tsx`
- `apps/desktop/src/app/routes.ts`
- `apps/desktop/src/styles.css`

## Structure notes

- The desktop already uses overlay-style settings pages, so the safest entry point for HermesOps was a new settings section rather than a brand-new shell route.
- The sidebar already supports nested views and deep-linkable tabs, which matches the requested dashboard/plugins/composio/logs split.
- The existing theme system is token-driven, so the dark-mode fix could be done in CSS variables instead of per-component overrides.

## Relevant findings

- HermesOps did not previously have a visual entry in the settings sidebar.
- Composio was CLI-visible but not exposed as a dedicated desktop panel.
- The app already had enough structure to add a read-only operational panel without introducing a new IPC surface.

## Evidence

- `reports/hermes_desktop_mod/evidence/desktop_file_map.txt`
- `reports/hermes_desktop_mod/evidence/desktop_search_hits.txt`

