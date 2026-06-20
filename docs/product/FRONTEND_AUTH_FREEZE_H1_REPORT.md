# FRONTEND-AUTH-FREEZE-H1 — Authenticated Frontend Freeze Audit

## Status

`PARTIAL_AUTH_REQUIRED`

Audit run: 2026-06-20T20:06:56-03:00.

## Resumo executivo

A auditoria validou build, sanidade estática e runtime público do frontend, mas não reproduziu o congelamento autenticado porque não havia sessão local autenticada segura disponível para o navegador de teste. A superfície `/login` renderizou normalmente, `/` redirecionou via SPA para `/login` sem loop visível, e a única chamada 401 observada sem sessão foi uma tentativa única esperada de `POST /api/v1/auth/refresh`.

A causa raiz do freeze pós-login permanece não confirmada nesta boundary. A análise estática não encontrou loop óbvio no `ProtectedRoute`, no redirecionamento de login ou no estado inicial de `AuthProvider`. Os candidatos mais prováveis para próxima investigação autenticada são as queries pós-login do dashboard (`/dashboard/summary`, `/dashboard/assets-by-status`, `/assets?page_size=200...`) e, ao navegar para ativos/detalhe, as queries de `api.users(...page_size=100)`, `AssetsPage` e `AssetDetailsPage`.

## Contexto

Projeto: `Painel ENS-Quality`.

Repositório: `/home/estevaoqualityadm/projects/Painel-ENS-Quality`.

Frontend: `frontend/itam-platform`.

Boundary: `FRONTEND-AUTH-FREEZE-H1 — audit authenticated frontend freeze after login`.

Commits recentes relevantes:

- `8241f00 fix(macros): keep post-movement macro copy flow visible`
- `9c95462 docs(macros): validate post-movement macro runtime`
- `9967f22 docs(macros): complete runtime visual recheck`
- `222d85d docs(auth): define safe local UAT authentication path`

## Ambiente

Node: `NODE_LINUX_OK` — `/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node`, `linux x64`, `v22.22.3`.

npm: `/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/npm`, `10.9.8`. Também existem entradas Windows no PATH, mas o npm efetivo usado foi Linux.

Build: `npm run build` executado com sucesso; Vite produziu `dist/index.html`, CSS `39.44 kB`, JS `495.86 kB`.

Scripts opcionais: `typecheck`, `lint` e `test` não estão presentes em `package.json`; `npm run <script> --if-present` retornou sem execução material.

Runtime: backend local iniciado em `http://127.0.0.1:8000` com Postgres/Redis locais via Docker Compose. `/health` retornou `200 OK`, `frontend_ready=true`, migrations `up_to_date`.

Auth path: sem sessão autenticada segura disponível nesta execução; docs anteriores indicam `AUTH-UAT-H1` ainda bloqueado por sessão local ausente.

Dist: `DIST_OK` antes do build e atualizado pelo build.

## Bug relatado

Após autenticação, a tela trava/congela.

Hipóteses avaliadas nesta boundary:

- loop de rota após login;
- protected route redirecionando em ciclo;
- estado de auth nunca sai de loading;
- revalidação de usuário causando render infinito;
- chamada API com 401/403 repetida;
- erro JS silencioso após login;
- freeze por componente específico;
- hook `useEffect` com dependências incorretas;
- problema de sessão/cookie/localStorage;
- bundle antigo/cache;
- problema em `api.users()`, `AssetsPage`, `AssetDetailsPage`, shell ou App router.

## Reprodução

Passos:

1. Validar worktree/stage inicial.
2. Validar Node/npm/dist.
3. Executar `npm run build` e scripts opcionais com `--if-present`.
4. Subir runtime local seguro em `127.0.0.1:8000` sem alterar código.
5. Abrir `/login` e `/` em navegador/probe sem credenciais.
6. Capturar console, page errors, respostas HTTP e estado visual sem imprimir cookies, storage ou headers sensíveis.

Resultado esperado:

- Com uma sessão autenticada, app deve navegar para `/`, renderizar shell, sidebar, header e dashboard sem spinner infinito, loop 401/403 ou render loop.

