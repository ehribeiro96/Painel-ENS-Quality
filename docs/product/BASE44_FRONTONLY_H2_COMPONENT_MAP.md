# BASE44-FRONTONLY-H2 — Assets Component Map

## Status

In progress / visually adapted.

## Rule

Base44 remains visual source only. Active ENS frontend remains source of truth for API, routing, auth, permissions and data contracts.

## Mapping

| Base44 source | Active target | Action | Preserved logic |
|---|---|---|---|
| Assets page visual | AssetsPage.tsx | adapt visual only | active API/list/search/pagination |
| Asset detail visual | AssetDetailsPage.tsx | adapt visual only | active detail/history/movement/macro |
| Status badges | Base44StatusBadge / AssetsPage | reuse/adapt | active asset status |
| Cards/grid | Base44AssetCard / Base44Surface | create/reuse | active asset data |
| Timeline/history | Base44AssetTimeline | create visual component | active asset history |
| Detail info layout | Base44InfoGrid | create visual component | active asset fields |
| Action header | Base44ActionBar | create visual component | active handlers |

## Explicitly not imported

- base44Client.js
- AuthContext.jsx
- query-client.js
- entities/*.json
- mock assets
- mock movements
