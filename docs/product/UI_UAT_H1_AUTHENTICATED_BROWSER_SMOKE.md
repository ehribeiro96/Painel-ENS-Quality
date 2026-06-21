# UI-UAT-H1 - Authenticated Browser Smoke

Data: 2026-06-21 20:25 -03:00

## Status

`PARTIAL_BROWSER_TOOLING_UNAVAILABLE`

## Objetivo

Executar smoke visual autenticado das rotas principais usando runtime local com FastAPI em `.venv`, Postgres/Redis via bridge e frontend Vite no WSL/Linux Node.

## Escopo

Rotas alvo:

- `/login`
- `/`
- `/assets`
- `/imports`
- `/macros`
- `/audit-logs`
- `/settings`
- `/ai-chat`

Critérios visuais planejados:

- login autenticado sem expor segredo;
- sidebar/menu utilizável;
- páginas principais renderizando sem erro visível;
- ausência de tela branca;
- ausência de erro crítico de console;
- rotas protegidas acessíveis com sessão;
- nenhuma credencial, token, cookie ou storage state persistido no repositório.

## Ambiente

Backend:

```text
FastAPI local via .venv
Porta temporária: 18086
Postgres: bridge Docker detectado sem imprimir DSN
Redis: bridge Docker detectado sem imprimir DSN
```

Frontend:

```text
Node: linux x64 /home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node
npm: 10.9.8
Vite: npm run dev -- --host 127.0.0.1 --port 5173
API configurada para http://127.0.0.1:18086 durante a execução
```

## Resultado Do Runtime Backend

```text
GET /health -> 200
GET /login -> 200
POST /api/v1/auth/login -> 200
AUTH_TOKEN_PRINTED=NO
```

Startup FastAPI validado por sinais redigidos:

```text
settings_validation -> OK
postgres -> OK
database_wait_ok
redis -> OK
redis_wait_ok
migrations -> OK
migrations_ok
bootstrap_admin -> OK
bootstrap_admin_ok
frontend_check -> OK
frontend_check_ok
startup_complete
```

## Resultado Do Runtime Frontend

O Vite foi iniciado com Linux Node e registrou:

```text
VITE v6.4.2 ready
Local: http://127.0.0.1:5173/
```

Entretanto, `curl http://127.0.0.1:5173/` expirou e a porta `5173` não permaneceu listada em `ss -ltnp`. A validação visual autenticada não foi executada porque não havia servidor frontend local acessível para o navegador.

## Browser Runner

Ferramentas verificadas no WSL:

```text
playwright=MISSING
@playwright/test=MISSING
chromium/chromium-browser/google-chrome/microsoft-edge: não encontrados no PATH
```

Não foi instalado nenhum pacote e nenhum browser foi baixado nesta boundary.

## Autenticação

Uma credencial temporária UAT já existente em `/tmp` foi reutilizada com modo `0600`. O valor da senha não foi impresso, não foi salvo no repositório e nenhum token/cookie foi exibido.

Resultado objetivo:

```text
AUTH_LOGIN_HTTP=200
AUTH_TOKEN_PRINTED=NO
```

## Smoke Visual

Resultado por etapa:

```text
Login visual: NAO_EXECUTADO
Rotas autenticadas em navegador: NAO_EXECUTADO
Console browser: NAO_CAPTURADO
Screenshots: NAO_GERADAS
Storage state: NAO_GERADO
Cookies/tokens: NAO_IMPRESSOS
```

Motivo:

```text
Browser runner indisponível no WSL e Vite local não manteve porta 5173 acessível apesar de log de readiness.
```

## Evidência Segura

Evidência registrada apenas como status HTTP, versões de runtime, presença/ausência de tooling e sinais de startup redigidos. Não foram registrados valores de credencial, token, cookie, header Authorization, DSN, Redis URL ou storage state.

## Cleanup

Processos temporários encerrados:

```text
FastAPI bridge 18086 -> encerrado
Vite 5173 -> encerrado
PORT_18086_FREE=YES
PORT_5173_FREE=YES
```

O arquivo temporário de credencial UAT em `/tmp` foi mantido para reuso controlado e continua fora do repositório.

## Decisão

`PARTIAL_BROWSER_TOOLING_UNAVAILABLE`

O backend bridge, a autenticação API e as dependências Postgres/Redis foram validados. O smoke visual autenticado permanece pendente por limitação de tooling/runtime frontend local nesta execução.
