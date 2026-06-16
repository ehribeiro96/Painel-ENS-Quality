# TEST-H2 — Pending Tests Review

## Escopo
Revisão conservadora dos testes pendentes ainda untracked antes desta boundary:

- `tests/test_import_conflict_detector.py`
- `tests/test_security_headers.py`

## Status inicial
Ambos estavam visíveis como untracked em `git status --short -- tests/test_import_conflict_detector.py tests/test_security_headers.py`.

## `tests/test_import_conflict_detector.py`

- Tipo: unit test de conflito/normalização interna do pipeline de imports.
- Dados reais: não usa dados reais; usa dicionários sintéticos inline.
- Dependência de `imports/`: não lê `imports/`; importa código Python do backend via `PYTHONPATH`/`ROOT`.
- Tokens/credenciais/paths sensíveis: não foram identificados valores sensíveis no conteúdo revisado.
- Formatação: trailing whitespace/EOF normalizados pela boundary.
- Markers adicionados: `pytest.mark.imports`, `pytest.mark.unit`.
- Decisão: deve entrar no Git; cobre comportamento de duplicidade/conflito sem alterar app.

## `tests/test_security_headers.py`

- Tipo: unit test de headers CSP aplicados por função interna do backend.
- Dados reais: não usa dados reais; instancia `starlette.responses.Response` em memória.
- Dependência de `imports/`: nenhuma.
- Tokens/credenciais/paths sensíveis: não foram identificados valores sensíveis no conteúdo revisado.
- Formatação: trailing whitespace/EOF normalizados pela boundary.
- Markers adicionados: `pytest.mark.security`, `pytest.mark.unit`.
- Decisão: deve entrar no Git; preserva validação de compatibilidade CSP legado sem alterar app.

## Resultado dos testes pendentes

Comando:
```bash
PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_import_conflict_detector.py tests/test_security_headers.py -q -o addopts=''
```

Resultado: `5 passed, 1 warning`, exit code `0`.

Retry `-s`: executado apenas como verificação operacional adicional; também retornou `5 passed, 1 warning`, exit code `0`. Não houve falha `_pytest/capture.py` nesta execução.

## Decisão de commit
Versionar seletivamente os dois testes junto com `pytest.ini` e docs TEST-H2. Não versionar arquivos fora da allowlist e não alterar código funcional.
