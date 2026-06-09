# UI/UX Audit Report — HermesOps Sentinel

Data: 2026-06-09
Modo: AUDIT_ONLY
Escopo: frontend web `frontend/itam-platform`

Nenhuma melhoria visual, CSS, componente, backend, auth, endpoint, migration, banco, `.env`, secret, commit ou push foi executado. Os únicos artefatos criados/atualizados foram documentação e screenshots em `frontend/itam-platform/docs/`.

## 1. Resumo executivo

- Status geral: NO-GO técnico e NO-GO visual.
- GO/NO-GO: NO-GO técnico + NO-GO visual.
- Motivo técnico: `npm run build` falha atualmente em `src/components/icons/HermesIcons.tsx(108,3)` com erro TypeScript `TS2740`, portanto não há build de release válido.
- Motivo visual: mesmo com renderização headless via Vite dev server, há riscos P1 persistentes: PNG de marca no runtime acima de 1 MB, cards claros vazando no tema escuro, título HTML antigo, CSS global com múltiplas gerações conflitantes e validação funcional crítica feita apenas com mocks.
- Principais riscos:
  - P1: build frontend falha (`HermesIcons.tsx`, retorno `HTMLElement` onde TypeScript espera `SVGSVGElement`).
  - P1: `frontend/itam-platform/src/assets/brand/sentinel-logo.png` tem 2.4 MB e também aparece em `dist/_assets/sentinel-logo-Ci3odQsd.png` com 2.4 MB em build anterior/stale.
  - P1: cards/bubbles claros ainda vazam em Dashboard e IA Chat, rompendo contraste e identidade escura.
  - P1: fluxo macro/import foi validado visualmente com mocks, não com backend real.
  - P2: `<title>ENS ITAM Platform</title>` em `index.html` ainda usa identidade antiga.
  - P2: `src/styles.css` tem 4032 linhas, `!important`, tokens antigos claros e tokens Sentinel sobrepostos.
- Melhorias prioritárias:
  1. Corrigir erro TypeScript do build.
  2. Remover PNG pesado do runtime/substituir por marca vetorial ou asset leve.
  3. Corrigir vazamento de cards claros em Dashboard, IA Chat e áreas com `.quick-card`/bubbles.
  4. Atualizar metadados HTML para HermesOps Sentinel.
  5. Consolidar tokens CSS e validar visual com screenshots após correção.

## 2. Escopo auditado

- Projeto: Painel ENS-Quality / HermesOps Sentinel.
- Caminho raiz: `/home/estevaoqualityadm/projects/Painel-ENS-Quality`.
- Frontend: `/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform`.
- Rotas auditadas por screenshot:
  - `/login`
  - `/`
  - `/assets`
  - `/imports`
  - `/macros`
  - `/ai-chat`
  - `/audit-logs`
  - `/settings`
- Viewports:
  - 1366x768
  - 1920x1080
  - 1366x768 com zoom 125% simulado via CSS `document.body.style.zoom = 1.25`
- Limitações:
  - Screenshots de rotas protegidas usaram Playwright com mocks de API. Eles validam renderização visual, não backend real.
  - Zoom 125% foi simulado via CSS, não por zoom real do navegador/OS.
  - Build de produção falha; screenshots foram obtidos via Vite dev server, não por artefato `dist` novo.
  - Backend real/import/macro/copy não foi exercido com dados reais.

## 3. Stack e arquitetura visual

- Stack:
  - React
  - Vite
  - TypeScript
  - React Router
  - TanStack Query
  - Lucide React
  - CSS global em `src/styles.css`
- Shell:
  - `src/components/AppShell.tsx`
  - Sidebar escura com `BrandMark`, navegação por `NavLink`, ícones HermesOps/lucide, usuário, logout e link legado.
  - Topbar com busca global, status pills e usuário.
- Rotas:
  - `src/App.tsx` registra login e rotas protegidas.
  - `RoleGuard` protege imports/macros/audit/settings conforme papel.
