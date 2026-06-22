# BASE44-FRONTONLY-H4 — Macros / Users / Remaining Operational Pages Component Map

## Status

Visual-only adaptation completed for the routed operational pages in scope.

## Rule

Base44 remains visual source only. Active ENS frontend remains source of truth for API, routing, auth, permissions and data contracts.

## Mapping

| Base44 source | Active target | Action | Preserved logic |
|---|---|---|---|
| Macro visual | MacrosPage.tsx | adapt visual only | active macro API/generation/copy |
| User visual | UsersPage.tsx | adapt visual only | active users API/roles/permissions |
| Stock visual | StockPage.tsx | adapt visual only | active API/contracts |
| Signatures visual | SignaturesPage.tsx | adapt visual only | active signature generation/download |
| Macro preview | Base44MacroPreview | create visual component | active generated content |
| Macro panel | Base44MacroPanel | create visual component | active generation/copy handlers |
| User card | Base44UserCard | create visual component | active user data |
| User role badge | Base44UserRoleBadge | create visual component | active roles/permissions |
| Operational grid | Base44OperationalGrid | create visual component | active data only |
| Copy block | Base44CopyBlock | create visual component | preview/copy content |

## Explicitly not imported

- base44Client.js
- AuthContext.jsx
- query-client.js
- entities/*.json
- mock users
- mock macros
- mock stock
- mock signatures
- mock movements
