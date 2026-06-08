# Ruff Validation Report

Data: 2026-06-02

## Objetivo

Estabilizar o Ruff em modo conservador, sem refatoracao funcional, sem migrar
FastAPI para `Annotated` e sem aplicar `F401` globalmente.

## Comandos executados

```powershell
.venv\Scripts\ruff.exe check backend tests *> docs\RUFF_BASELINE.txt
.venv\Scripts\ruff.exe check backend tests --fix --select I001,UP035,UP037,B009
.venv\Scripts\ruff.exe check backend tests --fix --select UP017
.venv\Scripts\ruff.exe check backend tests
.venv\Scripts\python.exe -m compileall -q backend/app backend/alembic tests
.venv\Scripts\python.exe -m unittest discover -s tests
npm run build
```

## Baseline

O baseline inicial foi salvo em:

```text
docs/RUFF_BASELINE.txt
```

O baseline inicial tinha exit code `1`, indicando pendencias Ruff antes da
rodada de estabilizacao.

## Erros corrigidos

- `I001`: ordenacao/formatacao de imports via fix seguro.
- `UP017`: uso de `datetime.UTC` em vez de `timezone.utc`.
- Imports `timezone` removidos pontualmente apos `UP017`.
- Import `Path` removido pontualmente de `tests/test_imports_regression.py`.
- `B008` em `backend/app/api/v1/dependencies/auth.py` corrigido com singletons
  de `Depends` no modulo, sem alterar regra de autenticacao.

## Erros ignorados conscientemente

- `B008` foi ignorado somente em `backend/app/api/v1/routes/*.py`, pois as rotas
  FastAPI usam `Depends` e `Query` em defaults por padrao do framework.
- `F401` foi ignorado somente em `backend/app/core/database/base.py`, porque os
  imports registram metadata SQLAlchemy/Alembic.
- `UP038` foi ignorado somente em `backend/app/shared/snapshots.py`; a migracao
  de `isinstance(value, (A, B))` para union types nao foi aplicada nesta etapa
  para manter o escopo conservador.

## Itens nao realizados

- Nao foi usado `--unsafe-fixes`.
- Nao foi aplicado `F401` globalmente.
- Nao foi feita migracao para `typing.Annotated`.

## Resultado das validacoes

| Validacao | Resultado |
|---|---|
| `compileall` | Passou |
| `unittest discover` | Passou: 20 testes, 5 skipped |
| `npm run build` | Passou |
| `ruff check backend tests` | Passou |

## Riscos restantes

- `B008` nas rotas FastAPI permanece ignorado por decisao tecnica consciente.
- `UP038` em snapshots permanece como melhoria pequena futura.
- A migracao para `Annotated` em dependencias FastAPI deve ser avaliada em uma
  fase separada, com testes de rotas e sem pressa.

## Proxima melhoria recomendada

Planejar uma fase especifica para migrar dependencias FastAPI para
`typing.Annotated`, reduzindo ignores `B008` sem alterar comportamento das rotas.
