# BASE44-FRONTONLY-H1 — Component Map

## Status

Implemented as a first visual-only import boundary.

## Rule

Base44 is visual source only. Active ENS frontend remains source of truth for auth, API, routing, permissions and data contracts.

## Mapping

| Base44 source | Active target | Action | Notes |
|---|---|---|---|
| Layout.jsx | AppShell.tsx / components/base44 | adapt visual only | preserve active routes/auth |
| Sidebar.jsx | AppShell.tsx / components/base44 | adapt visual only | preserve current navigation |
| Topbar.jsx | AppShell.tsx / components/base44 | adapt visual only | preserve current user/logout flow |
| PageHeader.jsx | Base44PageHeader.tsx | adapt | visual component |
| EmptyState.jsx | Base44EmptyState.tsx | adapt | visual component |
| StatusBadge.jsx | Base44StatusBadge.tsx | adapt | visual component |
| Dashboard page | DashboardPage.tsx | adapt visual only | use current API/query/data |
| Login visual | LoginPage.tsx | adapt visual only | use current auth |
| PageNotFound.jsx | NotFoundPage.tsx | adapt visual only | preserve route behavior |

## Explicitly not imported

- base44Client.js
- AuthContext.jsx
- query-client.js
- entities/*.json
- mock data
