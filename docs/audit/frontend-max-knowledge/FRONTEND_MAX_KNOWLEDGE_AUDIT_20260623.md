# Frontend Max Knowledge Audit - 2026-06-23

## 1. Status
GO

## 2. Scope
- Active frontend inventory
- Apoema consolidation target
- Legacy shell and compatibility surfaces
- Imported and exported frontend snapshots
- Risk classification for frontend noise

## 3. Executive summary
The active product frontend is `frontend/itam-platform`. Inside that app, `Apoema` is the best consolidation target because it already has an isolated shell, scoped CSS, its own route subtree, and its own AI chat adapter with explicit fallback boundaries.

The root shell still owns a wider compatibility surface: `src/pages/*`, `AppShell`, `base44`, `brand`, `ai-chat`, and the shared global stylesheet. Those areas are active, but they are not the long-term target shape for the product UX.

Most of the remaining frontend noise comes from frozen snapshots, exported release copies, imported external projects, and a legacy Laravel frontend archive. Those should stay in the audit trail, but they should not be treated as product target code.

## 4. Knowledge summary
| item | value |
|---|---|
| Active source frontend files | 103 |
| Apoema files | 23 |
| Root pages | 15 |
| Root components | 38 |
| Current app entrypoints | `src/main.tsx`, `src/App.tsx` |
| Apoema entrypoint | `src/apoema/index.ts` |

## 5. Frontend inventory
| surface | classification | evidence | conclusion |
|---|---|---|---|
| `frontend/itam-platform` | active product frontend | `package.json`, `vite.config.ts`, `src/main.tsx`, `src/App.tsx` | this is the build and runtime target |
| `frontend/itam-platform/src/apoema` | target experience | isolated shell, scoped CSS, custom chat API | primary consolidation target |
| `frontend/itam-platform/src/pages` | compatibility shell | root routes and legacy operational pages | active, but not the final target shape |
| `frontend/itam-platform/src/components/base44` | legacy compatibility layer | Base44-prefixed shared UI pieces | retain while migrating, then trim |
| `frontend/itam-platform/src/components/brand` | legacy brand layer | Hermes/Sentinel branded shell pieces | support only |
| `frontend/itam-platform/src/components/ai-chat` | legacy AI chat UI | old ` /ai-chat` surface | support only |
| `frontend/itam-platform/src/components/icons` | shared icon plumbing | Hermes SVG pack | asset plumbing, not target UX |
| `assets/legacy/Laravel` | legacy archive frontend | its own `package.json` and `vite.config.js` | keep as archive/reference |
| `imports/HermesOps-Final-Transfer/releases/20260608-091540/hermes-agent-hermesops` | imported external frontend bundle | multiple apps and a `web` frontend | reference/imported source only |
| `exports/final_release_candidate_v2_staging` | frozen export snapshot | `frontend/itam-platform` copy | read-only evidence |
| `exports/final_release_candidate_v2_1_staging` | frozen export snapshot | `frontend/itam-platform` copy | read-only evidence |
| `_validation/rc2_cleanroom_20260608` | validation snapshot | `frontend/itam-platform` copy | read-only evidence |
| `_validation/rc21_cleanroom_20260608` | validation snapshot | `frontend/itam-platform` copy | read-only evidence |
| `frontend/legacy` | empty placeholder | no files found | no product role |

## 6. Route ownership
- Root compatibility shell: `/`, `/assets`, `/assets/:id`, `/users`, `/users/:id`, `/assignments`, `/stock`, `/imports`, `/macros`, `/ai-chat`, `/signatures`, `/audit-logs`, `/settings`
- Auth route: `/login`
- Apoema target routes: `/apoema/*`, `/apoema-preview/*`, plus nested `dashboard`, `assets`, `chat`, `integrations`, `settings`
- Fallback route: `*`

## 7. Main conclusion
Apoema is the unique target candidate for consolidation because it already owns:
- an isolated shell
- its own route subtree
- scoped styling
- explicit chat fallback contracts
- preview and production aliases

The root shell is still broad and useful for compatibility, but it should be treated as the legacy support layer while Apoema becomes the center of gravity.

## 8. Recommendation
Use Apoema as the canonical UX target for new operational work. Keep the root shell only as a compatibility layer until its routes are either migrated or intentionally retired.
