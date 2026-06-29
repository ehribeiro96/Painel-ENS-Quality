# CI Repair - Quality Gates - 2026-06-29

## 1. Status
PARTIAL-GO: correcao aplicada, gates locais passaram e push normal sera executado; a decisao final depende da nova execucao do GitHub Actions.

## 2. Run ID
28381078282

## 3. Job ID
84083542556

## 4. Workflow
Quality Gates (`.github/workflows/quality-gates.yml`)

## 5. Step falho
Backend regression tests.

## 6. Causa raiz classificada
B_CI_WRONG_PYTEST_COMMAND / C_CI_MISSING_DEPENDENCIES.

O workflow executava `python -m unittest discover -s tests`, mas a suite atual validada localmente roda com `PYTHONPATH=backend python -m pytest -s -q`. No runner limpo, o comando via `unittest` importou testes que dependem de `pytest` sem garantir essa dependencia, e tambem expôs diferencas de artefatos ignorados por `*.log`.

## 7. Evidencia do log
- `test_import_conflict_detector` e `test_security_headers` falharam com `ModuleNotFoundError: No module named 'pytest'`.
- `test_m4_designer_api_contract_docs` acusou ausencia de `docs/audit/external-ens-unified-migration-m4-designer-api/ens-unified-migration-m4-designer-api-gates.log` no checkout limpo.
- O step executado no CI era `python -m unittest discover -s tests`.

## 8. Correcao aplicada
- Instalacao explicita de `pytest` no workflow `Quality Gates`.
- Step `Backend regression tests` alinhado ao gate local: `PYTHONPATH=backend python -m pytest -s -q`.
- Inclusao do gates log M4 exigido pelo teste de contrato, apesar da regra global `*.log`.

## 9. Gates locais
- `git diff --check`: PASS
- `PYTHONPATH=backend .venv/bin/python -m pytest -s -q`: PASS, 336 passed, 22 skipped, 1 warning
- `ruff check backend tests scripts`: PASS
- `compileall`: PASS
- `npm run build`: PASS

## 10. Seguranca
Nenhum segredo real identificado em workflow ou docs da fase. Nenhum storageState, cookie ou token foi commitado.

## 11. Push
Push normal previsto apos commit seletivo: `git push origin main`. Force push e tags nao usados.

## 12. Proxima fase
Verificar a nova execucao do workflow `Quality Gates`.