- CSS:
  - `src/styles.css`: 4032 linhas.
  - Camadas antigas claras e tokens Sentinel coexistem.
  - `!important` nas linhas 600-605.
  - Muitos hardcodes claros: `#fff`, `#fbfcfe`, `#eff6ff`, `white` e `rgba(...)` herdados.
- Assets:
  - `src/assets/brand/sentinel-logo.png`: 2.4 MB, P1 se usado no runtime.
  - Pack SVG HermesOps: arquivos pequenos de 4 KB cada.
  - Referências em `docs/brand`: OK como documentação, mas não runtime.
- Design system:
  - Componentes Sentinel: `BrandMark`, `HermesCard`, `HermesStatusPill`, `SentinelHero`, `SentinelSectionHeader`, `HermesIcons`.
  - Componentes comuns: `DataTable`, `StateBlocks`, `MoveAssetDialog`, AI Chat components.
  - Páginas ainda fora/parciais: Users, Signatures, Assignments, Stock, AssetDetails, UserDetails, NotFound.

## 4. Aderência à identidade HermesOps Sentinel

| Critério | Nota 0-5 | Evidência | Problema | Recomendação |
|---|---:|---|---|---|
| Marca | 4 | Login, shell e headers mostram HermesOps Sentinel e tagline. | `index.html` ainda usa `ENS ITAM Platform`; logo runtime é PNG pesado. | Atualizar metadados e substituir asset runtime por SVG/leve. |
| Shell | 4 | Sidebar escura, item ativo claro, ícones lineares, status pills. | Topbar/status parecem estáticos; precisa validar zoom real. | Conectar status a health real ou ajustar microcopy. |
| Dashboard | 3 | Hero e métricas comunicam centro de comando. | Cards claros/quick cards vazam tema antigo; scroll alto. | Reestilizar quick cards e compactar acima da dobra. |
| Login | 4 | Visual forte e coerente, tagline clara. | Inputs dependem de placeholder; title antigo. | Labels acessíveis e metadata. |
| Assets | 4 | Tabela e filtros operacionais, status claros. | Ações por ícone densas; precisa validação com dados largos. | Melhorar affordance e tooltips/labels. |
| Imports | 3 | Pipeline longo e explicativo. | Apply/cancel muito abaixo; validação visual mockada. | Tornar decisão mais visível e validar com HML real. |
| Macros | 3 | Header e lista renderizam com mock. | Fluxo gerar/copiar real não validado; preview precisa contraste. | Smoke HML após build corrigido. |
| IA Chat | 3 | Provider/mode claros. | Bubbles/cards claros quebram tema escuro. | Reestilizar conversation cards e message bubbles. |
| Auditoria | 4 | Rastreabilidade, filtros em breve e IDs compactos. | Validado com mock; dados longos reais podem quebrar. | Testar com logs reais sintéticos. |
| Settings | 3 | Header Sentinel. | Conteúdo parece estático/placeholders de integração. | Exibir estados reais ou rotular como planejamento. |
| Coerência geral | 3 | Identidade já é reconhecível. | Ainda parece camada nova sobre CSS antigo. | Consolidar tokens e migrar páginas restantes. |

## 5. Auditoria por tela

