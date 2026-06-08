# Read-Only Bridge Smoke Test Checklist

## Itens visuais

- [ ] `HermesOps` aparece na sidebar.
- [ ] A aba `Composio` aparece.
- [ ] A UI está em pt-BR.
- [ ] A seção `Status ao vivo via HermesOps` aparece.
- [ ] O botão `Atualizar status` existe e é seguro.
- [ ] O botão `Verificar segredo --dry-run` existe e é seguro.
- [ ] O botão `Health check read-only` existe e é seguro.
- [ ] O botão `Listar toolkits read-only` existe e é seguro.
- [ ] `Request ID` aparece quando o CLI retorna um valor.
- [ ] A API key não aparece.
- [ ] Os botões perigosos continuam desabilitados.
- [ ] Nenhuma tool foi executada pela UI.
- [ ] Nenhuma connected account foi criada.

## Resultado da sessão

- A tentativa de abrir o Desktop com `bash desktop_cli/wrappers/hermes_desktop_patched_source.sh` não chegou a uma sessão visual confiável.
- O launcher encontrou `Port 5174 is already in use`.
- O processo Electron também falhou com `TypeError: Cannot read properties of undefined (reading 'isPackaged')` nesse ambiente de smoke.
- Resultado: smoke visual não concluído nesta sessão.

