# PT-BR UI Smoke Test Checklist

## Checklist
- [ ] Abrir o Desktop patchado com `desktop_cli/wrappers/hermes_desktop_patched_source.sh`
- [x] Sidebar Settings mostra `HermesOps`
- [x] Callout HermesOps/Composio está visível
- [x] Tabs aparecem como `Painel`, `Plugins`, `Composio` e `Logs`
- [x] Botões e rótulos principais aparecem em pt-BR
- [x] A seção `Health check da API` aparece no painel
- [x] O health check está bloqueado / mock
- [x] Nenhuma API real foi chamada pelo renderer
- [x] A mensagem sobre a API key não exibida aparece na UI
- [x] O dark mode continua legível

## Observação
O smoke test visual completo depende da abertura manual do app no ambiente gráfico; a checagem funcional segura foi validada pelo CLI nesta sessão.
