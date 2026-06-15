# Visual Smoke Manual Runbook

## Rotas obrigatórias

- `/login`
- `/`
- `/assets`
- `/imports`
- `/macros`
- `/ai-chat`
- `/audit-logs`
- `/settings`
- `/assinaturas/`
- `/admin/`

## Viewports

- `1920x1080`
- `1366x768`
- `1366x768` com zoom `125%`

## Critérios de aprovação

- sem overflow horizontal;
- tabs sem sobreposição;
- botões clicáveis;
- sidebar legível;
- cards legíveis;
- tabelas com scroll controlado;
- `Apply` protegido em `/imports`;
- IA Chat oculto com `ENABLE_AI_CHAT=false`;
- IA Chat visível com `ENABLE_AI_CHAT=true`;
- legado preservado;
- preview de assinatura intacto.

## Ordem sugerida

1. Abrir `/login` e autenticar.
2. Confirmar shell principal em `/`.
3. Verificar navegação lateral e cabeçalho.
4. Validar módulos de lista e tabela.
5. Abrir `/imports` e confirmar proteção do `Apply`.
6. Abrir `/macros` e confirmar visibilidade da macro gerada.
7. Abrir `/ai-chat` com a flag apropriada.
8. Validar `/assinaturas/` e `/admin/`.

## Observação

- Este runbook é manual e não substitui a evidência de execução em ambiente UAT.
- Se o ambiente não estiver ativo, registrar o bloqueio com data e motivo.
