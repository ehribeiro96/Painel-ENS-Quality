# UI/UX Improvement Roadmap — HermesOps Sentinel

Modo: plano seguro para fase posterior. Não executar automaticamente.

## Fase 0 — Bloqueios de produção

### 0.1 Corrigir build TypeScript

Problema: `npm run build` falha em `src/components/icons/HermesIcons.tsx(108,3)` com `TS2740`, retorno `HTMLElement` incompatível com `SVGSVGElement`.
Impacto: 5 — sem build de release, não há GO técnico.
Arquivo provável: `frontend/itam-platform/src/components/icons/HermesIcons.tsx`.
Solução sugerida: ajustar tipagem/checagem de `document.documentElement` para `SVGSVGElement` de forma segura, sem voltar a `dangerouslySetInnerHTML` inseguro se a mudança recente visou hardening.
Risco: médio; ícones aparecem no shell e várias páginas.
Esforço: 1.
Prioridade: P1.
Critério de aceite: `npm run build` passa e ícones renderizam nos screenshots.

### 0.2 Remover PNG pesado do runtime

Problema: `src/assets/brand/sentinel-logo.png` tem 2.4 MB e entra no runtime/dist.
Impacto: 4 — performance e percepção de produto.
Arquivo provável: `src/assets/brand/sentinel-logo.png`, `src/components/brand/BrandMark.tsx`.
Solução sugerida: substituir por SVG/componente vetorial ou PNG/WebP runtime menor que 100–300 KB; manter imagens grandes somente em `docs/brand/reference`.
Risco: baixo se preservar classes/dimensões.
Esforço: 1-2.
Prioridade: P1.
Critério de aceite: asset de marca runtime <=300 KB, preferencialmente <=100 KB, e screenshots sem regressão.

### 0.3 Corrigir cards/bubbles claros em tema escuro

Problema: quick cards do Dashboard e bubbles/cards do IA Chat vazam tema claro.
Impacto: 4 — quebra identidade command center e contraste.
Arquivo provável: `src/styles.css`, `src/pages/DashboardPage.tsx`, `src/pages/AiChatPage.tsx`, `src/components/ai-chat/*`.
Solução sugerida: retematizar `.quick-card`, conversation cards e message bubbles com tokens `--sentinel-*`; evitar selector amplo que quebre outras páginas.
Risco: médio por classes compartilhadas.
Esforço: 2.
Prioridade: P1.
Critério de aceite: screenshots 1366x768/1920x1080/zoom125 sem blocos brancos destoantes.

### 0.4 Atualizar metadados HTML

Problema: browser title ainda é `ENS ITAM Platform`.
Impacto: 2.
Arquivo provável: `frontend/itam-platform/index.html`.
Solução sugerida: trocar para `HermesOps Sentinel — Guardião local da infraestrutura`.
Risco: baixo.
Esforço: 1.
Prioridade: P2, mas pode entrar na Fase 0 por baixo risco.
Critério de aceite: screenshots/Playwright mostram `document.title` atualizado.

## Fase 1 — Shell e identidade

### 1.1 Status operacional honesto no topbar

Problema: `Agente local` aparece como online de forma aparentemente estática.
Impacto: 3.
Arquivo provável: `src/components/AppShell.tsx`.
Solução sugerida: se não houver health real, usar microcopy neutra; se houver endpoint, refletir health real.
Risco: médio se envolver API; baixo se só texto.
Esforço: 2.
Prioridade: P2.
Critério de aceite: UI não comunica online sem evidência real.

### 1.2 Validar shell em zoom real

Problema: zoom 125% foi apenas simulado; precisa validação real.
Impacto: 4.
Arquivo provável: `src/styles.css`, `AppShell`, `SentinelHero`.
Solução sugerida: testar no navegador real/headless com scale ou manual; ajustar breakpoints e topbar/sidebar.
Risco: médio.
Esforço: 3.
Prioridade: P1/P2.
Critério de aceite: sem overflow horizontal nem botões fora da tela em 1366x768 zoom 125% e 150%.

## Fase 2 — Dashboard/Centro de Comando

### 2.1 Reforçar quick actions operacionais

Problema: atalhos parecem cards claros genéricos.
Impacto: 4.
Arquivo provável: `DashboardPage.tsx`, `styles.css`.
Solução sugerida: usar padrão `HermesCard`/card escuro com ícone linear, status e subtítulo operacional.
Risco: baixo/médio.
Esforço: 2.
Prioridade: P1.
Critério de aceite: Dashboard parece command center técnico, sem estética SaaS clara.

### 2.2 Reduzir scroll do dashboard

Problema: Dashboard tem scroll vertical alto em 1366 e 1920.
Impacto: 3.
Arquivo provável: `DashboardPage.tsx`, `styles.css`.
Solução sugerida: compactar hero, métricas e ações; priorizar cards críticos acima da dobra.
Risco: médio.
Esforço: 3.
Prioridade: P2.
Critério de aceite: principais KPIs e alertas aparecem sem scroll em 1366x768 ou com scroll mínimo.

