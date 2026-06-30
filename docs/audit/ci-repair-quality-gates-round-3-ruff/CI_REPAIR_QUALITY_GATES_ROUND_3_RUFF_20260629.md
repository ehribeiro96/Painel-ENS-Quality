# CI Repair Quality Gates Round 3 Ruff — 2026-06-29

## 1. Status
PARTIAL-GO: falha Ruff identificada, correcao aplicada e gates locais passaram. A decisao final depende do novo run do GitHub Actions apos push normal.

## 2. Run analisado
- Run ID: 28382644451
- Workflow: Quality Gates
- Job: quality
- Step falho: Ruff check

## 3. Falha Ruff
- Regra: UP038
- Total: 3 ocorrencias
- Arquivos:
  - `tests/test_artifacts_contract.py:46`
  - `tests/test_designer_mock_contract.py:72`
  - `tests/test_rag_mcp_mock_contract.py:68`

## 4. Causa raiz
- `B_CI_RUFF_COMMAND_DIFFERS_FROM_LOCAL`: o workflow usava `ruff check backend/app tests`, enquanto o gate local canonico usa `backend tests scripts`.
- `D_TEST_CODE_TRIGGERS_UP038_AND_SHOULD_BE_UPDATED`: tres helpers ASGI em testes usavam `isinstance(..., (bytes, bytearray))`.

## 5. Ruff local vs CI
- Local: `ruff 0.15.16`
- CI: `ruff 0.11.13`
- Comando local canonico: `.venv/bin/python -m ruff check backend tests scripts`
- Comando CI anterior: `ruff check backend/app tests`
- Comando CI corrigido: `python -m ruff check backend tests scripts`

## 6. Correcao aplicada
- Workflow alinhado ao comando Ruff canonico.
- As tres ocorrencias foram atualizadas para `isinstance(..., bytes | bytearray)`.
- Nenhum `noqa`, skip ou `continue-on-error` foi adicionado.

## 7. Gates locais
- `git diff --check`: PASS
- `PYTHONPATH=backend JWT_SECRET_KEY=<redacted-ci-synthetic> .venv/bin/python -m pytest -s -q`: PASS, 336 passed, 22 skipped, 1 warning
- `.venv/bin/python -m ruff check backend tests scripts`: PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: PASS
- `frontend/itam-platform npm run build`: PASS

## 8. Seguranca
- Segredos reais encontrados: nao
- StorageState/cookies/tokens commitados: nao

## 9. Push
- Push executado nesta etapa: pendente no momento deste relatorio.
- Force push: nao
- Tags: nao

## 10. Proxima fase
POST_CI_REPAIR_VERIFICATION se o novo run passar; nova rodada pontual se o novo run falhar.
