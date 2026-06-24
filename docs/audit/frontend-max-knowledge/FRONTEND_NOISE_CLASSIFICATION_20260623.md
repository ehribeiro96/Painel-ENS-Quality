# Frontend Noise Classification - 2026-06-23

## 1. Purpose
Classify frontend-related surfaces into active target, support, legacy, snapshot, imported, or empty placeholder buckets so Apoema can remain the clear target.

## 2. Classification table
| bucket | meaning | examples | action |
|---|---|---|---|
| active target | user-facing target code | `frontend/itam-platform/src/apoema` | keep and consolidate into Apoema |
| active support | still used by the current product shell | `src/pages/*`, `AppShell`, `lib/api.ts`, `lib/auth.tsx` | keep until migration finishes |
| legacy compatibility | old UI surface still in use | `components/base44`, `components/brand`, `components/ai-chat` | retain as compatibility only |
| imported external | code brought in from another project | `imports/HermesOps-Final-Transfer/.../web` | do not treat as product target |
| frozen snapshot | validation or export copy | `_validation/*`, `exports/*` | keep as evidence only |
| legacy archive | older framework/app archive | `assets/legacy/Laravel` | preserve as archive/reference |
| empty placeholder | folder without code | `frontend/legacy` | ignore for product planning |

## 3. Noise candidates
| path | reason it is noise | why it should not drive product decisions |
|---|---|---|
| `assets/legacy/Laravel` | separate legacy frontend stack | archive only, not the active React/Vite app |
| `imports/HermesOps-Final-Transfer/releases/20260608-091540/hermes-agent-hermesops` | imported bundle with multiple apps | external source, not the current product runtime |
| `_validation/rc2_cleanroom_20260608/Painel-ENS-Quality-RC/frontend/itam-platform` | frozen validation copy | useful for comparison only |
| `_validation/rc21_cleanroom_20260608/Painel-ENS-Quality-RC/frontend/itam-platform` | frozen validation copy | useful for comparison only |
| `exports/final_release_candidate_v2_staging/Painel-ENS-Quality-RC/frontend/itam-platform` | release export snapshot | useful for audit history only |
| `exports/final_release_candidate_v2_1_staging/Painel-ENS-Quality-RC/frontend/itam-platform` | release export snapshot | useful for audit history only |
| `frontend/legacy` | empty placeholder | no implementation to consolidate |
| `frontend/itam-platform/src/components/base44` | legacy compatibility UI | support layer, not target UX |
| `frontend/itam-platform/src/components/brand` | legacy brand shell | support layer, not target UX |
| `frontend/itam-platform/src/components/ai-chat` | old chat surface | support layer, not target UX |

## 4. What is not noise
- `frontend/itam-platform`
- `frontend/itam-platform/src/apoema`
- `frontend/itam-platform/src/main.tsx`
- `frontend/itam-platform/src/App.tsx`
- `frontend/itam-platform/src/lib/api.ts`
- `frontend/itam-platform/src/lib/auth.tsx`
- `frontend/itam-platform/src/apoema/lib/apoemaChatApi.ts`
- `frontend/itam-platform/src/apoema/types.ts`

## 5. Rule of thumb
If a path is part of the active React/Vite runtime and still serves users, it is not noise even when it is legacy. If a path is a snapshot, export, import, or archive, it is noise for product planning and should stay out of the target boundary.