| Tela | Status | Problemas | Severidade | Arquivos prováveis | Recomendação |
|---|---|---|---|---|---|
| Login | Bom parcial | Título HTML antigo; labels de inputs dependem de placeholder. | P2 | `index.html`, `LoginPage.tsx` | Corrigir metadata e labels acessíveis. |
| Dashboard | Parcial | Cards claros/quick cards quebram command center escuro; scroll alto. | P1 | `DashboardPage.tsx`, `styles.css` | Corrigir cards claros e compactar layout. |
| Assets | Bom parcial | Tabela legível; ações densas; validar dados reais largos. | P2 | `AssetsPage.tsx`, `DataTable.tsx` | Melhorar affordance, tooltips e responsividade. |
| Imports | Parcial crítico | Página longa; apply no fim; estados críticos precisam HML real. | P1/P2 | `ImportsPage.tsx` | Card de decisão visível e smoke real controlado. |
| Macros | Parcial crítico | Render visual com mock; copiar/generation_id real não validado. | P1 | `MacrosPage.tsx`, `MoveAssetDialog.tsx` | Validar com backend real após build. |
| IA Chat | Parcial | Bubbles/cards claros em tema escuro; provider visual ok. | P1 | `AiChatPage.tsx`, `components/ai-chat/*`, `styles.css` | Corrigir contraste e cards claros. |
| Auditoria | Bom parcial | Tabela boa com mock; filtros são chips em breve. | P2 | `AuditLogsPage.tsx`, `DataTable.tsx` | Testar com logs reais e metadados longos. |
| Settings | Parcial | Integrações parecem estáticas. | P2 | `SettingsPage.tsx` | Diferenciar configurado/não configurado/legado. |
| Users | Antigo/parcial | Fora do Sentinel completo. | P2 | `UsersPage.tsx` | Migrar para Sentinel em fase 2. |
| Assignments | Antigo/parcial | “Movimentações” vs “Atribuições” pode confundir. | P2 | `AssignmentsPage.tsx`, `AppShell.tsx` | Clarificar visão atual vs histórico. |
| Signatures | Antigo/parcial | Coexiste com legado; identidade parcial. | P2 | `SignaturesPage.tsx` | Migrar preservando legado. |
| Stock/Details/NotFound | Antigo/parcial | Fora do design system. | P3 | pages respectivas | Fase posterior. |

## 6. Auditoria de fluxos UX

| Fluxo | Resultado | Problema | Impacto | Prioridade |
|---|---|---|---:|---|
| Login | Visual validado sem sessão, 3 viewports. | Title antigo e labels por placeholder. | 3 | P2 |
| Abrir Centro de Comando | Visual validado com mock. | Cards claros e scroll alto. | 4 | P1 |
| Buscar/filtrar ativo | UI renderiza filtros/busca. | Sem backend real; ações densas. | 3 | P2 |
| Abrir/importar Lansweeper | UI renderiza pipeline com mock. | Apply no fim, página longa, validação real ausente. | 4 | P1 |
| Revisar importação | Staging/conflitos/erros renderizam. | Dados reais não validados; labels técnicos. | 4 | P2 |
| Gerar/visualizar macro | Tela renderiza macro com mock. | Backend real/campos obrigatórios/copy não validado. | 4 | P1 |
| Copiar macro | Código chama clipboard + API `macroMarkCopied`. | Não validado real. | 4 | P1 |
| Abrir IA Assistiva | Renderiza com mock. | Bubble/card claro e contraste ruim. | 4 | P1 |
| Consultar Auditoria | Renderiza com mock. | Filtros avançados ainda “em breve”. | 3 | P2 |
| Abrir Configurações | Renderiza. | Conteúdo estático pode induzir falsa completude. | 2 | P2 |
| Estados vazios | `EmptyState` e DataTable existem. | Algumas mensagens genéricas. | 2 | P2 |
| Estados de erro | Alerts existem. | Alguns textos sem acento e genéricos. | 2 | P2 |
| Estados de loading | `LoadingBlock` com aria-busy/live. | Bom baseline. | 1 | P3 |

## 7. Acessibilidade

| Problema | Severidade | Evidência | Recomendação |
|---|---|---|---|
| Build falha, impedindo validação release acessível | P1 | `npm run build` falha em `HermesIcons.tsx(108,3)`. | Corrigir tipagem antes de release. |
| Contraste ruim em elementos claros | P1 | Screenshots mostram cards/bubbles claros no tema escuro. | Usar tokens Sentinel escuros e contraste AA. |
| Login sem labels explícitos visíveis | P2 | Inputs usam placeholder. | Adicionar labels visíveis ou sr-only/aria-label. |
| Foco teclado não validado manualmente | P2 | Apenas CSS/estático e screenshots. | Roteiro Tab/Shift+Tab/Escape/Enter. |
| Uso de status por cor | P2 | Pills têm texto/glyph, mas badges antigos podem depender de cor. | Garantir texto em todos status. |
| Microcopy sem acento em telas antigas | P3 | `Nao`, `usuario`, `Pagina` detectáveis em código. | Revisão PT-BR. |

