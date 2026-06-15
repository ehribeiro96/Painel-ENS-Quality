# Frontend Runtime Normalization B4-A2

## 1. Resumo Executivo

`B4-A2` is the runtime normalization boundary for the frontend. The goal is not visual polish. The goal is to make `tsc`, `vite build`, and `npm run build` reproducible from a single runtime path.

Current outcome:

- `tsc -b` passes when executed with the Windows `node.exe` directly.
- `vite build` fails when executed with the Windows `node.exe` because the current dependency tree is Linux-oriented and the Windows optional Rollup package is not present.
- `npm run build` fails from the WSL shell because the `npm` that resolves in this environment is the Windows wrapper and it falls back into a UNC/CMD path.
- The recommended runtime for this repository is WSL-native Node.js inside the Linux distro.
- The follow-up activation and validation are documented in [FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md).

## 2. Sintoma Observado

Observed symptoms during the baseline:

- WSL shell has no `node` on `PATH`.
- `npm` resolves to the Windows installation under `C:\Program Files\nodejs`.
- `npm run build` switches into a UNC path and cannot resolve `tsc`.
- `vite build` under Windows Node attempts to load a Windows Rollup optional package that is not installed in the current tree.

The symptom pattern is consistent with runtime mixing, not with frontend source code defects.

## 3. Diagnóstico Node/npm

Observed values:

- `node` on WSL PATH: missing
- `npm` on WSL PATH: Windows wrapper
- `npm version`: `11.12.0`
- `npm config get script-shell`: `null`
- `npm config get prefix`: Windows roaming profile
- `npm config get cache`: Windows profile cache path

Interpretation:

- The WSL shell is not using a native Linux Node runtime.
- The `npm` command in the shell is not aligned with the Linux filesystem tree that hosts the project.

## 4. Diagnóstico node_modules

Relevant findings:

- `frontend/itam-platform/node_modules/.bin/tsc` exists.
- `frontend/itam-platform/node_modules/.bin/vite` exists.
- `frontend/itam-platform/node_modules/@rollup/rollup-linux-x64-gnu` exists.
- `frontend/itam-platform/node_modules/@rollup/rollup-linux-x64-musl` exists.
- A Windows Rollup optional package was not present in the current tree.

Interpretation:

- The installed dependencies are Linux-oriented.
- The tree is not consistent with the Windows Node runtime that `npm run build` currently uses in this shell.
- The current tree is therefore a bad fit for cross-runtime execution.

## 5. Resultado dos Comandos

### `tsc`

Command:

```bash
cd frontend/itam-platform && timeout 120 ./node_modules/.bin/tsc -b
```

Result:

- `FAIL` in WSL shell
- reason: `node` is missing from the WSL PATH

Windows Node comparison:

```bash
cd frontend/itam-platform && timeout 180 "/mnt/c/Program Files/nodejs/node.exe" ./node_modules/typescript/bin/tsc -b
```

Result:

- `PASS`

### `vite build`

Command:

```bash
cd frontend/itam-platform && timeout 180 ./node_modules/.bin/vite build
```

Result:

- `FAIL` in WSL shell
- reason: `node` is missing from the WSL PATH

Windows Node comparison:

```bash
cd frontend/itam-platform && timeout 180 "/mnt/c/Program Files/nodejs/node.exe" ./node_modules/vite/bin/vite.js build
```

Result:

- `FAIL`
- reason: missing optional package `@rollup/rollup-win32-x64-msvc`

### `npm run build`

Command:

```bash
cd frontend/itam-platform && timeout 180 npm run build
```

Result:

- `FAIL`
- reason: Windows `npm` wrapper entered CMD/UNC mode inside WSL and could not resolve `tsc`

### Windows Node direct, used for comparison

Command:

```bash
cd frontend/itam-platform && timeout 180 "/mnt/c/Program Files/nodejs/node.exe" ./node_modules/typescript/bin/tsc -b
```

Result:

- `PASS`

Command:

```bash
cd frontend/itam-platform && timeout 180 "/mnt/c/Program Files/nodejs/node.exe" ./node_modules/vite/bin/vite.js build
```

Result:

- `FAIL`
- reason: missing Windows Rollup optional dependency

## 6. Causa Provável

Primary cause:

- runtime mixing between WSL and Windows Node/npm

Secondary cause:

- dependency tree installed for Linux-oriented execution, then exercised through Windows Node/npm from the WSL shell

This combination produces two different failure modes:

- shell wrapper failure for `npm run build`
- optional dependency mismatch for `vite build`

## 7. Runtime Recomendado

Recommended runtime:

- WSL-native Node.js LTS inside the Linux distro

Why:

- the repository itself lives under `/home/estevaoqualityadm/...`
- the dependency tree currently looks Linux-oriented
- WSL-native `node` and `npm` will keep the build path consistent with the filesystem

## 8. Procedimento Recomendado para WSL Nativo

Suggested procedure, not executed in this round:

```bash
node --version
npm --version
cd frontend/itam-platform
rm -rf node_modules
npm ci
npm run build
```

Important:

- `rm -rf node_modules` and `npm ci` must be executed only in a dedicated authorized round.
- The goal is to rebuild dependencies inside the same runtime that will execute the build.

## 9. Procedimento Alternativo para Windows Nativo

If Windows-native runtime is chosen instead:

1. Open the repository through a proper Windows path, not a WSL UNC path.
2. Use the Windows `node.exe` and `npm.cmd` consistently.
3. Reinstall dependencies using the Windows runtime.
4. Run:

```bash
cd frontend/itam-platform
npm ci
npm run build
```

This option is valid only if the team decides to standardize the project on Windows tooling.

## 10. Comandos Proibidos / Não Recomendados Nesta Rodada

- `npm install`
- `npm ci`
- `rm -rf node_modules`
- `package-lock.json` edits for build repair
- Docker-based fixes for this problem

These actions are deferred to a dedicated runtime-normalization round.

## 11. Como Validar Depois da Normalização

After the runtime is normalized, validate with the same runtime only:

```bash
cd frontend/itam-platform
./node_modules/.bin/tsc -b
./node_modules/.bin/vite build
npm run build
```

Validation criteria:

- all three commands must use the same runtime family
- no UNC fallback
- no optional Rollup package mismatch
- no source-code-only workaround required

## 12. Riscos

- If runtime mixing continues, the team will keep seeing contradictory build failures.
- If dependencies are rebuilt under the wrong runtime, the current mismatch will repeat.
- Do not treat this as a UI regression until the runtime itself is normalized.

## 13. Próximo Passo

Start `B4-B` only after the frontend build is reproducible in the chosen runtime.

That means:

- runtime normalized
- `tsc` pass confirmed
- `vite build` pass confirmed
- `npm run build` pass confirmed

Status update:

- this follow-up was completed in `B4-A3`
- the frontend build is now reproducible in WSL
- `B4-B` can begin with the runtime already normalized

Only then should visual polish or smoke-visual follow-up continue.
