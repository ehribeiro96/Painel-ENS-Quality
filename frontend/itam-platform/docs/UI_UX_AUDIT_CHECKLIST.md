# UI/UX Audit Checklist — HermesOps Sentinel

## Modo AUDIT_ONLY

- [x] Não alterar frontend funcional.
- [x] Não alterar CSS/componentes.
- [x] Não alterar backend/auth/endpoints/banco/migrations/.env.
- [x] Não commitar/push/git add.
- [x] Criar/atualizar apenas relatórios e screenshots em `frontend/itam-platform/docs/`.

## Conferência inicial

- [x] `pwd` executado.
- [x] `git status --short --untracked-files=all` executado.
- [x] `find . -maxdepth 3 ...` executado.
- [x] `find . -name AGENTS.md -print` executado.
- [x] `find . -name README.md -maxdepth 4 -print` executado.
- [x] `AGENTS.md` raiz lido.
- [x] `README.md` raiz lido.

## Arquitetura frontend

- [x] File tree `src` mapeado.
- [x] Entrypoint/rotas identificados (`main.tsx`, `App.tsx`).
- [x] Shell/sidebar/topbar identificados (`AppShell.tsx`).
- [x] Componentes comuns identificados (`DataTable`, `StateBlocks`, `MoveAssetDialog`).
- [x] Componentes de marca identificados (`BrandMark`, `HermesCard`, `HermesStatusPill`, `SentinelHero`, `SentinelSectionHeader`).
- [x] Ícones e assets identificados.
- [x] CSS global/tokens/hardcodes mapeados.
- [x] Páginas fora da identidade listadas.

## Build e validações frontend

- [x] `npm run build` executado.
- [x] Build falhou documentado: `HermesIcons.tsx(108,3) TS2740`.
- [x] `npm run lint` executado e script inexistente documentado.
- [x] `npm run type-check` executado e script inexistente documentado.
- [x] `npm test` executado e script inexistente documentado.
- [x] Dist/assets avaliados como possivelmente stale por build atual falhar.

## Assets e imagens

- [x] `src/assets` medido.
- [x] `docs/brand` medido.
- [x] Imagens runtime/doc listadas.
- [x] `sentinel-logo.png` classificado como P1 runtime por 2.4 MB.
- [x] SVGs HermesOps classificados como OK.

## CSS e design system

- [x] `wc -l styles.css`: 4032 linhas.
- [x] `!important` encontrado nas linhas 600-605.
- [x] Hardcodes claros encontrados.
- [x] Riscos de `word-break`, `white-space`, `max-width`, overflow levantados.
- [x] Conflito entre tokens antigos e Sentinel registrado.

## Smoke visual

- [x] Ferramentas verificadas: Playwright e Node disponíveis.
- [x] Vite dev server iniciado.
- [x] Screenshots 1366x768 gerados para `/login`, `/`, `/assets`, `/imports`, `/macros`, `/ai-chat`, `/audit-logs`, `/settings`.
- [x] Screenshots 1920x1080 gerados para as mesmas rotas.
- [x] Screenshots 1366x768 zoom 125% simulado gerados para as mesmas rotas.
- [x] Login capturado sem sessão/mock de autenticação positiva.
- [x] Rotas protegidas capturadas com mocks e limitação documentada.

## Critérios visuais

- [x] Marca avaliada.
- [x] Shell/sidebar/topbar avaliados.
- [x] Dashboard avaliado.
- [x] Login avaliado.
- [x] Assets avaliado.
- [x] Imports avaliado.
- [x] Macros avaliado.
- [x] IA Chat avaliado.
- [x] Auditoria avaliada.
- [x] Settings avaliada.

## Fluxos UX

- [x] Login.
- [x] Abrir Centro de Comando.
- [x] Buscar/filtrar ativo visualmente.
- [x] Abrir/importar Lansweeper visualmente.
- [x] Revisar importação visualmente.
- [x] Gerar/visualizar macro visualmente com mock.
- [x] Copiar macro identificado no código, não validado real.
- [x] Abrir IA Assistiva.
- [x] Consultar Auditoria.
- [x] Abrir Configurações.
- [x] Estados vazios.
- [x] Estados de erro.
- [x] Estados de loading.

## Acessibilidade

- [x] Contraste avaliado por screenshot.
- [x] Labels/aria avaliados estaticamente.
- [x] Alt/ícones decorativos avaliados estaticamente.
- [x] Headings avaliados estaticamente.
- [x] Uso de cor como indicador registrado.
- [x] Foco de teclado registrado como limitação pendente de teste manual.

## Responsividade

- [x] 1366x768 testado via screenshot.
- [x] 1920x1080 testado via screenshot.
- [x] 1366x768 zoom 125% simulado testado via screenshot.
- [x] 150% não executado nesta rodada; recomendado para próxima validação after.
- [x] Import/Dashboard com scroll vertical alto registrados.

## Backend sem alteração

- [x] `python3` sem venv executado e falhas por dependências/ambiente registradas.
- [x] `.venv` executado conforme padrão do projeto.
- [x] venv compileall passou.
- [x] venv unittest passou: 130 testes, OK, 8 skipped.
- [x] venv ruff passou.

## Entregáveis

- [x] `frontend/itam-platform/docs/UI_UX_AUDIT_REPORT.md` atualizado.
- [x] `frontend/itam-platform/docs/UI_UX_IMPROVEMENT_ROADMAP.md` atualizado.
- [x] `frontend/itam-platform/docs/UI_UX_AUDIT_CHECKLIST.md` atualizado.
- [x] Screenshots salvos em `frontend/itam-platform/docs/ui-audit/screenshots/`.

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
