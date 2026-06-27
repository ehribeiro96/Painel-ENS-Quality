# M6A Auth Redirect Diagnosis - 2026-06-26

## 1. Status
NO-GO:

## 2. Objetivo
Reconciliar o gate M6, commitar evidencias M6 seletivamente e diagnosticar o redirect autenticado das rotas Apoema para `/login`.

## 3. Resultado M6
- Docs M6 commitados seletivamente em `d9309da`.
- Evidencias M6 continham material sensivel em `raw/playwright-results.json`.
- Evidencia sensivel foi redigida no working tree e commitada em `5350527`.
- Push nao foi executado.

## 4. Diagnostico do redirect
- `AUTH_STATE_FOUND=0` para `/tmp/apoema-uat-auth-state.json` no ciclo M6A.
- Porta `5175` nao estava ativa no momento do probe.
- Nao foi possivel reexecutar Playwright autenticado nem refresh no contexto do browser sem regenerar a sessao temporaria.
- O frontend ja contem o contrato de boot StrictMode-safe: `AbortError` e cancelamento nao limpam sessao, e `ProtectedRoute` aguarda `loading` antes de redirecionar.

## 5. Root cause classificado
`A_STORAGE_STATE_STALE` / `AUTH_STATE_MISSING_AFTER_M6`.

O blocker atual nao comprovou novo defeito de auth frontend. A evidencia disponivel indica que a sessao temporaria usada na execucao M6 nao esta mais disponivel para validar o browser autenticado neste ciclo.

## 6. Seguranca
- storageState fora do repo: sim.
- storageState commitado: nao.
- Credenciais impressas: nao.
- Material sensivel em evidencias M6: detectado apos commit local e redigido em commit posterior.
- Push executado: nao.

## 7. Decisao UI gate
`PARTIAL_READY_BACKEND_ONLY`

Motivo: backend, OpenAPI, runtime e API smoke autenticado estavam prontos no M6, mas o gate visual autenticado nao pode ser fechado nesta reconciliacao sem storageState valido e sem reexecutar browser autenticado.

## 8. Frontend auth
Nenhuma alteracao de frontend foi aplicada nesta fase. A inspecao confirmou:
- `AuthProvider` trata `AbortError` como neutro.
- `api.refresh` aceita `signal` e preserva `credentials: include`.
- `ProtectedRoute` renderiza `RouteLoading` enquanto `loading` esta ativo.
- Redirect para `/login` ocorre somente apos fim do loading e ausencia de `token` ou `user`.

## 9. Backend e boundary
- Backend alterado: nao.
- Docker alterado: nao.
- Migrations alteradas: nao.
- Apoema UI alterada: nao.
- Provider/MCP/vector/imagem real integrados: nao.

## 10. Limitacoes
- Sem `/tmp/apoema-uat-auth-state.json`, o probe autenticado nao pode confirmar refresh 200 ou redirect.
- Como material sensivel entrou em commit local antes da redaction, a linha deve permanecer NO-GO ate rotacao/reescrita local apropriada antes de qualquer push.

## 11. Proxima fase recomendada
`M6A_SECURITY_HISTORY_REPAIR_AND_AUTH_STATE_REGEN`

Regenerar storageState em `/tmp`, validar refresh no contexto do browser, reexecutar Playwright autenticado e tratar a historia local antes de qualquer push.