## 8. Responsividade

Evidência capturada:

- 1366x768: screenshots para 8 rotas.
- 1920x1080: screenshots para 8 rotas.
- 1366x768 zoom 125% simulado: screenshots para 8 rotas.

Métricas headless indicam `scrollWidth == clientWidth` nas rotas capturadas, sem overflow horizontal detectado nesse método. Porém:

- `Imports` tem scroll vertical muito alto:
  - 1366x768: `scrollHeight` ~2424.
  - zoom 125%: `scrollHeight` ~3054.
- Dashboard também tem scroll vertical alto.
- Zoom 125% foi simulado por CSS; exige validação real no navegador/OS antes de qualquer GO visual.

## 9. Performance e assets

Build atual:

```text
npm run build
src/components/icons/HermesIcons.tsx(108,3): error TS2740: Type 'HTMLElement' is missing ... from type 'SVGSVGElement'
```

Assets medidos:

| Asset | Tamanho | Classificação |
|---|---:|---|
| `src/assets/brand/sentinel-logo.png` | 2.4 MB | P1 runtime |
| `dist/_assets/sentinel-logo-Ci3odQsd.png` | 2.4 MB | P1 runtime/stale dist |
| SVGs HermesOps | 4 KB cada | OK |
| `docs/brand/mockups/command-center-mockup.png` | 1.7 MB | OK se apenas docs |
| `docs/brand/reference/guardian.png` | 2.9 MB | OK se apenas docs |

Critério aplicado:
- <=100 KB: OK
- 100–300 KB: atenção
- 300 KB–1 MB: risco médio
- >1 MB: P1 para runtime

## 10. CSS e design system

- `styles.css`: 4032 linhas.
- `!important`: linhas 600-605.
- Hardcodes claros antigos vazam: `#fff`, `#fbfcfe`, `#eff6ff`, `white`.
- Camadas conflitantes:
  - base clara antiga no início;
  - ajustes UX intermediários;
  - tokens `--color-*` intermediários;
  - tokens `--sentinel-*` no final.
- Riscos:
  - cards claros reaparecem por herança de `.card`, `.quick-card`, AI Chat bubbles.
  - manutenção difícil por duplicação de `.sidebar`, `.topbar`, `.card`, `.alert`.
  - `word-break: break-all` em preview pode prejudicar legibilidade de macros.

## 11. Riscos para produção

| Prioridade | Risco |
|---|---|
| P1 | Build frontend falha. |
| P1 | Logo PNG runtime acima de 1 MB. |
| P1 | Cards/bubbles claros quebram tema escuro e contraste. |
| P1 | Fluxos críticos macro/import não validados com backend real. |
| P1 | CSS global conflitante aumenta risco de regressão visual. |
| P2 | `index.html` ainda usa `ENS ITAM Platform`. |
| P2 | Páginas Users/Assignments/Signatures/Stock/Details fora da identidade completa. |
| P2 | Labels/acessibilidade incompletos no login e possíveis campos. |
| P3 | Refinamento techno-indígena ainda discreto e inconsistente. |

## 12. Recomendações por fase

Fase 0:
- Corrigir build TypeScript em `HermesIcons.tsx`.
- Remover/substituir PNG pesado do runtime.
- Corrigir cards/bubbles claros em Dashboard e IA Chat.
- Atualizar title HTML.

Fase 1:
- Consolidar shell/topbar/status e responsividade real em zoom 125%/150%.

Fase 2:
- Reforçar Dashboard/Centro de Comando e quick actions como cards operacionais escuros.

Fase 3:
- Migrar Users, Assignments, Signatures, Stock, AssetDetails, UserDetails e NotFound para padrões Sentinel.

Fase 4:
- Acessibilidade: labels, foco de teclado, headings, contraste AA.

