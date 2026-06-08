# HermesOps Desktop Bridge Security Audit

## Resumo

A bridge do Hermes Desktop para o HermesOps Composio foi implementada como uma camada allowlisted no processo principal do Electron, com contrato exposto via preload e consumo somente no renderer por chamadas fixas e sanitizadas.

## Respostas objetivas

- Existe preload? Sim. O arquivo [`apps/desktop/electron/preload.cjs`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/electron/preload.cjs) já expunha `window.hermesDesktop` e agora exporta `window.hermesDesktop.hermesOps`.
- Existe IPC? Sim. O arquivo [`apps/desktop/electron/main.cjs`](/home/ribeiro/Build_Mod/upstream/hermes-agent-hermesops/apps/desktop/electron/main.cjs) usa `ipcMain.handle(...)` para a bridge read-only.
- `contextIsolation` está ativo? Sim. O `BrowserWindow` principal mantém `contextIsolation: true`.
- `nodeIntegration` está desabilitado? Sim. O `BrowserWindow` principal mantém `nodeIntegration: false`.
- Já existe padrão seguro para comandos locais? Sim. O Desktop já usa IPC + `execFile`/`spawn` em vários fluxos internos e a bridge nova segue esse padrão com allowlist fixa.
- Há uso inseguro de shell livre? Não na bridge nova. O renderer não recebe shell livre e não envia string arbitrária.
- Onde a bridge deve ser implementada? No processo principal do Electron para execução local e no preload para contrato exposto ao renderer; a UI consome apenas métodos fixos.

## Superfície allowlisted

- `hermesops_status`
- `composio_status`
- `composio_secret_check_dry_run`
- `composio_api_health_read_only`
- `composio_api_toolkits_read_only`

## Segurança aplicada

- Sem shell livre.
- Sem entrada arbitrária da UI.
- Timeout de 20 segundos.
- Saída sanitizada.
- Detecção de padrões de segredo.
- `x-request-id` preservado na resposta quando disponível.
- Nenhum valor de `COMPOSIO_API_KEY` é exposto ao renderer.

## Verificação

- Build do Desktop passou.
- Type-check passou.
- ESLint alvo passou.
- Smoke visual tentou abrir, mas o launcher foi bloqueado por porta já ocupada e o processo Electron no ambiente falhou com `app.isPackaged` indefinido.

