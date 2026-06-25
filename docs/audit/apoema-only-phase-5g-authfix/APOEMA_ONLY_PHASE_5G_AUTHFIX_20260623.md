# Apoema-only Phase 5G Authfix - 2026-06-23

## 1. Status
PARTIAL-GO

## 2. Metodo usado
COOKIE_NORMALIZED_SAME_ORIGIN

Foi criado um cookie novo a partir do login local e ele foi normalizado em script temporario fora do repositorio. O `storageState` foi salvo em `/tmp/apoema-uat-auth-state.json`.

## 3. storageState criado
Sim.

Evidencia sem conteudo sensivel:

- `AUTH_STATE_FILE_EXISTS=1`
- arquivo em `/tmp/apoema-uat-auth-state.json`
- permissao final ajustada para `0600`

## 4. storageState localizado fora do repo
Sim.

Nenhum `storageState`, cookie, header, token ou sessao foi gravado dentro do repositorio.

## 5. storageState validado em refresh
Sim, no ciclo same-origin do Vite:

- `COOKIE_COUNT_FOR_REFRESH=1`
- `COOKIE_NAMES_FOR_REFRESH=ens_itam_refresh`
- `REFRESH_STATUS=200`
- `REFRESH_OK=1`
- `AUTH_STATE_FILE_EXISTS=1`
- `AUTH_STATE_VALID=1`

Observacao: a tentativa com `API_URL=http://127.0.0.1:8080` confirmou que o cookie entrava no contexto Playwright, mas o browser falhou no `fetch` cross-origin para o backend direto. O app em Vite usa `/api/v1` via proxy same-origin, entao a validacao util para o frontend foi repetida com `API_URL=http://127.0.0.1:18096`.

## 6. Rotas protegidas validadas
Tentativa executada em:

- `/apoema`
- `/apoema/chat`
- `/apoema/assets`
- `/apoema/assets/123`
- `/apoema/users`
- `/apoema/users/123`
- `/apoema/settings`

Resultado: as 7 rotas redirecionaram para `/login` durante a validacao de navegacao.

## 7. Rotas que redirecionaram para login
Todas as rotas protegidas testadas na navegacao Playwright redirecionaram para `/login`.

Diagnostico tecnico: durante o boot do app em Vite dev, a chamada `POST /api/v1/auth/refresh` aparece, mas e abortada com `net::ERR_ABORTED`. Isso e consistente com o fluxo de `AuthProvider` sob React `StrictMode` no dev server: o primeiro efeito de boot pode ser abortado antes de receber resposta, deixando a rota protegida sem `token/user` em memoria e acionando o redirect para `/login`.

## 8. Credenciais impressas
Nao.

As credenciais foram usadas apenas por scripts temporarios fora do repositorio e nao foram impressas nos logs.

## 9. Artefatos sensiveis em docs
Nao.

Os logs salvos registram apenas contagens, nomes de cookie, status HTTP, paths e metadados nao sensiveis. Valores de sessao ou credencial nao foram gravados.

## 10. Backend alterado
Nao.

## 11. Codigo alterado
Nao.

## 12. Validacoes executadas
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`: PASS
- `.venv/bin/python -m ruff check backend tests scripts`: PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: PASS
- `npm run build`: PASS
- `git diff --check`: PASS

## 13. Evidencias
- `raw/cookie-state-authfix.log`: tentativa com API direta em `8080`; cookie disponivel, fetch cross-origin falhou.
- `raw/cookie-state-authfix-same-origin.log`: refresh same-origin validado com sucesso.
- `raw/auth-state-filter.log`: remocao do cookie stale duplicado no arquivo temporario.
- `raw/auth-state-validation-results.json`: validacao das rotas protegidas.
- `raw/debug-boot-filtered.json`: metadados de boot sem segredos.
- `apoema-only-phase-5g-authfix-gates.log`: gates tecnicos.

## 14. Limitacoes
O objetivo de criar um `storageState` seguro e validar refresh foi atingido. A validacao de navegacao protegida no Vite dev ainda nao passou por causa do abort do refresh durante o boot do app.

Nao foi aplicada correcao de codigo porque a boundary desta tarefa proibia alterar `App.tsx`, auth, backend, CSS ou UI.

## 15. Proxima fase recomendada
Executar uma fase pequena de diagnostico/correcao do boot autenticado em Vite dev, focada no `AuthProvider` sob `StrictMode`, antes de repetir a auditoria visual autenticada completa.

Opcao segura para a proxima fase: ajustar o fluxo de refresh para que um abort do primeiro efeito em dev nao seja tratado como sessao invalida permanente.