Fase 5:
- Performance/assets: logo vetorial, lazy loading, inspeção bundle após build voltar a passar.

Fase 6:
- Refinamento visual: circuitos discretos, densidade técnica, microcopy operacional.

## 13. Evidências

Comandos executados:

```bash
pwd
git status --short --untracked-files=all
find . -maxdepth 3 -name AGENTS.md -o -name README.md -o -name package.json -o -name vite.config.* -o -name tsconfig.json
find . -name AGENTS.md -print
find . -name README.md -maxdepth 4 -print
find src -maxdepth 5 -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.css" -o -name "*.json" \) | sort
grep -R "HermesOps\|Sentinel\|ENS ITAM\|Funenseg\|Inventário TI\|Command Center\|Centro de Comando" -n src index.html || true
grep -R "sidebar\|Shell\|Layout\|Header\|Topbar\|Brand\|Logo" -n src || true
npm run build
npm run lint
npm run type-check
npm test
find dist -type f -exec du -h {} + | sort -h | tail -60
find frontend/itam-platform/src/assets -type f -exec du -h {} +
wc -l frontend/itam-platform/src/styles.css
grep -n "!important" frontend/itam-platform/src/styles.css
python3 -m compileall -q backend/app backend/alembic tests
python3 -m unittest discover -s tests
python3 -m ruff check backend tests scripts
source .venv/bin/activate && python -m compileall -q backend/app backend/alembic tests
source .venv/bin/activate && python -m unittest discover -s tests
source .venv/bin/activate && python -m ruff check backend tests scripts
```

Resultados relevantes:

- `npm run build`: falhou por TypeScript.
- `npm run lint`: script inexistente.
- `npm run type-check`: script inexistente.
- `npm test`: script inexistente.
- `python3` sem venv: falhou por dependências ausentes/versões globais (`pydantic`, `fastapi`, `flask`, `structlog`, `openpyxl`, `pandas`, SQLAlchemy antigo, `ruff` ausente).
- venv do projeto:
  - compileall: OK.
  - unittest: `Ran 130 tests`, OK, `skipped=8`.
  - ruff: OK.

Screenshots gerados em `frontend/itam-platform/docs/ui-audit/screenshots/`:

- `20260609-login-1366x768.png`
- `20260609-login-1920x1080.png`
- `20260609-login-1366x768-zoom125.png`
- `20260609-home-1366x768.png`
- `20260609-home-1920x1080.png`
- `20260609-home-1366x768-zoom125.png`
- `20260609-assets-1366x768.png`
- `20260609-assets-1920x1080.png`
- `20260609-assets-1366x768-zoom125.png`
- `20260609-imports-1366x768.png`
- `20260609-imports-1920x1080.png`
- `20260609-imports-1366x768-zoom125.png`
- `20260609-macros-1366x768.png`
- `20260609-macros-1920x1080.png`
- `20260609-macros-1366x768-zoom125.png`
- `20260609-ai-chat-1366x768.png`
- `20260609-ai-chat-1920x1080.png`
- `20260609-ai-chat-1366x768-zoom125.png`
- `20260609-audit-logs-1366x768.png`
- `20260609-audit-logs-1920x1080.png`
- `20260609-audit-logs-1366x768-zoom125.png`
- `20260609-settings-1366x768.png`
- `20260609-settings-1920x1080.png`
- `20260609-settings-1366x768-zoom125.png`

## 14. Conclusão

Veredito: NO-GO técnico + NO-GO visual.

Condição mínima para avançar:

1. `npm run build` precisa voltar a passar.
2. PNG pesado precisa sair do runtime ou ser substituído por asset leve/vetorial.
3. Cards/bubbles claros precisam ser corrigidos no tema escuro.
4. Screenshots after precisam comprovar melhoria em 1366x768, 1920x1080 e zoom 125%/150% real ou documentado.
5. Import/macro/copy precisam de smoke HML real com dados sintéticos antes de qualquer release que dependa desses fluxos.

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
