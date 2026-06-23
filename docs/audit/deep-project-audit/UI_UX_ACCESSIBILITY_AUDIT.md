# UI/UX & Accessibility Audit — Deep Project Audit 2026-06-23

## Pontos positivos

- Componentes reutilizáveis: `LoadingBlock`, `EmptyState`, `Alert` (`StateBlocks.tsx`)
- Labels em inputs principais (`aria-label` na busca global, login fields)
- `:focus-visible` em botões, nav, sort buttons (`styles.css`)
- `aria-live="polite"` em busca e chat Apoema
- Nav lateral com `aria-label`
- Apoema: `ThemeSelector` com `role="group"`
- Confirmações antes de apply/cancel import e delete asset

## Problemas UX

| ID | Problema | Prioridade |
|----|----------|------------|
| UX-001 | Busca global mostra "Nenhum resultado" em falha de API | P2 |
| UX-002 | Apoema simula resposta IA em falha de backend | P1 |
| UX-003 | Status pills "Online" fixos no topbar | P2 |
| UX-004 | Settings sugere configuração sem persistência | P2 |
| UX-005 | Dados mock Apoema parecem operacionais | P2 |
| UX-006 | PT-BR sem acentos em erros/guards | P2 |
| UX-007 | `window.confirm` nativo (baixa acessibilidade) | P3 |

## Responsividade

- Desktop 1920×1080: grids multi-coluna, shell 2 colunas — **OK** por CSS
- 1366×768: shell reduz sidebar para 240px em `@media (max-width: 1200px)` — **OK**
- 900px: sidebar vira bloco superior, nav 2 colunas — **OK**
- 760px: ajustes adicionais login/shell — **OK**
- Mobile 390×844: **não testado visualmente**; CSS tem regras parciais

## Acessibilidade básica

| Critério | Status | Nota |
|----------|--------|------|
| Foco visível | Parcial | Presente em controles Base44; não auditado em Apoema completo |
| Teclado | Parcial | Sem teste manual de tab order |
| Contraste | Não medido | Paleta escura Base44 + Apoema — sem ferramenta de contraste |
| Tabelas | OK | `table-wrap` com scroll |
| Erros visuais | OK | classes `.alert.danger/warning` |
| Screen reader em SPA route change | Não verificado | |

## Apoema — densidade responsiva

Commit `d22c432` indica melhorias de densidade mobile; CSS confirma breakpoints dedicados.

## Recomendações

1. P1: Apoema deve comunicar erro de sessão/API sem simular chat bem-sucedido.
2. P2: Health pill dinâmico no shell.
3. P2: Revisão ortográfica PT-BR centralizada.
4. P3: Substituir `confirm()` por modal acessível.
5. P3: Auditoria de contraste com ferramenta (axe/Lighthouse) quando Playwright disponível.
