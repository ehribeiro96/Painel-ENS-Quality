# Frontend Consolidation Roadmap - 2026-06-23

## 1. Objective
Consolidate the product around Apoema without deleting archives, snapshots, or compatibility layers during this audit.

## 2. Recommended sequence
1. Keep Apoema as the canonical target surface for new operational UI.
2. Preserve root shell compatibility while routes still depend on it.
3. Move repeated operational patterns into Apoema or shared typed helpers.
4. Reduce the global CSS and compatibility component footprint.
5. Retire legacy route ownership only after parity is confirmed.
6. Keep snapshots and imported projects as evidence, not as target inputs.

## 3. Route migration order
| order | route family | reason |
|---|---|---|
| 1 | `/apoema/*` and `/apoema-preview/*` | already isolated and closest to the target shape |
| 2 | `/ai-chat` | overlaps with Apoema chat concerns and error handling |
| 3 | `/assets` and `/assets/:id` | core operational inventory surface |
| 4 | `/imports` | operational workflow with explicit guards |
| 5 | `/macros` | workflow surface used by support users |
| 6 | `/users` and `/users/:id` | shared identity/asset context |
| 7 | `/signatures` | supporting operational module |
| 8 | `/assignments` | movement workflow surface |
| 9 | `/audit-logs` | admin support surface |
| 10 | `/settings` | configuration surface |

## 4. Consolidation constraints
- No code deletion in this audit.
- No backend changes in this audit.
- No push in this audit.
- Preserve compatibility until target parity exists.
- Keep fallback behavior explicit, not silent.

## 5. Architectural cleanup priorities
| priority | item | why |
|---|---|---|
| high | isolate root shell globals | reduces cross-surface regressions |
| high | keep Apoema chat error contract explicit | avoids masking auth/API failures |
| medium | reduce `src/styles.css` coupling | large global CSS is the main styling risk |
| medium | decide the future of `components/base44` | compatibility UI can become dead weight |
| medium | reduce dependency on imported snapshots | keeps planning focused on the active product |
| low | archive legacy frontends with clear labels | preserves history without confusing the target |

## 6. Target state
The end state should be:
- one clear product target: Apoema
- one compatibility shell only as needed during migration
- one shared auth/session layer
- one explicit chat error model
- one scoped visual system for the target experience

## 7. Non-goals for this audit
- Removing legacy code
- Rewriting backend contracts
- Refactoring navigation behavior
- Changing deployment topology
- Running a push
