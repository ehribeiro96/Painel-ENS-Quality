# Apoema 1366x768 Responsive Polish

## 1. Objetivo
Reduzir a densidade visual em `1366x768` sem degradar a experiência premium em `1920x1080`.

## 2. Problemas corrigidos
- Ativos: colunas secundárias foram removidas da visualização estreita para liberar espaço útil no grid.
- Chat de IA: a composição ficou menos comprimida, com sidebar central e composer mais confortáveis.
- Header/títulos: títulos principais passaram a quebrar melhor e com menos impacto visual.
- Shell/painel: sidebars, cards e gaps foram compactados no breakpoint intermediário.

## 3. Estratégia aplicada
- Breakpoints:
  - `max-width: 1440px`
  - `max-width: 1366px`
- Colunas:
  - redução da largura das rails laterais;
  - tabela de ativos com foco em colunas essenciais no viewport menor.
- Painel lateral:
  - rail direita e sidebar esquerda ficaram mais estreitos;
  - composer e cards laterais perderam padding excessivo.
- Espaçamentos:
  - paddings e gaps reduzidos em cards, hero e blocos do chat;
  - títulos com `text-wrap: balance`.

## 4. Validação
- Build: OK
- `/apoema-preview`: OK
- `1366x768`: melhorou a legibilidade e reduziu a sensação de layout espremido.
- `1920x1080`: preservado; a composição continua premium.
- Tema claro: OK
- Tema escuro: OK
- Tema automático: OK

### Evidências
- `docs/apoema-visual-qa/screenshots/after-polish/1366-assets.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1366-chat.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1366-dashboard.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1920-dashboard.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1920-assets.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1920-chat.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1920-settings.png`

## 5. Riscos restantes
- A tabela de ativos em `1366x768` continua priorizando legibilidade e pode exigir outro ajuste fino se novos campos forem adicionados.
- O título principal ainda quebra em múltiplas linhas, porém sem a compressão visual anterior.

## 6. Próxima fase
- Manter o Apoema Preview como funcionalmente estável.
- Se houver nova rodada visual, fazer apenas ajuste fino de densidade em `1366x768`, sem mexer no comportamento.
