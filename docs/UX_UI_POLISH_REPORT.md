# UX/UI Polish Report

Data: 2026-06-03

## Resumo executivo

Rodada conservadora de polimento visual concluida nas telas de Macros, Importar/Exportar, Ativos e no shell principal. A intervencao ficou restrita a microcopy, labels, badges, estados vazios, contraste leve, responsividade e clareza operacional.

Nao houve alteracao de backend, migrations, regras de negocio, pipeline Lansweeper, assinaturas, legado Flask ou dados UAT. Apply do `ens.db` nao foi executado.

Decisao: `GO COM RESSALVAS`.

A ressalva e apenas de evidencia visual automatizada: as rotas reais foram validadas e o build passou, mas o navegador embutido da sessao nao navegou corretamente para capturar medicoes finais de viewport; a tentativa ficou em `about:blank`. Nao foi instalada dependencia nova apenas para isso.

## Telas avaliadas

| Tela | Resultado |
| --- | --- |
| Sidebar/topbar | Labels revisados, acentos corrigidos, busca global com placeholder mais operacional |
| Ativos | Tabela mais clara para cadastro incompleto, sem usuario, status em PT-BR e acoes por linha |
| Importar/Exportar | Fluxo de importacao ficou mais explicito: etapas, bloqueios, recomendacao e exportacao desabilitada com texto honesto |
| Macros | Preview vazio mais claro, campos obrigatorios destacados, pendencias visiveis e macro de movimentacao evidenciada |
| Movimentacao | Textos do modal revisados e macro de movimentacao preservada |

## Ajustes aplicados

- Criados helpers de apresentacao em `frontend/itam-platform/src/lib/format.ts` para status de ativos, decisoes de importacao e labels tecnicos.
- Sidebar/topbar recebeu textos com acentuacao correta e placeholder operacional.
- Ativos passou a exibir:
  - `Cadastro incompleto` para linhas sem identificadores suficientes;
  - `Sem usuario` quando nao ha colaborador vinculado;
  - status traduzidos para PT-BR;
  - acoes com labels e `aria-label` mais claros.
- Importar/Exportar passou a exibir:
  - etapas do fluxo;
  - painel de decisao;
  - bloqueios antes do apply;
  - metricas com severidade visual;
  - botao de exportacao desabilitado como `Exportacao em preparacao`.
- Macros passou a exibir:
  - macro `ativos-atualizar-inventario` como usada em movimentacoes de ativos;
  - preview vazio sem poluir a tela com placeholders crus;
  - aviso objetivo para campos pendentes;
  - chips para pendencias;
  - campos obrigatorios marcados com `*`.
- CSS recebeu classes pequenas e reutilizaveis para badges, chips, stepper, painel de decisao e preview.

## Problemas encontrados

| Problema | Correcao |
| --- | --- |
| Labels tecnicos apareciam crus em algumas telas | Adicionados formatadores PT-BR |
| Export CSV parecia acao disponivel | Botao ficou desabilitado com microcopy honesta |
| Preview de macro vazio podia confundir | Empty state orienta preencher campos e gerar preview |
| Pendencias de macro nao tinham destaque suficiente | Alerta e chips de campos pendentes |
| Ativos sem usuario/identificador nao ficavam evidentes | Badges `Sem usuario` e `Cadastro incompleto` |

## Validacao de rotas

Rotas validadas em UAT:

| Rota | Resultado |
| --- | --- |
| `/health` | `200` |
| `/` | `200` |
| `/macros` | `200` |
| `/assets` | `200` |
| `/imports` | `200` |
| `/assinaturas/` | `200` |
| `/admin/` | `302` |
| `/api/v1/macros/templates` sem token | `401` |
| `/api/v1/assets` sem token | `401` |

## Validacoes tecnicas

Comandos executados com sucesso:

```powershell
npm run build
python -m compileall -q backend/app backend/alembic tests scripts
python -m unittest discover -s tests
ruff check backend tests scripts
docker compose config --services
```

Resultados:

- frontend build: sucesso;
- compileall: sucesso;
- testes Python: `39` testes executados, `6` skipped, `OK`;
- Ruff: `All checks passed!`;
- Docker Compose config: servicos `postgres`, `redis`, `app`.

