# Frontend WSL Native Runtime B4-A3

## 1. Resumo Executivo

`B4-A3` activated a Linux/WSL-native frontend runtime and validated the build pipeline on that single runtime.

Outcome:

- WSL-native Node.js is active through local `nvm`.
- `npm ci` succeeded in `frontend/itam-platform`.
- `tsc -b` passed.
- `vite build` passed.
- `npm run build` passed.
- `package-lock.json` did not change.

Decision:

- `GO`
- The frontend build is now reproducible in the chosen runtime.

## 2. Estado Inicial

Before activation:

- `node` was missing from the WSL `PATH`.
- `npm` resolved to the Windows installation under `C:\Program Files\nodejs`.
- The frontend dependency tree was Linux-oriented.
- The Windows runtime could run `tsc` but failed on `vite build`.
- The Windows `npm run build` path failed because it entered UNC/CMD mode.

## 3. Diagnóstico Node/NPM Antes

Before activation:

- WSL `node`: absent
- WSL `npm`: Windows wrapper
- Windows `node.exe`: present
- Windows `npm.cmd`: present

The runtime was mixed and not suitable for deterministic frontend builds.

## 4. Método Usado Para Ativar Node/NPM Linux

Used method:

- local `nvm` already present under `~/.nvm`
- Node version activated: `v22.22.3`
- no remote installer
- no `curl | bash`
- no `apt` install

Commands used conceptually:

```bash
source "$HOME/.nvm/nvm.sh"
nvm use 22.22.3
```

## 5. Resultado `npm ci`

Command:

```bash
cd frontend/itam-platform
npm ci
```

Result:

- `PASS`
- 83 packages added
- 0 vulnerabilities reported by the install summary

## 6. Resultado `tsc`

Command:

```bash
timeout 120 ./node_modules/.bin/tsc -b
```

Result:

- `PASS`

## 7. Resultado `vite build`

Command:

```bash
timeout 180 ./node_modules/.bin/vite build
```

Result:

- `PASS`

## 8. Resultado `npm run build`

Command:

```bash
timeout 180 npm run build
```

Result:

- `PASS`

Interpretation:

- the build pipeline is now reproducible inside WSL using the Linux Node runtime.

## 9. `package-lock.json`

Status:

- unchanged

The normalization affected only the local `node_modules` tree.

## 10. Riscos Remanescentes

- Windows Node/npm should not be used again for this repository under the `/home/...` WSL checkout.
- Reintroducing a mixed runtime would likely re-create the earlier failure mode.
- The next boundary must stay visual-only; it should not reintroduce runtime repair work.

## 11. Comandos Recomendados Para o Dia a Dia

```bash
source "$HOME/.nvm/nvm.sh"
nvm use 22.22.3
cd frontend/itam-platform
npm run build
```

If `nvm` is not already loaded in the shell, source it first.

## 12. Comandos Proibidos / Não Recomendados

- `npm install`
- `npm ci` during the same boundary without a runtime reason
- deleting anything outside `frontend/itam-platform/node_modules`
- switching back to Windows `npm`/`node` for this repository
- Docker, migrations, backend changes, or UI redesign in this boundary

## 13. Critério Para Abrir `B4-B`

`B4-B` can start now because the runtime is reproducible.

Recommended entry conditions for `B4-B`:

- keep the WSL-native Node runtime active
- do not mix Windows Node/npm into the build path
- keep visual changes isolated from runtime fixes
- validate with the same runtime before and after any UI change
