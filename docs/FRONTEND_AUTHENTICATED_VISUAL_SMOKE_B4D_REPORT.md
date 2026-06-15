# Frontend Authenticated Visual Smoke B4-D Report

## 1. Resumo Executivo

`B4-D -- Authenticated visual smoke and fine polish` validou o frontend autenticado com backend real e sessao real obtida manualmente pelo operador, sem expor credenciais.

Status: `GO`.

Motivo:

- backend real respondeu com dependencias OK;
- sessao autenticada foi obtida sem bypass;
- rotas internas prioritarias foram avaliadas com screenshots desktop/mobile;
- ajustes aplicados foram pequenos e comprovados por screenshot;
- build final passou;
- nenhum segredo foi exposto;
- nao houve commit nem stage.

## 2. Ambiente Usado

Runtime frontend:

- `node`: `v22.22.3`
- `npm`: `10.9.8`
- `node`: `/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node`
- `npm`: `/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/npm`

Frontend:

- Vite build validado em `frontend/itam-platform`
- preview iniciado em `http://127.0.0.1:4173/`
- smoke autenticado executado no app servido pelo backend em `http://127.0.0.1:8000/`, para manter API e frontend no mesmo origin

Browser:

- Playwright temporario em `/tmp/painel-ens-b4d-pw`
- Chromium headful para login manual
- Chromium headless/headful para screenshots

## 3. Backend e Dependencias

Diagnostico:

- Docker: disponivel
- Docker Compose: disponivel
- Postgres: ativo e healthy em `5432`
- Redis: ativo e healthy em `6379`
- backend: ja estava ativo em `127.0.0.1:8000`

Validacao:

- `GET /health`: `200 OK`
- `startup_complete`: `true`
- `postgres`: `ok`
- `redis`: `ok`
- `migration.status`: `up_to_date`
- `bootstrap_admin`: `exists`
- `GET /api/v1/auth/refresh`: `404` controlado, sem timeout

Observacao:

- nao foi iniciado um segundo backend porque a porta `8000` ja estava ocupada por `uvicorn --reload`;
- o processo existente nao foi encerrado ao final por nao ter sido criado nesta boundary.

## 4. Sessao Real Sem Expor Credenciais

Metodo:

1. Playwright abriu Chromium headful em `http://127.0.0.1:8000/login`.
2. O operador digitou credenciais diretamente na janela do navegador.
3. O script aguardou a presenca de `.shell` e URL interna, sem ler campos de senha.
4. Nenhuma credencial foi impressa, armazenada em documento ou solicitada no chat.

Resultado:

- sessao real obtida: sim;
- URL autenticada inicial: `http://127.0.0.1:8000/`;
- shell presente: sim.

Nota:

- o storage state salvo em `/tmp/painel-ens-b4d-auth-state.json` nao foi suficiente para uma recaptura headless posterior; para as rotas ajustadas, uma segunda autenticacao manual headful foi usada.

## 5. Rotas Autenticadas Avaliadas

Rotas React autenticadas:

- `/`
- `/imports`
- `/macros`
- `/ai-chat`
- `/audit-logs`
- `/settings`

Rotas legadas avaliadas:

- `/assinaturas/`
- `/admin/`

Resultados gerais:

- rotas React: `200`, sem redirect para login, `.shell` presente;
- links do shell sublinhados/crus: `0` detectados;
- console errors nas rotas React: nenhum;
- `/assinaturas/`: renderizou legado fora do shell;
- `/admin/`: redirecionou para `/admin/login`, comportamento esperado do legado.

## 6. Screenshots Gerados

Smoke autenticado inicial:

- `docs/audit/screenshots/b4d/authenticated/desktop/`
- `docs/audit/screenshots/b4d/authenticated/mobile/`
- `docs/audit/screenshots/b4d/authenticated/manifest.json`

Smoke pos-polish das rotas afetadas:

- `docs/audit/screenshots/b4d/after-polish/desktop/imports.png`
- `docs/audit/screenshots/b4d/after-polish/desktop/ai-chat.png`
- `docs/audit/screenshots/b4d/after-polish/mobile/imports.png`
- `docs/audit/screenshots/b4d/after-polish/mobile/ai-chat.png`
- `docs/audit/screenshots/b4d/after-polish/manifest.json`

## 7. Problemas Encontrados

