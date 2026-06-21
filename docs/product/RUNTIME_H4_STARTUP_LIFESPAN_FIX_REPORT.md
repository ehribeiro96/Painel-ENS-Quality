# RUNTIME-H4 - Startup/Lifespan Readiness Fix

## Status

`GO_STARTUP_FAILS_FAST_WITH_CLEAR_REASON`

## Diagnostico

O loopback local, o `uvicorn` minimo, o import de `app.main` e `uvicorn app.main:app --lifespan off` funcionavam. O bloqueio acontecia somente com `lifespan on` e `run.py`.

O probe com `lifespan on` mostrou:

```text
Waiting for application startup.
startup_begin
database_wait_begin
```

Depois disso a aplicacao nao expunha listener HTTP util e `/health` ficava em timeout.

## Causa raiz

O startup aguardava a etapa de Postgres sem timeout por etapa. Quando a conexao local de banco ficava bloqueada, o lifespan nao chegava a `Uvicorn running`, deixando `/health` e `/login` pendurados sem causa operacional clara.

## Correcao aplicada

- Adicionado `app_startup_step_timeout_seconds`, default `15.0`.
- `_run_startup_step` agora aplica `asyncio.wait_for` por etapa.
- Adicionados logs estruturados:
  - `startup_step_begin`
  - `startup_step_ok`
  - `startup_step_timeout`
  - `startup_step_error`
- `wait_for_dependencies` passou a executar Postgres e Redis como etapas nomeadas.
- Mensagens de erro de startup passam por redacao de DSN/campos sensiveis.
- Snapshot de startup passou a registrar flags de presenca para admin, sem e-mail/nome em claro.

## Timeouts/logs adicionados

Timeout padrao por etapa:

```text
app_startup_step_timeout_seconds=15.0
```

Exemplo validado:

```text
startup_step_begin step=postgres timeout_seconds=15.0
startup_step_timeout step=postgres timeout_seconds=15.0
startup_failed failed_step=postgres exception_type=TimeoutError exception_message=postgres_timeout_after_15s
```

## Validacao

Executado:

```text
.venv/bin/python -m unittest tests.test_startup_diagnostics -v
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
python -m ruff check backend/app/core/config/settings.py backend/app/core/startup.py tests/test_startup_diagnostics.py
```

Resultado:

```text
159 tests OK, skipped=8
ruff OK
compileall OK
```

## O que nao foi alterado

- Frontend.
- Migrations.
- Docker/Compose.
- Package files.
- Assets.
- IA/Ollama.
- Regras de negocio.
- Credenciais ou arquivos `.env`.

## Riscos restantes

O runtime local ainda nao ficou pronto porque a etapa Postgres falhou por timeout. A falha agora e curta, explicita e rastreavel, mas a conectividade local de banco ainda precisa ser corrigida para UAT autenticado.

## Proxima boundary

`DB-RUNTIME-H1 - fix local dependency connectivity for UAT`
