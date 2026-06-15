# Import Pipeline / Staging B3 Report

## 1. Resumo Executivo

A boundary `B3 — Import pipeline/staging` foi concluída com sucesso funcional e sem alteração de código nesta rodada final. O pipeline de importação já estava refatorado de forma progressiva em rodadas anteriores e passou pela validação B3 dedicada nesta sessão sem regressão.

Resultado final: `GO`.

## 2. Escopo B3

- `backend/app/domains/imports/`
- `backend/app/domains/imports/service.py`
- `backend/app/domains/imports/normalization/`
- `backend/app/domains/imports/parsing/`
- `backend/app/domains/imports/classification/`
- `tests/test_import_*`
- `tests/fixtures/imports/`
- documentação operacional B3 em `docs/`

Fora de escopo nesta rodada:

- AI Chat
- frontend
- CSS
- migrations
- Docker
- Ollama/Hermes config
- `.env`, dumps, bancos, tokens e credenciais

## 3. Estado Baseline Antes da Edição

- Branch: `main`
- Relação com upstream: `main...origin/main [ahead 1]`
- `git diff --cached --name-status`: vazio
- Worktree: suja por mudanças preexistentes fora desta boundary
- `compileall` B3: passou
- `ruff` B3: passou
- `pytest` B3 dedicado: primeira execução falhou por captura ao encerrar; retry com `-s` passou

## 4. Arquitetura Atual do Pipeline

O `ImportService` continua como orquestrador em [backend/app/domains/imports/service.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/service.py), delegando para:

- [backend/app/domains/imports/parsing/spreadsheet_reader.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/parsing/spreadsheet_reader.py)
- [backend/app/domains/imports/normalization/lansweeper_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/normalization/lansweeper_normalizer.py)
- [backend/app/domains/imports/classification/identity_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/identity_classifier.py)
- [backend/app/domains/imports/classification/conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/conflict_detector.py)
- [backend/app/domains/imports/classification/row_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/row_classifier.py)

Fluxo validado:

- parsing CSV/XLSX
- seleção de aba `report` com fallback preservado no serviço
- normalização Lansweeper
- identidade forte/fraca
- deduplicação interna
- classificação por linha
- staging
- preview/report
- apply parcial

## 5. Problemas Encontrados

Nenhum problema funcional novo foi encontrado no recorte B3 desta sessão. O que apareceu foi apenas limitação de ambiente em comandos de descoberta do `pytest` com captura padrão, já conhecida em rodadas anteriores.

## 6. Correções Aplicadas

Nenhuma correção de código foi necessária nesta rodada final. O código do pipeline já estava estabilizado e passou na validação dedicada de B3.

## 7. Arquivos Alterados

Nesta rodada de fechamento, apenas documentação foi atualizada:

