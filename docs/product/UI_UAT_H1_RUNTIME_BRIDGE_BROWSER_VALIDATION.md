# UI-UAT-H1 - Runtime Bridge Browser Validation

Data: 2026-06-21 20:25 -03:00

## Status

`PARTIAL_BROWSER_TOOLING_UNAVAILABLE`

## Objetivo

Validar a combinação de runtime bridge backend, frontend Vite e navegador autenticado para smoke visual local.

## Comandos Executados

Comandos principais:

```text
git status --short --branch
docker compose up -d postgres redis
curl http://127.0.0.1:18086/health
curl http://127.0.0.1:18086/login
node -p "process.platform + ' ' + process.arch + ' ' + process.execPath"
npm -v
node -e "require.resolve('playwright')"
npm run dev -- --host 127.0.0.1 --port 5173
curl http://127.0.0.1:5173/
ss -ltnp
```

Nenhum comando destrutivo foi executado. Não houve `npm install`, alteração de `package-lock.json`, alteração de Docker/Compose, alteração de frontend source, alteração de backend ou migration.

## Backend Bridge

Resultado:

```text
Postgres container: healthy
Redis container: healthy
FastAPI bridge socket: ready
GET /health: 200
GET /login: 200
POST /api/v1/auth/login: 200
```

O script temporário de bootstrap aplicou URLs de conexão somente no ambiente do processo filho e não imprimiu DSN.

## Frontend Vite

Resultado:

```text
Node Linux: OK
npm: OK
Vite log: ready
HTTP 5173: timeout
Porta 5173 em ss: não permaneceu escutando
```

Classificação:

```text
PARTIAL_RUNTIME_FRONTEND_PORT_UNAVAILABLE
```

## Browser Tooling

Resultado:

```text
playwright: ausente
@playwright/test: ausente
chromium/chromium-browser/google-chrome/microsoft-edge: ausentes no PATH
```

Classificação:

```text
PARTIAL_BROWSER_TOOLING_UNAVAILABLE
```

## Segurança

Itens protegidos:

```text
Senha: não impressa
Token: não impresso
Cookie: não impresso
Authorization: não impresso
Storage state: não gerado
DSN Postgres: não impresso
Redis URL: não impressa
Screenshots: não geradas
```

## Validação Obtida

Validado nesta boundary:

- dependências Postgres/Redis disponíveis via Docker;
- FastAPI local em `.venv` operando via bridge;
- health público 200;
- login HTML público 200;
- login API autenticado 200 com credencial temporária segura;
- Node Linux correto disponível;
- ausência objetiva de Playwright/browser no WSL.

Não validado nesta boundary:

- navegação visual autenticada;
- renderização das rotas protegidas em browser;
- console browser;
- screenshots;
- fluxo visual de macro pós-movimentação.

## Próxima Ação Recomendada

Criar boundary dedicada para disponibilizar um runner de navegador suportado no WSL e repetir o smoke autenticado:

```text
UI-UAT-H2 - provide supported browser runner for WSL
```

Em paralelo, investigar por que o Vite registra readiness, mas a porta `5173` não permanece acessível:

```text
UI-RUNTIME-H1 - stabilize Vite dev server accessibility in WSL
```
