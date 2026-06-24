# Apoema Only Target Architecture - 2026-06-23

## 1. Goal
Describe Apoema as the consolidation target for the Painel ENS-Quality frontend without changing runtime code in this task.

## 2. Entry path
- `frontend/itam-platform/src/App.tsx` lazy-loads `ApoemaApp`
- `frontend/itam-platform/src/apoema/index.ts` exports `ApoemaApp`
- `frontend/itam-platform/src/apoema/ApoemaApp.tsx` owns the route subtree

## 3. Route tree
```
/apoema/*
  /apoema/dashboard
  /apoema/assets
  /apoema/chat
  /apoema/integrations
  /apoema/settings

/apoema-preview/*
  same tree as /apoema/*
```

## 4. Shell composition
- Left sidebar for navigation
- Top bar for mode and context
- Right rail for status and safety cues
- Main panel for the selected page

## 5. Apoema source boundaries
| file | role | note |
|---|---|---|
| `src/apoema/ApoemaApp.tsx` | local router and shell | owns the isolated experience |
| `src/apoema/styles/apoema.css` | scoped visual system | keeps styling away from the root shell |
| `src/apoema/lib/apoemaChatApi.ts` | API adapter | separates HTTP errors from network fallback |
| `src/apoema/types.ts` | typed contract | defines provider, chat, and error kinds |
| `src/apoema/mockApi.ts` | offline fallback content | allowed only when backend is unavailable |
| `src/apoema/pages/*` | Apoema views | dashboard, assets, chat, integrations, settings |

## 6. Architecture decisions already present
- Apoema has its own theme mode and visual isolation.
- Apoema uses a dedicated chat adapter instead of the generic root API client.
- The chat adapter classifies `401`, `403`, `422`, `429`, `5xx`, and network failure separately.
- Fallback content is visually marked as fallback, not as live AI output.
- `/apoema-preview/*` is an alias to the same target tree, not a separate product.

## 7. What should stay out of the target boundary
- Root compatibility pages under `src/pages/*`
- `AppShell` and the Base44 compatibility layer
- `components/brand`
- `components/ai-chat`
- `frontend/legacy`
- imported/exported snapshots under `_validation`, `exports`, and `imports`

## 8. Consolidation principle
If a feature must live in the target experience, it should be expressed in Apoema first. The root shell should only keep what is required for compatibility, migration staging, or legacy support.

## 9. Practical target rules
- Keep auth/session handling shared, not duplicated.
- Keep API fallback explicit and limited to real network failure.
- Keep styling scoped under `.apoema-root`.
- Keep route aliases aligned between `/apoema/*` and `/apoema-preview/*`.
- Keep the target UI readable and operational, not marketing-led.