- [docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md)
- [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
- [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md)

## 8. Testes Executados Antes/Depois

Comandos executados nesta rodada:

```bash
PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app/domains/imports tests
timeout 120 .venv/bin/python -m ruff check backend/app/domains/imports tests
PYTHONPATH=backend timeout 120 .venv/bin/python -m pytest tests -q --collect-only -s -o addopts='' | grep -Ei 'import|imports|staging|lansweeper' || true
PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_import_conflict_detector.py tests/test_import_identity_classifier.py tests/test_import_lansweeper_normalizer.py tests/test_import_pipeline_units.py tests/test_import_row_classifier.py tests/test_import_spreadsheet_reader.py tests/test_imports_regression.py tests/test_legacy_ens_db_importer.py -q -o addopts=''
PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_import_conflict_detector.py tests/test_import_identity_classifier.py tests/test_import_lansweeper_normalizer.py tests/test_import_pipeline_units.py tests/test_import_row_classifier.py tests/test_import_spreadsheet_reader.py tests/test_imports_regression.py tests/test_legacy_ens_db_importer.py -q -s -o addopts=''
```

Resultado:

- `compileall`: passou.
- `ruff`: passou.
- `pytest` B3 dedicado: passou no retry com `-s` (`54 passed, 5 skipped`).
- `collect-only`: passou com `-s` e listou a cobertura B3 real; a variante sem `-s` falhou por captura no encerramento.

## 9. Resultado de Parsing

Validado por:

- [tests/test_import_spreadsheet_reader.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_spreadsheet_reader.py)
- [tests/test_imports_regression.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_imports_regression.py)

Resultados:

- CSV válido carrega sem sheet.
- XLSX com aba `report` usa a aba correta.
- Aba ausente pode ser rejeitada em modo estrito de teste.
- Arquivo vazio e extensão inválida seguem como erro funcional.

## 10. Resultado de Normalização

Validado por:

- [tests/test_import_lansweeper_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_lansweeper_normalizer.py)
- [tests/test_import_pipeline_units.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_pipeline_units.py)

Resultados:

- IP em `Name` não vira hostname.
- `lastuser` continua como hint em metadados.
- `Barcode` vazio não vira patrimônio.
- `Undefined` e `Not scanned` viram nulo.
- `Custom1` vence `Type`.
- Nome válido segue como hostname quando apropriado.

## 11. Resultado de Classificação

Validado por:

- [tests/test_import_identity_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_identity_classifier.py)
- [tests/test_import_conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_conflict_detector.py)
- [tests/test_import_row_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_pipeline_units.py)

Resultados:

- serial válido continua forte;
- patrimônio válido continua forte;
- hostname não-IP continua válido;
- IP-only segue para revisão;
- conflito real continua bloqueante;
- duplicata equivalente continua `SKIPPED_DUPLICATE_IN_FILE`;
- `CREATE`, `SAFE_UPDATE`, `REVIEW_REQUIRED`, `CONFLICT`, `INVALID` e `SKIPPED_DUPLICATE_IN_FILE` ficaram cobertos.

## 12. Resultado de Staging / Idempotência

Validado por:

- [tests/test_import_pipeline_units.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_pipeline_units.py)
- [tests/test_imports_regression.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_imports_regression.py)

Resultados:

- staging preserva preview e report;
- apply parcial segue ativo;
- duplicatas equivalentes não quebram o lote;
- conflitos reais permanecem bloqueantes;
- reimportação segura preserva campos operacionais validados.

## 13. Scanner Redigido

Escopo do scanner nesta rodada:

- [backend/app/domains/imports/service.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/service.py)
- [backend/app/domains/imports/normalization/asset_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/normalization/asset_normalizer.py)
- [backend/app/domains/imports/parsing/spreadsheet_reader.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/parsing/spreadsheet_reader.py)
- [backend/app/domains/imports/classification/identity_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/identity_classifier.py)
- [backend/app/domains/imports/classification/conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/conflict_detector.py)
- [backend/app/domains/imports/classification/row_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/imports/classification/row_classifier.py)
- [tests/test_import_conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_conflict_detector.py)
- [tests/test_import_identity_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_identity_classifier.py)
- [tests/test_import_lansweeper_normalizer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_lansweeper_normalizer.py)
- [tests/test_import_pipeline_units.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_pipeline_units.py)
- [tests/test_import_row_classifier.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_row_classifier.py)
- [tests/test_import_spreadsheet_reader.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_spreadsheet_reader.py)
- [tests/test_imports_regression.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_imports_regression.py)
- [tests/test_legacy_ens_db_importer.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_legacy_ens_db_importer.py)
- [docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md)
- [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
- [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md)

Classificação resumida:

- `eval`: resolvido em B2; não reapareceu no escopo B3.
- `dangerouslySetInnerHTML`: resolvido em B2; não reapareceu no escopo B3.
- `COMPOSIO_API_KEY`: esperado em docs fora do escopo funcional B3.
- `api_key`, `secret`, `token`, `password`, `private_key`, `sk-`, `bearer`: apenas em testes/documentação histórica ou asserções negativas, sem exposição de valor sensível.

## 14. Riscos Remanescentes

- O worktree geral continua misturado com outras boundaries pré-existentes.
- O frontend build permanece como pendência ambiental separada, não relacionada ao importador.
- O importador ainda tem grandes responsabilidades em `ImportService`, embora a refatoração já esteja bem segmentada.

## 15. Itens Fora de Escopo

- AI Chat
- frontend
- CSS
- migrations
- Docker
- Ollama/Hermes config
- `.env`, dumps, bancos, tokens e credenciais
- `tools/hermesops_offline/*`
- `tools/hmlops_cli/*`
- Laravel legado

## 16. Próximo Passo Recomendado

`B4 — Frontend shell/UX`

Motivo:

- `B3` foi fechado com validação dedicada concluída;
- a próxima fronteira funcional natural é o frontend shell/UX;
- as pendências de build e smoke visual já estão documentadas para essa boundary.
