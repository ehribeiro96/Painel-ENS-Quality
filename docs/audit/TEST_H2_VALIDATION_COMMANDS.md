# TEST-H2 — Validation Commands

## Princípio
Usar comandos previsíveis, explícitos e reproduzíveis.

## Compile
```bash
PYTHONPATH=backend .venv/bin/python -m compileall -q backend/app tests
```

## Coleta
```bash
PYTHONPATH=backend .venv/bin/python -m pytest --collect-only -q -o addopts=''
```

## Security
```bash
PYTHONPATH=backend .venv/bin/python -m pytest -m "security" -q -o addopts=''
```

## Imports
```bash
PYTHONPATH=backend .venv/bin/python -m pytest -m "imports" -q -o addopts=''
```

## AI Chat
```bash
PYTHONPATH=backend .venv/bin/python -m pytest -m "ai_chat" -q -o addopts=''
```

## Testes críticos explícitos

### ai_chat
```bash
PYTHONPATH=backend .venv/bin/python -m pytest \
  tests/test_ai_chat_api.py \
  tests/test_ai_chat_hardening.py \
  tests/test_ai_chat_mvp.py \
  tests/test_ai_chat_ollama_provider.py \
  tests/test_ai_chat_provider_mock.py \
  tests/test_ai_chat_rate_limit.py \
  -q -o addopts=''
```

### security
```bash
PYTHONPATH=backend .venv/bin/python -m pytest \
  tests/test_security_headers.py \
  tests/test_hermes_icons_security.py \
  -q -o addopts=''
```

### imports
```bash
PYTHONPATH=backend .venv/bin/python -m pytest \
  tests/test_import_conflict_detector.py \
  tests/test_import_identity_classifier.py \
  tests/test_import_lansweeper_normalizer.py \
  tests/test_import_pipeline_units.py \
  tests/test_import_row_classifier.py \
  tests/test_import_spreadsheet_reader.py \
  tests/test_imports_regression.py \
  -q -o addopts=''
```

## Retry operacional
Se ocorrer `FileNotFoundError` em `_pytest/capture.py`, repetir com `-s` e documentar. O retry com `-s` não deve ser usado para esconder falha real de teste.

Exemplo:
```bash
PYTHONPATH=backend .venv/bin/python -m pytest <alvo> -q -s -o addopts=''
```

## O que não fazer
- não usar skip para esconder falha
- não rodar com dados reais
- não alterar app para teste passar
- não usar dados em imports/

## Observação de discovery
`pytest.ini` registra markers oficiais e exclui recursão em diretórios locais/artefatos (`imports`, `exports`, `_validation`, `frontend`, `node_modules`, `.venv`) para evitar coleta acidental de snapshots, transferências e release candidates fora da árvore canônica `tests/`.