Resultado observado:

- Sem sessão, `/login` renderizou formulário normalmente.
- Sem sessão, `/` carregou SPA e redirecionou para `/login`.
- Houve uma única chamada `POST /api/v1/auth/refresh` com `401`, esperada para navegador sem refresh cookie válido.
- Não houve erro JS fatal ou page error na superfície pública.
- Não foi possível validar o estado pós-login autenticado.

## Auditoria estática

Arquivos principais inspecionados:

- `frontend/itam-platform/src/lib/auth.tsx`
- `frontend/itam-platform/src/lib/api.ts`
- `frontend/itam-platform/src/App.tsx`
- `frontend/itam-platform/src/pages/LoginPage.tsx`
- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/pages/DashboardPage.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`
- `frontend/itam-platform/src/lib/useLocalStorageState.ts`

Achados:

1. Auth guard entra em loop? Não há loop óbvio no código. `ProtectedRoute` retorna loading enquanto `loading=true`, redireciona para `/login` se `!token || !user`, e renderiza children quando ambos existem.
2. Login redireciona para rota que redireciona de volta? `LoginPage` redireciona para `/` quando `token` existe e, após submit, usa `location.state.from.pathname || '/'`. O risco teórico é usuário/token inconsistente, mas `TokenResponse` tipa `user` obrigatório.
3. Estado `loading` nunca muda? `AuthProvider` chama `refreshSession()` no mount e executa `setLoading(false)` no `.then` e no `.catch`. Sem sessão, runtime confirmou saída do loading.
4. `useEffect` chama `setState` sem dependência correta? O efeito inicial de `AuthProvider` tem dependência vazia por design. `AssetsPage` tem efeito de seed de URL params também com dependência vazia e comentário explícito. Não foi encontrado loop direto.
5. `useEffect` depende de objeto/função recriada a cada render? `AppShell` depende de `query` e `token`; há debounce e cleanup. Não há chamada imediata em loop sem input.
6. API 401 dispara logout e login em loop? `request()` tenta refresh uma vez em 401 quando permitido; se refresh falha, chama `handleUnauthorized()`. Sem sessão, observou-se uma única chamada de refresh e redirecionamento para login, não loop.
7. Rota `/` decide errado quando autenticado? Não confirmado sem sessão. Estático indica rota index dentro de `ShellRoute` para `DashboardPage`.
8. Chamada `api.users()` entra em loop? Não confirmado em runtime autenticado. Estaticamente, `AssetsPage` e `AssetDetailsPage` chamam `api.users(token, '?page_size=100')` via React Query com `enabled: Boolean(token)` e queryKey estável `['users','movement-select']`.
9. `AssetsPage` ou shell renderiza estado pesado indefinidamente? Não confirmado. `DashboardPage` busca até 200 ativos e calcula agregações locais. `AssetsPage` pagina e usa page size até 200. Não há while/setInterval.
10. Erro JS impede commit de render? Não observado na tela pública; pós-login não validado.

## Auditoria runtime

Runtime público:

- `GET /health`: `200 OK`, frontend pronto, Postgres ok, Redis ok, migrations up-to-date.
- `GET /login`: `200 OK`, HTML SPA renderizado.
- `GET /`: `200 OK`, HTML SPA renderizado; redirecionamento para `/login` acontece no cliente quando não autenticado.

Probe seguro em `/login`:

- URL final: `http://127.0.0.1:8000/login`.
- Login form: presente.
- Shell/sidebar/header: ausentes, esperado sem auth.
- Loading text: ausente após estabilização.

Probe seguro em `/` sem sessão:

- URL final: `http://127.0.0.1:8000/login`.
- Redirecionamento SPA: `/` -> `/login`.
- Login form: presente.
- Shell/sidebar/header: ausentes, esperado sem auth.
- Loading text: ausente após estabilização.

## Network audit

Sem sessão autenticada:

```text
METHOD PATH STATUS COUNT OBSERVATION
GET /login 200 1 login SPA served
GET / 200 1 SPA served before client-side auth redirect
GET /_assets/index-ByTPm-5T.css 200 1 css bundle ok
GET /_assets/index-CYFwUpId.js 200 1 js bundle ok
POST /api/v1/auth/refresh 401 1 expected without refresh cookie; no 401 loop observed
```

