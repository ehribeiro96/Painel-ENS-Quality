# RUNTIME-H4 - Readiness Validation

## Status

`GO_STARTUP_FAILS_FAST_WITH_CLEAR_REASON`

## Baseline antes do patch

Confirmado em diagnostico anterior:

```text
LOOPBACK_BASIC_OK
UVICORN_LOOPBACK_OK
IMPORT_OK
APP_LIFESPAN_OFF_HTTP_OK
APP_LIFESPAN_ON_STARTUP_TIMEOUT
RUNPY_18085_TIMEOUT
```

## Validacao pos-patch - lifespan on

Comando:

```text
PYTHONUNBUFFERED=1 PYTHONPATH=backend:src .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18084 --lifespan on --log-level info
```

Resultado:

```text
LIFESPAN_ON_READY=NO
startup_step_begin step=settings_validation
startup_step_ok step=settings_validation
startup_step_begin step=postgres timeout_seconds=15.0
startup_step_timeout step=postgres timeout_seconds=15.0
startup_failed failed_step=postgres exception_type=TimeoutError exception_message=postgres_timeout_after_15s
Application startup failed. Exiting.
```

Classificacao:

```text
GO_STARTUP_FAILS_FAST_WITH_CLEAR_REASON
```

## Validacao pos-patch - run.py

Comando:

```text
APP_PORT=18085 APP_HOST=127.0.0.1 ENS_BUILD_FRONTEND=0 PYTHONPATH=backend:src timeout 45s .venv/bin/python run.py
```

Resultado:

```text
startup_step_begin step=settings_validation
startup_step_ok step=settings_validation
startup_step_begin step=postgres timeout_seconds=15.0
startup_step_timeout step=postgres timeout_seconds=15.0
startup_failed failed_step=postgres exception_type=TimeoutError exception_message=postgres_timeout_after_15s
Application startup failed. Exiting.
```

Classificacao:

```text
GO_RUNPY_FAILS_FAST_WITH_CLEAR_REASON
```

## Seguranca de logs

Os logs exibidos foram redigidos. Nao foram impressos DB URL, senha, token, cookie, header Authorization ou storage state.

## Processos temporarios

Processos temporarios de runtime foram encerrados ao final das validacoes. As portas `18084` e `18085` nao ficaram ocupadas.

## Decisao

O travamento indefinido do lifespan foi corrigido. O runtime ainda depende de resolver a conectividade local do Postgres para UAT.
