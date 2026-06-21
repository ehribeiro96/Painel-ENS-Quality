# Next Boundary Decision

Boundary atual: `RUNTIME-H4 - fix FastAPI startup/lifespan readiness`.

## Estado consolidado

- Loopback WSL basico: OK.
- `uvicorn` minimo: OK.
- Import de `app.main`: OK.
- `uvicorn app.main:app --lifespan off`: OK.
- `uvicorn app.main:app --lifespan on`: deixou de travar indefinidamente e agora falha rapido com etapa clara.
- `run.py`: deixou de travar indefinidamente e agora falha rapido com etapa clara.

## Decisao objetiva

A proxima boundary deve corrigir a conectividade local de dependencias para UAT.

Motivo:

- O problema de runtime sem diagnostico foi resolvido.
- A aplicacao agora registra `postgres_timeout_after_15s`.
- O app ainda nao fica pronto porque Postgres local nao responde dentro do timeout de startup.

## Evidencia resumida RUNTIME-H4

```text
startup_step_begin step=postgres timeout_seconds=15.0
startup_step_timeout step=postgres timeout_seconds=15.0
startup_failed failed_step=postgres exception_type=TimeoutError exception_message=postgres_timeout_after_15s
Application startup failed. Exiting.
```

Validações executadas:

```text
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

## Proxima boundary recomendada

1. `DB-RUNTIME-H1 - fix local dependency connectivity for UAT`
   Objetivo: restaurar conectividade local do Postgres/Redis necessaria para startup completo e UAT autenticado.

## Boundary seguinte apos dependencias

2. `RUNTIME-H5 - run authenticated UAT smoke on restored runtime`
   Condicao: FastAPI pronto com `startup_complete=true` e dependencias locais saudaveis.

## O que nao fazer agora

- Nao alterar frontend.
- Nao alterar migrations sem causa DB comprovada.
- Nao apagar dados locais.
- Nao resetar banco.
- Nao imprimir credenciais, tokens, cookies ou storage state.
- Nao alterar Docker/Compose fora de boundary operacional explicita.
- Nao misturar UAT autenticado com correcao de conectividade.

## Decisao final

Proxima boundary recomendada: `DB-RUNTIME-H1 - fix local dependency connectivity for UAT`.