Auditoria pós-login autenticada: `PARTIAL_AUTH_REQUIRED`.

## Console audit

Sem sessão autenticada:

- Console registrou apenas o erro de recurso `401 Unauthorized` para `POST /api/v1/auth/refresh` sem cookie válido.
- `pageErrors`: nenhum.
- Erro fatal de render: não observado na superfície pública.
- Stack trace de componente: não disponível porque a sessão autenticada não foi alcançada.

Classificação: erro de rede esperado sem auth, não bloqueante para `/login`.

## Performance/freeze audit

Sem auth:

- Não houve spinner infinito em `/login`.
- Não houve navegação presa entre `/` e `/login`.
- Não houve repetição infinita de chamadas 401/403.
- Não houve page error.

Pós-login:

- `PERF_TRACE_NOT_AVAILABLE` para estado autenticado porque a sessão segura não estava disponível.
- `PARTIAL_AUTH_REQUIRED` para CPU/render loop pós-login.

## Classificação do freeze

Classificação final desta boundary: `PARTIAL_AUTH_REQUIRED`.

Classificações não confirmadas:

- `FREEZE_AUTH_GUARD_LOOP`: não evidenciado sem auth.
- `FREEZE_LOADING_STATE_STUCK`: não evidenciado sem auth; tela pública saiu do loading.
- `FREEZE_API_401_LOOP`: não evidenciado sem auth; refresh 401 ocorreu uma vez.
- `FREEZE_RENDER_EXCEPTION`: não evidenciado na superfície pública.
- `FREEZE_USEEFFECT_LOOP`: não evidenciado estaticamente.
- `FREEZE_ROUTE_REDIRECT_LOOP`: não evidenciado sem auth.
- `FREEZE_ASSET_PAGE_LOOP`: não testado autenticado.
- `FREEZE_USERS_API_LOOP`: não testado autenticado.

## Causa raiz provável

Não confirmada nesta boundary.

Hipótese mais provável para próxima boundary: se o freeze realmente ocorre após login, ele deve acontecer depois de `login()` preencher `token/user` e o app entrar em `ShellRoute`, provavelmente durante queries iniciais do `DashboardPage` ou durante queries de páginas autenticadas (`AssetsPage`/`AssetDetailsPage` com `api.users('?page_size=100')`). A rota/auth guard em si não mostrou loop claro no código e o runtime sem sessão mostrou refresh único e redirecionamento estável para `/login`.

## Evidência segura

- Stage inicial vazio.
- `npm run build` passou.
- `package.json` e `package-lock.json` sem diff após build/scripts.
- `/health`, `/login`, `/` validados via curl.
- Script temporário seguro criado fora do repositório: `/tmp/frontend_auth_freeze_probe.cjs`.
- Probe executado sem imprimir headers, cookies, localStorage, Authorization ou storage state.
- Nenhum screenshot, trace, storage state ou perfil de navegador foi commitado.

## Riscos

- Risco P0 ainda não descartado: congelamento autenticado pode existir, mas não foi reproduzido sem sessão.
- Sem auth path repetível, a equipe continua sem evidência objetiva de causa raiz pós-login.
- `DashboardPage` dispara múltiplas queries iniciais; se alguma resposta autenticada ficar lenta/errada, o usuário pode perceber travamento.
- `api.users('?page_size=100')` é compartilhado por `AssetsPage` e `AssetDetailsPage`; se o endpoint falhar/ficar lento pós-login, a movimentação pode degradar.
- Logs de runtime podem conter metadados de configuração; relatórios desta boundary não incluem valores sensíveis.

## Próxima boundary recomendada

`AUTH-UAT-H2 — provision documented local UAT test user`.

Justificativa: a reprodução autenticada ficou bloqueada por ausência de sessão/credencial segura disponível ao auditor. Antes de corrigir código, é necessário obter um caminho UAT local que permita autenticar sem expor segredo e então repetir a coleta pós-login.
