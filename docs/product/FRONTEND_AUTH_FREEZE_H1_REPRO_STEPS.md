# FRONTEND-AUTH-FREEZE-H1 — Reproduction Steps

## Pré-condições

- Repositório: `/home/estevaoqualityadm/projects/Painel-ENS-Quality`.
- Frontend: `frontend/itam-platform`.
- Node Linux disponível via nvm.
- Runtime local acessível em `http://127.0.0.1:8000`.
- Postgres/Redis locais ativos para backend.
- Sessão ou usuário UAT local seguro disponível para reproduzir o estado pós-login.

## Como validar ambiente sem expor segredo

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality

git status --short --branch
git diff --cached --name-status

cd frontend/itam-platform
node -p "process.platform + ' ' + process.arch + ' ' + process.execPath"
node -v
npm -v
npm run build
npm run typecheck --if-present
npm run lint --if-present
npm run test --if-present
```

Depois confirmar que `frontend/itam-platform/package.json` e `frontend/itam-platform/package-lock.json` não mudaram.

## Como autenticar sem expor senha

Opção recomendada:

1. Operador provisiona sessão/usuário UAT local conforme boundary `AUTH-UAT-H2`.
2. Operador digita credenciais diretamente no navegador headed.
3. Auditor não recebe, não imprime e não salva senha.
4. Auditor não exporta storage state, cookies, Authorization header ou perfil de navegador para o repositório.

Alternativa com sessão já existente:

1. Usar perfil local temporário fora do repositório.
2. Não imprimir cookies/localStorage/sessionStorage.
3. Não commitar perfil de navegador.
4. Descartar o perfil após a coleta, se houver risco de segredo.

Se não houver sessão/credencial segura:

- Classificar como `PARTIAL_AUTH_REQUIRED`.
- Validar somente `/login` e redirecionamento público de `/`.
- Não inventar credencial e não tentar ler `.env`.

## Rotas testadas nesta boundary

Sem sessão autenticada:

- `http://127.0.0.1:8000/login`
- `http://127.0.0.1:8000/`

Resultado observado:

- `/login` renderizou formulário.
- `/` renderizou SPA e redirecionou para `/login` no cliente.
- `POST /api/v1/auth/refresh` retornou 401 uma vez, esperado sem refresh cookie.
- Sem page errors.

Rotas que ainda exigem sessão autenticada:

- `/`
- `/assets`
- `/assets/:id`
- modal de movimentação em `AssetsPage` ou `AssetDetailsPage`

## Checklist pós-login para próxima execução

1. Registrar URL final após login.
2. Confirmar shell principal renderizado.
3. Confirmar sidebar visível.
4. Confirmar header/topbar visível.
5. Confirmar dashboard/home visível.
6. Confirmar ausência de spinner infinito.
7. Confirmar console sem erro fatal.
8. Confirmar network sem loop 401/403.
9. Confirmar network sem chamadas repetidas infinitas.
10. Observar CPU/percepção de render loop.
11. Clicar em Ativos.
12. Clicar no detalhe de um ativo de teste/UAT.
13. Abrir modal de movimentação sem executar mutação destrutiva fora do plano UAT.

## Como coletar evidência segura

Script temporário criado nesta boundary:

```bash
NODE_PATH=$(npm root -g) node /tmp/frontend_auth_freeze_probe.cjs http://127.0.0.1:8000/login
NODE_PATH=$(npm root -g) node /tmp/frontend_auth_freeze_probe.cjs http://127.0.0.1:8000/
```

Para próxima execução autenticada, usar script equivalente com perfil temporário fora do repositório e redatores ativos para nomes de chave:

- token
- session
- cookie
- authorization
- password
- secret

Registrar somente:

```text
METHOD PATH STATUS COUNT OBSERVATION
```

Remover query string sensível e nunca imprimir headers.

## O que não registrar

- Senha.
- Cookie.
- Refresh token.
- Access token.
- Authorization header.
- Session secret.
- Conteúdo completo de localStorage/sessionStorage.
- Storage state do Playwright.
- Perfil de navegador.
- Screenshot com dado real.
- Trace contendo dado sensível.

## Resultado observado nesta boundary

`PARTIAL_AUTH_REQUIRED`: a superfície pública está estável, mas o freeze pós-login não foi reproduzido nem descartado porque a sessão autenticada segura não estava disponível ao auditor.