## Fase 3 — Páginas críticas

### 3.1 Imports/Lansweeper: decisão segura visível

Problema: página longa; apply/cancel ficam no final; validação real ausente.
Impacto: 4.
Arquivo provável: `ImportsPage.tsx`, `styles.css`.
Solução sugerida: card de decisão mais próximo do topo ou sticky, bloqueadores claros, labels humanizados para modos/status.
Risco: alto se alterar lógica; manter visual/microcopy primeiro.
Esforço: 3.
Prioridade: P1/P2.
Critério de aceite: operador entende se pode aplicar e por quê, sem rolar até o final.

### 3.2 Macros ITIL: smoke real e visual

Problema: geração/cópia real não validada; fluxo crítico exige `generation_id` e `copied_at`.
Impacto: 4.
Arquivo provável: `MacrosPage.tsx`, `MoveAssetDialog.tsx`.
Solução sugerida: após build corrigido, smoke HML com asset sintético e macro pós-movimentação.
Risco: alto em dados reais; baixo em HML isolado.
Esforço: 3.
Prioridade: P1.
Critério de aceite: macro gerada após movimento salvo, visível, copiada e marcada como copied com evidência.

### 3.3 Migrar páginas fora da identidade

Problema: Users, Assignments, Signatures, Stock, Details e NotFound ainda parciais/antigas.
Impacto: 3.
Arquivo provável: pages respectivas.
Solução sugerida: aplicar `SentinelSectionHeader`, cards escuros, `HermesStatusPill`, microcopy PT-BR e estados consistentes.
Risco: médio.
Esforço: 3-4.
Prioridade: P2.
Critério de aceite: nenhuma rota principal parece sistema antigo com tinta nova.

## Fase 4 — Acessibilidade e responsividade

### 4.1 Labels e foco de teclado

Problema: login usa placeholder; foco real por teclado não foi validado.
Impacto: 3.
Arquivo provável: `LoginPage.tsx`, `AppShell.tsx`, forms.
Solução sugerida: labels visíveis/sr-only, aria-label em busca, teste Tab/Shift+Tab/Escape/Enter.
Risco: baixo.
Esforço: 2.
Prioridade: P2.
Critério de aceite: inputs têm nomes acessíveis e foco visível em fluxos críticos.

### 4.2 Responsividade de tabelas

Problema: tabelas podem quebrar com dados reais largos.
Impacto: 3.
Arquivo provável: `DataTable.tsx`, `AssetsPage.tsx`, `AuditLogsPage.tsx`, `ImportsPage.tsx`.
Solução sugerida: truncamento com title, scroll horizontal intencional, colunas essenciais preservadas.
Risco: médio.
Esforço: 3.
Prioridade: P2.
Critério de aceite: dados longos não quebram layout em 1366x768/zoom125.

## Fase 5 — Performance e assets

### 5.1 Reauditar bundle após build passar

Problema: build atual falha; números de dist podem estar stale.
Impacto: 4.
Arquivo provável: `App.tsx`, assets, imports.
Solução sugerida: após corrigir build, medir `dist` novamente; avaliar code splitting se JS crescer.
Risco: baixo para auditoria; médio para implementação.
Esforço: 2.
Prioridade: P2.
Critério de aceite: relatório atualizado com sizes reais pós-build.

### 5.2 Limpeza gradual do CSS global

Problema: CSS global com 4032 linhas e tokens duplicados.
Impacto: 5.
Arquivo provável: `src/styles.css`.
Solução sugerida: inventário de classes usadas, separar tokens/base/components/pages ou limpeza incremental com screenshot before/after.
Risco: alto.
Esforço: 4.
Prioridade: P2.
Critério de aceite: menos duplicação, sem regressão visual comprovada.

## Fase 6 — Refinamento visual

### 6.1 Techno-indígena minimalista consistente

Problema: identidade existe, mas circuitos/padrões ainda são inconsistentes.
Impacto: 2.
Arquivo provável: brand components, icons, CSS.
Solução sugerida: padrões sutis de circuito/borda apenas em cards operacionais, sem decoração excessiva.
Risco: baixo/médio.
Esforço: 2.
Prioridade: P3.
Critério de aceite: UI comunica soberania local e comando técnico sem virar landing decorativa.

### 6.2 Revisão de microcopy PT-BR

Problema: labels técnicos crus e textos sem acento persistem.
Impacto: 2.
Arquivo provável: pages, `format.ts`.
Solução sugerida: glossário operacional HermesOps para import, staging, conflito, movimentação, macro, auditoria.
Risco: baixo.
Esforço: 2.
Prioridade: P3.
Critério de aceite: linguagem consistente, sem `Nao`, `usuario`, `Pagina` nas telas principais.

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

Status atualizado da Fase 0: `concluída com ressalvas`.