### Medio

`/ai-chat` desktop:

- o composer recebia foco automatico e podia rolar a pagina no carregamento;
- evidencia: screenshot autenticado inicial de `/ai-chat` mostrava conteudo superior acima da topbar sticky.

### Medio/Baixo

`/imports` desktop/mobile:

- DataTables vazias em cards estreitos mantinham `min-width: 820px`;
- empty states ficavam deslocados ou parcialmente cortados na area visivel.

### Baixo/Fora de Escopo B4-D

`/assinaturas/` e `/admin/`:

- CSP bloqueou carregamento externo de Google Fonts do legado;
- isso envolve legado/CSP/backend e nao foi alterado nesta boundary.

## 8. Correcoes Aplicadas

Correcoes pequenas:

- `ChatComposer.tsx`: foco automatico alterado para `focus({ preventScroll: true })`.
- `DataTable.tsx`: tabelas vazias agora adicionam `table-wrap-empty`.
- `styles.css`: `.table-wrap-empty .data-table` usa `min-width: 100%`, preservando `min-width: 820px` para tabelas com dados.

## 9. Arquivos Alterados

Codigo frontend:

- `frontend/itam-platform/src/components/ai-chat/ChatComposer.tsx`
- `frontend/itam-platform/src/components/DataTable.tsx`
- `frontend/itam-platform/src/styles.css`

Documentacao/evidencia:

- `docs/FRONTEND_AUTHENTICATED_VISUAL_SMOKE_B4D_REPORT.md`
- `docs/FRONTEND_VISUAL_REPAIR_B4C_REPORT.md`
- `docs/FRONTEND_MANUAL_VISUAL_SMOKE_B4B3_REPORT.md`
- `docs/audit/README.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`
- `docs/audit/screenshots/b4d/`

## 10. Identidade HermesOps Sentinel Preservada

Preservado:

- dark command center;
- teal/green controlado;
- cards escuros;
- bordas suaves;
- sidebar/topbar consistentes;
- visual tecnico, corporativo e auditavel.

Nao foi feito:

- redesign;
- nova biblioteca visual;
- dependencia nova no repo;
- bypass de autenticacao;
- usuario fake;
- alteracao de backend funcional;
- alteracao de migrations;
- alteracao de `package-lock`.

## 11. Resultado Build

Antes dos ajustes:

- `tsc -b`: `PASS`
- `vite build`: `PASS`
- `npm run build`: `PASS`

Depois dos ajustes:

- `tsc -b`: `PASS`
- `vite build`: `PASS`
- `npm run build`: `PASS`

## 12. Smoke Pos-Correcao

Rotas recapturadas:

- `/imports`
- `/ai-chat`

Resultados:

- desktop/mobile sem redirect para login;
- `.shell` presente;
- console errors: nenhum;
- empty tables em `/imports`: `min-width` computado como `100%`;
- AI Chat desktop abre com cabecalho e shell no topo, sem rolagem automatica indesejada.

## 13. Scanner Redigido

Scanner redigido executado sobre arquivos alterados.

Termos verificados:

- `api_key`
- `token`
- `secret`
- `password`
- `private_key`
- `sk-`
- `bearer`
- `COMPOSIO_API_KEY`
- `CodeGPT.apiKey`
- `dangerouslySetInnerHTML`
- `eval`

Resultado:

- sem segredo novo identificado;
- falso positivo em CSS: `mask-image` contem a sequencia `sk-`;
- falsos positivos em docs: lista dos termos do proprio scanner, mencao historica a `COMPOSIO_API_KEY` sem valor, e textos explicativos sobre credenciais/sessao;
- nenhum valor sensivel foi impresso.

## 14. Riscos Remanescentes

- `/assinaturas/` e `/admin/` sao legados fora do shell React e registram bloqueio CSP de fonte externa.
- O worktree geral continua misturado com alteracoes de outras boundaries.
- Smoke usou dados reais locais; futuras capturas devem continuar evitando exposicao de credenciais e dados sensiveis.

## 15. Proximo Passo Recomendado

Recomendacao: abrir boundary separada `B4-E -- legacy CSP and route polish` apenas se o legado `/assinaturas/` e `/admin/` precisar de tratamento visual/CSP.

Nao ha necessidade de outro reparo amplo do shell React neste momento.
