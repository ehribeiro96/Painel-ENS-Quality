# Read-Only Bridge Implementation Report

## O que foi feito

Foi criada uma bridge allowlisted entre o Hermes Desktop e o CLI `hermesops` para expor status read-only do Composio sem abrir a API no renderer.

## Arquitetura

- `apps/desktop/electron/main.cjs`
  - executa `hermesops` localmente com `execFile`
  - aplica allowlist fixa
  - impõe timeout de 20 segundos
  - sanitiza stdout/stderr
  - bloqueia qualquer saída suspeita de segredo
- `apps/desktop/electron/preload.cjs`
  - expõe métodos fixos em `window.hermesDesktop.hermesOps`
- `apps/desktop/src/app/settings/hermesops-settings.tsx`
  - consome a bridge
  - mostra status ao vivo via HermesOps
  - mantém botões perigosos desabilitados

## Comandos allowlisted

- `hermesops status`
- `hermesops composio status`
- `hermesops composio secret check --dry-run`
- `hermesops composio api health --read-only --confirm-network`
- `hermesops composio api toolkits --read-only --confirm-network`

## Comandos bloqueados

- `composio execute`
- `tools/execute`
- `connect account`
- `create connected account`
- `send email`
- `create issue`
- `delete`
- `write action`
- `admin action`
- `shell`
- `bash -c`
- `sh -c`
- `powershell`
- `curl direto`
- `sudo`
- `docker`
- `npm install`

## Resultado da UI

- A aba `Composio` deixou de ser apenas um mock estático.
- A tela agora exibe `Status ao vivo via HermesOps`.
- A UI mostra status do HermesOps, status do plugin, secret check, health check e toolkits.
- `Request ID` aparece quando o CLI fornece esse dado.
- A API key permanece oculta.
- Os botões perigosos seguem desabilitados.

## Validações

- `node --check electron/main.cjs`
- `node --check electron/preload.cjs`
- `npm run type-check`
- `npx eslint src/app/settings/index.tsx src/app/settings/hermesops-settings.tsx src/app/settings/hermesops-i18n.ts src/global.d.ts`
- `npm run build`
- `hermesops status`
- `hermesops composio secret check --dry-run`
- `hermesops composio api health --read-only --confirm-network`
- `hermesops composio api toolkits --read-only --confirm-network`

