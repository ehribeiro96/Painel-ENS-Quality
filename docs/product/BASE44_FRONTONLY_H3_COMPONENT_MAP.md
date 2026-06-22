# BASE44-FRONTONLY-H3 — Audit / Imports / Settings Component Map

## Status

Imported visually and validated against the live ENS frontend boundary.

## Rule

Base44 remains visual source only. Active ENS frontend remains source of truth for API, routing, auth, permissions and data contracts.

## Mapping

| Base44 source | Active target | Action | Preserved logic |
|---|---|---|---|
| Audit visual | AuditLogsPage.tsx | adapt visual only | active audit API/filter/query params |
| Import visual | ImportsPage.tsx | adapt visual only | active import flow/validation/API |
| Settings visual | SettingsPage.tsx | adapt visual only | active settings/contracts |
| Filter blocks | Base44FilterPanel | create/reuse | active state and handlers |
| Audit event list/card | Base44AuditEventCard | create visual component | active audit log data |
| Import panel | Base44ImportPanel | create visual component | active import state |
| Settings sections | Base44SettingsSection | create visual component | active settings data |

## Explicitly not imported

- base44Client.js
- AuthContext.jsx
- query-client.js
- entities/*.json
- mock audit logs
- mock imports
- mock settings
