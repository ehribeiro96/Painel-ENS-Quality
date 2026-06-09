# HermesOps Sentinel UI Guide

## Conceito

HermesOps Sentinel é o centro de comando local do Painel ENS-Quality.
A interface comunica:

- agente local;
- soberania operacional;
- inventário técnico;
- rastreabilidade;
- auditoria;
- automação controlada;
- memória operacional;
- segurança;
- suporte N2.

## Paleta

Tokens principais:

- `--sentinel-bg-main: #070A0D`
- `--sentinel-bg-panel: #0D1117`
- `--sentinel-bg-card: #111820`
- `--sentinel-text-main: #F4F1E8`
- `--sentinel-text-muted: #9EA7B3`
- `--sentinel-primary: #00E5B0`
- `--sentinel-secondary: #38BDF8`
- `--sentinel-warning: #F59E0B`
- `--sentinel-danger: #EF4444`
- `--sentinel-success: #22C55E`

## Componentes criados

- `BrandMark`
- `HermesCard`
- `HermesStatusPill`
- `SentinelHero`
- `SentinelSectionHeader`
- `HermesIcons`

## Uso correto da marca

- Use `BrandMark` para identificação principal do painel.
- Use `SentinelHero` em telas institucionais e de entrada.
- Use `HermesCard` para blocos operacionais escuros com densidade técnica.
- Use `HermesStatusPill` para estados curtos e rastreáveis.
- Use `HermesIcons` para linguagem visual consistente.

## Uso correto dos ícones

- Prefira ícones lineares e discretos.
- Mantenha ícones em `currentColor`.
- Evite glow exagerado em estado normal.
- Use destaque apenas para estado ativo, online, sucesso ou foco.

## Restrições

- Não usar a imagem do guardião como background permanente.
- Não aumentar o brilho a ponto de comprometer contraste.
- Não trocar dados reais por mock.
- Não alterar backend, auth, migrations, contratos de API ou legado.
- Não introduzir dependência nova sem necessidade técnica forte.

## Páginas aplicadas

- `Dashboard`
- `Login`
- `Assets`
- `Imports`
- `Macros`
- `AI Chat`
- `Audit Logs`
- `Settings`
- `AppShell`

## Assets copiados

- `frontend/itam-platform/src/assets/brand/sentinel-logo.png`
- `frontend/itam-platform/src/assets/icons/hermesops/svg/*.svg`
- `frontend/itam-platform/src/assets/icons/hermesops/icon-manifest.json`
- `frontend/itam-platform/docs/brand/reference/guardian.png`
- `frontend/itam-platform/docs/brand/reference/guardiao-original.png`
- `frontend/itam-platform/docs/brand/reference/sentinel-logo-reference.png`
- `frontend/itam-platform/docs/brand/mockups/command-center-mockup.png`

## Pendências

- Smoke visual manual em `1920x1080`, `1366x768` e zoom `125%`.
- Refinar os cards de métricas do dashboard se necessário após inspeção no navegador.
- Validar se o pack de ícones precisa de pequenos ajustes de densidade em telas compactas.

## Pré-produção visual

- Build Vite executado com sucesso.
- Smoke visual: não executado neste ambiente por ausência de navegador gráfico/binário de browser local.
- Asset `sentinel-logo.png`: otimizado sem dependência nova pela remoção de chunk ancillary `caBX`.
- Tamanho final do `sentinel-logo.png`: `2,472,076` bytes.
- Rotas verificadas em smoke técnico: `/` e resposta HTTP do app local. As rotas `login`, `assets`, `imports`, `macros`, `ai-chat`, `audit-logs` e `settings` permanecem no contrato visual e devem ser conferidas manualmente.
- `Users`, `Signatures`, `Assignments` ainda seguem com o visual anterior e são candidatos para uma Fase 2.

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