## Segurança e dados

- Apply do `ens.db` nao foi executado.
- Nenhum usuario foi criado ou alterado.
- Nenhuma migration foi criada ou alterada.
- Nenhum segredo foi impresso ou gravado.
- Pipeline Lansweeper, assinaturas e legado `/assinaturas/` e `/admin/` foram preservados.

## Riscos restantes

- Captura visual automatizada por viewport nao foi concluida nesta sessao porque o navegador embutido nao navegou alem de `about:blank`.
- Recomenda-se uma passada manual final em `1920x1080`, `1366x768` e zoom `125%` antes de demonstracao para usuario final.

## Decisao

Decisao: `GO COM RESSALVAS`.

Motivo: as melhorias sao pequenas, o build/testes/rotas passaram e nao houve alteracao funcional sensivel. A ressalva fica limitada a evidencia visual automatizada de viewport.

## HermesOps Sentinel visual identity

A identidade HermesOps Sentinel foi aplicada no frontend principal como uma segunda camada visual focada em centro de comando, rastreabilidade e operação local.

### Componentes criados

- `frontend/itam-platform/src/components/brand/BrandMark.tsx`
- `frontend/itam-platform/src/components/brand/HermesCard.tsx`
- `frontend/itam-platform/src/components/brand/HermesStatusPill.tsx`
- `frontend/itam-platform/src/components/brand/SentinelHero.tsx`
- `frontend/itam-platform/src/components/brand/SentinelSectionHeader.tsx`
- `frontend/itam-platform/src/components/icons/HermesIcons.tsx`

### Páginas atualizadas

- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/pages/DashboardPage.tsx`
- `frontend/itam-platform/src/pages/LoginPage.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/pages/ImportsPage.tsx`
- `frontend/itam-platform/src/pages/MacrosPage.tsx`
- `frontend/itam-platform/src/pages/AiChatPage.tsx`
- `frontend/itam-platform/src/pages/AuditLogsPage.tsx`
- `frontend/itam-platform/src/pages/SettingsPage.tsx`
- `frontend/itam-platform/src/components/StateBlocks.tsx`
- `frontend/itam-platform/src/components/DataTable.tsx`

### Observacao

A execução desta etapa ocorreu sem alterar backend, migrations, autenticação, pipeline Lansweeper, macros ou legado `/assinaturas/` e `/admin/`.

## Pré-produção visual

- Build Vite executado com sucesso.
- Smoke visual: não executado neste ambiente por ausência de navegador gráfico/binário de browser local.
- Asset `sentinel-logo.png`: otimizado sem dependência nova pela remoção de chunk ancillary `caBX`.
- Tamanho final do `sentinel-logo.png`: `2,472,076` bytes.
- Rotas verificadas em smoke técnico: `/` e resposta HTTP do app local. As rotas `login`, `assets`, `imports`, `macros`, `ai-chat`, `audit-logs` e `settings` permanecem no contrato visual e devem ser conferidas manualmente.
- Pendências visuais: `Users`, `Signatures`, `Assignments` ainda seguem com o visual anterior e podem receber uma Fase 2 Sentinel.

## Fase 0 — Hardening técnico/visual aplicado

Correções aplicadas:
- Corrigido erro TypeScript em `HermesIcons.tsx`.
- PNG pesado removido do runtime.
- Marca operacional substituída por ícone vetorial/componentizado.
- Dashboard quick cards retematizados para tema escuro Sentinel.
- IA Chat retematizado para remover bubbles/cards claros.
- Macros retematizado para remover preview/card claro.
- `<title>` atualizado para HermesOps Sentinel.
- Build executado com sucesso.
- Screenshots after gerados.

Limitações:
- Screenshots de rotas protegidas podem usar mocks e não validam backend real.
- Fluxos reais de importação/macro/copied_at ainda exigem smoke HML.
- Users, Signatures, Assignments, Stock, Details e NotFound permanecem para fase posterior.

Veredito atualizado: `GO técnico + GO visual com ressalvas`.
