# Keyboard Layout Fix Report

## What changed

- Added a live keyboard metadata panel inside HermesOps settings.
- Added the PT-BR desktop launcher wrapper:
  - `desktop_cli/wrappers/hermes_desktop_ptbr.sh`
  - `desktop_cli/wrappers/Start-HermesOpsDesktop-PTBR.ps1`
- Added CLI diagnostics:
  - `hermesops desktop keyboard status`
  - `hermesops desktop locale status`
  - `hermesops desktop launch --pt-br`
  - `hermesops desktop launch --pt-br --dry-run`

## Safety rules followed

- No text input is persisted.
- No Composio API or MCP calls were added.
- The panel only shows event metadata such as `key`, `code`, and modifier flags.

## Validation

- `hermesops desktop keyboard status`
- `hermesops desktop locale status`
- `hermesops desktop launch --pt-br --dry-run`

