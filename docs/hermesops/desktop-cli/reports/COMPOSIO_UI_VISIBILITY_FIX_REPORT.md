# Composio UI Visibility Fix Report

## What changed

- Added an always-visible sidebar callout in [`src/app/settings/index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L93) with the labels `HermesOps` and `Composio`.
- Kept the dedicated `HermesOps` nav item in the sidebar in [`src/app/settings/index.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/index.tsx#L152).
- Added a patch marker and a mock/read-only badge strip in [`src/app/settings/hermesops-settings.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/hermesops-settings.tsx#L215).
- Added the visible `Composio` tab and the required content block in [`src/app/settings/hermesops-settings.tsx`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/src/app/settings/hermesops-settings.tsx#L316).

## Visible content now

- `Status: configured`
- `Ambiente: test`
- `Modo: dry-run`
- `Rede: bloqueada`
- `Credenciais: presentes / ocultas`
- `API: desabilitada`
- `MCP: desabilitado`
- `Ações externas: bloqueadas`
- `HML obrigatório: sim`
- `Composio está em modo mock/read-only. Nenhuma API real foi chamada.`
- `HermesOps UI Patch: f529068+`

## Validation

- `npm run type-check` passed after fixing the missing `title` prop in the plugin summary row.
- `npx eslint src/app/settings/index.tsx src/app/settings/hermesops-settings.tsx` passed.
- `hermesops composio status` and `hermesops composio secret check --dry-run` remained local and safe.

## Notes

- No Composio API call was made.
- No MCP call was made.
- No external action was executed.
- No secret file was opened.

