# Frontend Shell/UX B4-A Baseline

## Summary

Boundary `B4-A` was used to establish the baseline for the frontend shell/UX and to separate code health from environment health.

Outcome:

- `tsc -b` passes when run directly with the Windows `node.exe`.
- `vite build` fails in the current cross-runtime setup because the Windows Node runtime cannot resolve the Rollup optional package installed for the current workspace state.
- `npm run build` fails from the WSL shell because the Windows npm wrapper switches into a UNC path and then cannot resolve `tsc` from that execution context.
- No functional frontend code changes were required during this baseline pass.
- The runtime follow-up is documented in [FRONTEND_RUNTIME_NORMALIZATION_B4A2.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_RUNTIME_NORMALIZATION_B4A2.md).
- The runtime activation follow-up is documented in [FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md).

Decision:

- `GO COM RESSALVAS`
- The codebase looks structurally sound for this boundary, but the build environment still needs alignment before a clean end-to-end build can be treated as green in this shell.

## Worktree Status

Current repository state at baseline:

- branch: `main`
- upstream: `origin/main`
- ahead/behind: `main...origin/main [ahead 1]`
- staged files: none
- tracked changes: pre-existing edits outside this boundary remain in the worktree
- untracked files: pre-existing audit, import, AI chat, and frontend artifacts remain present

This baseline did not add or stage functional code.

## Environment Diagnosis

Observed execution context:

- `node` is not available on the WSL PATH.
- `npm` resolves to the Windows installation under `C:\Program Files\nodejs`.
- `npm config get script-shell` returns `null`.
- `npm config get prefix` points to the Windows roaming profile.
- `frontend/itam-platform/node_modules/.bin/tsc` exists.
- `frontend/itam-platform/node_modules/.bin/vite` exists.
- `C:\Program Files\nodejs\node.exe` exists and is callable from WSL.

Implication:

- The local shell is mixing WSL path semantics with a Windows Node runtime.
- The workspace currently has a Node module tree that is not aligned with the Windows runtime used by `vite build`.

## Baseline Commands

Executed during this boundary:

- `git status --short --branch`
- `command -v node || true`
- `command -v npm || true`
- `node --version || true`
- `npm --version || true`
- `npm config get script-shell || true`
- `npm config get prefix || true`
- `test -x node_modules/.bin/tsc && echo LOCAL_TSC_OK || echo LOCAL_TSC_MISSING`
- `test -x node_modules/.bin/vite && echo LOCAL_VITE_OK || echo LOCAL_VITE_MISSING`
- `npm pkg get scripts`
- `timeout 180 '/mnt/c/Program Files/nodejs/node.exe' ./node_modules/typescript/bin/tsc -b`
- `timeout 180 '/mnt/c/Program Files/nodejs/node.exe' ./node_modules/vite/bin/vite.js build`
- `timeout 180 npm run build`

## Build Results

### `tsc -b`

Status: `PASS`

Interpretation:

- TypeScript compilation is currently healthy.
- No frontend source edits were required to satisfy the compiler.

### `vite build`

Status: `FAIL` in the Windows Node runtime

Observed issue:

- Rollup attempted to load the Windows optional package `@rollup/rollup-win32-x64-msvc`.
- The package was not present in the current workspace install state.

Interpretation:

- This is an environment/runtime alignment issue, not a shell/UX code regression.
- The failure only appears when the build is executed through Windows Node against the current workspace dependency tree.

### `npm run build`

Status: `FAIL`

Observed issue:

- The Windows npm wrapper switched to a UNC path under WSL.
- `CMD.EXE` could not operate correctly in that path context.
- `tsc` was not resolved in that execution path.

Interpretation:

- This is the known wrapper issue that was already suspected in previous rounds.
- It is a shell/runtime problem, not a TypeScript source error.

## Shell / UX Inspection

Files reviewed for baseline context:

- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/components/StateBlocks.tsx`
- `frontend/itam-platform/src/components/icons/HermesIcons.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/pages/AuditLogsPage.tsx`
- `frontend/itam-platform/src/pages/ImportsPage.tsx`
- `frontend/itam-platform/src/pages/SettingsPage.tsx`
- `frontend/itam-platform/src/styles.css`

Observed structure:

- `AppShell` provides the main sidebar/topbar/content shell used across the frontend.
- `ImportsPage` still contains the guarded apply path, preview/staging/conflict sections, and explicit confirmation before apply.
- `AssetsPage` and `AuditLogsPage` are built around cards, badges, tables, and explicit loading/error states.
- `SettingsPage` is a simple card grid and does not introduce runtime complexity.
- `styles.css` already includes overflow control for table containers and responsive breakpoints at `1200px`, `900px`, and `760px`.

No code change was required to establish this baseline.

## Risks Remaining

- Frontend build validation remains environment-sensitive because the shell mixes WSL with a Windows Node runtime.
- The current workspace dependency tree appears to be missing the Windows Rollup optional package required by `vite build` under that runtime.
- This baseline did not execute any browser smoke or layout screenshot validation.

## Next Step

Proceed with `B4` shell/UX work only after the environment is normalized enough to make `vite build` deterministic in the chosen runtime.

If a concrete UI issue is found later, keep the fix minimal and boundary-scoped.
