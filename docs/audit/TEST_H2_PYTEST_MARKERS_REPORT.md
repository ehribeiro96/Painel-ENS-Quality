# TEST-H2 — Pytest Markers and Validation Standardization

## Resumo executivo
Status: `PARTIAL`.
Stage inicial/final: stage inicial vazio; stage final deve permanecer vazio após commit.
Commit criado: `test: standardize pytest markers and validation commands`.
Arquivos de teste tratados:
- `tests/test_import_conflict_detector.py`
- `tests/test_security_headers.py`

A boundary padronizou markers pytest, revisou os dois testes pendentes e executou validações controladas sem alterar código funcional do backend, frontend, Docker, migrations, assets ou imports.

## Configuração pytest encontrada
Antes da boundary havia `pyproject.toml`, mas sem `[tool.pytest.ini_options]` e sem configuração pytest efetiva. Foi criado `pytest.ini` na raiz do projeto.

Configuração criada:
- markers oficiais TEST-H2;
- `norecursedirs` para impedir coleta acidental de diretórios locais/artefatos já fora do escopo de testes canônicos: `.git`, `.venv`, `frontend`, `node_modules`, `imports`, `exports`, `_validation`.

Justificativa do `norecursedirs`: a coleta ampla inicial entrou em snapshots/release candidates/transferências locais e em `imports/`, gerando import mismatch e erros de coleta fora da árvore canônica `tests/`. A boundary não adicionou `addopts`, `filterwarnings`, `testpaths`, `pythonpath` ou `asyncio_mode`.

## Markers adicionados
Markers oficiais registrados em `pytest.ini`:
- `unit`
- `integration`
- `smoke`
- `operational`
- `security`
- `ai_chat`
- `imports`
- `legacy`

Markers aplicados somente aos testes pendentes:
- `tests/test_import_conflict_detector.py`: `imports`, `unit`
- `tests/test_security_headers.py`: `security`, `unit`

## Testes pendentes revisados

### `tests/test_import_conflict_detector.py`
- Estava untracked.
- Não usa dados reais.
- Não lê `imports/`.
- Usa dados sintéticos inline.
- Foi formatado somente para whitespace/EOF.
- Recebeu markers `imports` e `unit`.
- Resultado explícito: passou.

### `tests/test_security_headers.py`
- Estava untracked.
- Não usa dados reais.
- Não lê `imports/`.
- Instancia resposta Starlette em memória.
- Foi formatado somente para whitespace/EOF.
- Recebeu markers `security` e `unit`.
- Resultado explícito: passou.

## Validações executadas

- Compile: `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests`
  - Resultado: exit code `0`.
- Coleta: `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest --collect-only -q -o addopts=''`
  - Resultado após `norecursedirs`: `171 tests collected`, exit code `0`.
- Testes pendentes explícitos: `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_import_conflict_detector.py tests/test_security_headers.py -q -o addopts=''`
  - Resultado: `5 passed, 1 warning`, exit code `0`.
- Marker `security`: `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest -m "security" -q -o addopts=''`
  - Resultado: `2 passed, 169 deselected, 1 warning`, exit code `0`.
- Marker `imports`: `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest -m "imports" -q -o addopts=''`
  - Resultado: `3 passed, 168 deselected, 1 warning`, exit code `0`.
- Marker `ai_chat`: `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest -m "ai_chat" -q -o addopts=''`
  - Resultado: `171 deselected, 1 warning`, exit code `5` por ausência de testes marcados `ai_chat` nesta boundary.

## Bug conhecido de captura pytest
O bug operacional conhecido (`FileNotFoundError` em `_pytest/capture.py`) não ocorreu nas validações finais. Um retry explícito com `-s` nos dois testes pendentes também passou (`5 passed, 1 warning`).

## Comandos oficiais
Os comandos oficiais foram documentados em `docs/audit/TEST_H2_VALIDATION_COMMANDS.md`.

## O que não foi alterado
- Nenhum código funcional em `backend/app`.
- Nenhum arquivo em `frontend`.
- Nenhum arquivo em `assets`.
- Nenhum conteúdo em `imports/`.
- Nenhum Dockerfile ou docker-compose.
- Nenhuma migration.
- Nenhum `package-lock`.
- Nenhum `.env` ou artefato sensível.
- Nenhum teste existente além dos dois pendentes.

## Riscos restantes
- `ai_chat` está registrado como marker, mas nenhum teste foi marcado nesta boundary; o comando `-m "ai_chat"` retorna exit code `5` por ausência de seleção. Classificação: `PARTIAL`, não falha funcional.
- A cobertura por marker ainda é inicial: `security` cobre 2 testes e `imports` cobre 3 testes porque a boundary proibiu marcação em massa.
- A coleta ampla dependia de excluir diretórios locais/artefatos; sem `norecursedirs`, snapshots e imports locais podem contaminar discovery.

## Próximas boundaries recomendadas
1. `PUSH-C1 — publish validated local commits`, se autenticação GitHub estiver resolvida.
2. `LEGACY-H3 — legacy archive/manual artifact handling`, somente com decisão humana.
3. `CI-H4 — publish workflow design`, somente com decisão humana.
4. `SEC-H3`, somente se revisão humana confirmar necessidade.

## Decisão final
`PARTIAL`: pytest markers e comandos foram padronizados, os testes pendentes foram revisados/versionados seletivamente e as validações principais passaram. A ressalva é a ausência de testes marcados `ai_chat`, mantida sem correção nesta boundary para não marcar testes existentes em massa.
