# Import Service Refactor Manifest

- Data/hora: 2026-06-08 23:25:42 -03
- Branch: `main`
- Status do worktree: sujo por mudanças pré-existentes fora desta rodada e pelas alterações desta rodada no importador.
- Objetivo: executar extração progressiva e controlada do pipeline de importação Lansweeper sem reescrever `ImportService`, sem alterar contratos, sem mudar regra de negócio e sem executar `Apply`.
- Etapa atual: início da Extração 3 controlada para identidade, classificação e conflitos, após a Extração 2 de normalização.

## Escopo permitido

- Extrair blocos coesos do `ImportService` para módulos menores.
- Manter `backend/app/domains/imports/service.py` como orquestrador.
- Preservar comportamento validado de upload, preview, staging, conflicts, report e apply parcial.
- Adicionar testes específicos para o bloco extraído.

## Escopo proibido

- Alterar contrato das rotas.
- Alterar nomes de status.
- Alterar regra de negócio.
- Alterar frontend.
- Executar `Apply` completo.
- Executar `Apply` do `ens.db`.
- Criar migration.
- Mexer em `/admin/`, `/assinaturas/`, `/macros`, `/users`, `/assets`.
- Alterar normalização já consolidada, report ou apply nesta extração, exceto a fachada de compatibilidade `identity_for()` necessária para centralizar a regra real na camada de classificação.

## Arquivos candidatos

- `backend/app/domains/imports/service.py`
- `backend/app/domains/imports/normalization/asset_normalizer.py`
- `backend/app/domains/imports/parsing/__init__.py`
- `backend/app/domains/imports/parsing/spreadsheet_reader.py`
- `backend/app/domains/imports/normalization/__init__.py`
- `backend/app/domains/imports/normalization/lansweeper_normalizer.py`
- `backend/app/domains/imports/classification/__init__.py`
- `backend/app/domains/imports/classification/identity_classifier.py`
- `backend/app/domains/imports/classification/conflict_detector.py`
- `backend/app/domains/imports/classification/row_classifier.py`
- `tests/test_import_spreadsheet_reader.py`
- `tests/test_import_lansweeper_normalizer.py`
- `tests/test_import_identity_classifier.py`
- `tests/test_import_conflict_detector.py`
- `tests/test_import_row_classifier.py`
- `docs/IMPORT_SERVICE_REFACTOR_PLAN.md`
- `docs/IMPORT_SERVICE_REFACTOR_REPORT.md`

## Riscos

- A extração de parsing pode alterar comportamento de seleção de aba ou exceções funcionais se não for mantida exatamente compatível.
- A extração de identidade/classificação/conflitos pode alterar decisões finais se houver divergência da regra atual.
- O frontend build permanece pendente por bloqueio ambiental alheio ao importador.
- O `ImportService` concentra várias responsabilidades; qualquer extração além de parsing nesta rodada aumenta risco de regressão.

## Baseline de testes

- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` passou.
- `.venv/bin/python -m ruff check backend tests scripts` passou.
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` passou.
- `docker compose config >/tmp/painel-compose-config.out && echo OK` passou.
- `cd frontend/itam-platform && npm run build` falhou por limitação ambiental do wrapper Windows/UNC no WSL.

## Decisão de prosseguir

- Prosseguir com ressalva para a Extração 3 controlada: identidade, classificação e conflitos.

## Arquivos alterados nesta rodada

- `backend/app/domains/imports/service.py`
- `backend/app/domains/imports/parsing/__init__.py`
- `backend/app/domains/imports/parsing/spreadsheet_reader.py`
- `backend/app/domains/imports/normalization/__init__.py`
- `backend/app/domains/imports/normalization/lansweeper_normalizer.py`
- `backend/app/domains/imports/classification/__init__.py`
- `backend/app/domains/imports/classification/identity_classifier.py`
- `backend/app/domains/imports/classification/conflict_detector.py`
- `backend/app/domains/imports/classification/row_classifier.py`
- `tests/test_import_spreadsheet_reader.py`
- `tests/test_import_lansweeper_normalizer.py`
- `tests/test_import_identity_classifier.py`
- `tests/test_import_conflict_detector.py`
- `tests/test_import_row_classifier.py`
- `docs/IMPORT_SERVICE_REFACTOR_PLAN.md`
