# Import Service Refactor Plan

## Mapa de responsabilidades atual

1. Upload e criação de job:
   - `upload_spreadsheet()`
   - `import_lansweeper()`
2. Leitura CSV/XLSX:
   - `_parse_file()`
3. Seleção de aba:
   - `_parse_file()`
4. Detecção de preset:
   - `detect_import_preset()`
   - `effective_mapping()`
5. Mapping:
   - `update_mapping()`
   - `_detected_mapping()`
6. Normalização:
   - `normalize_asset_row()`
   - `normalize_column_name()`
7. Identidade:
   - `identity_for()`
   - `analyze_identity()`
   - `is_valid_serial()`
   - `is_valid_patrimony()`
   - `is_valid_hostname()`
   - `is_ip_only()`
8. Conflitos:
   - `build_internal_duplicate_plan()`
   - `detect_row_conflict()`
9. Classificação:
   - `classify_row()`
10. Validação:
   - `validate_raw_row_security()`
   - `validate_normalized_asset()`
11. Validation errors:
   - `_persist_row_issues()`
12. Staging:
   - `upload_spreadsheet()`
13. Preview:
   - `_build_report()` / staging endpoints
14. Report:
   - `_build_report()`
   - `_build_summary()`
   - `_build_distributions()`
   - `_build_quality()`
15. Apply:
   - `apply_import()`
   - `_apply_safe_merges()`
16. Merge seguro:
   - `apply_trusted_updates()`
   - `build_asset_from_import()`
17. Auditoria:
   - `AuditService.record()`
18. Paginação:
   - endpoints de listagem/staging usam paginação de API
19. Cancelamento:
   - `cancel_import()`

## Dependências internas

- Parsing alimenta upload e update mapping.
- Normalização alimenta identidade, deduplicação e conflitos.
- Classificação depende de normalização e de assets existentes.
- Report consome staging, classificação e métricas.
- Apply depende de staging, merge policy e auditoria.

## Funções grandes

- `upload_spreadsheet()`
- `apply_import()`
- `update_mapping()`
- `_build_internal_duplicate_plan()`
- `_classify_row()`
- `_apply_safe_merges()`
- `_build_report()`

## Normalização Lansweeper mapeada no `service.py`

- `_detected_mapping()` normaliza colunas de entrada para nomes canônicos.
- `upload_spreadsheet()` e `update_mapping()` constroem `raw_rows` e chamam `normalize_asset_row()` sobre cada linha.
- `_build_internal_duplicate_plan()` usa `identity_for()` para agrupar duplicatas equivalentes.
- `_classify_row()` consome a saída normalizada, mas não deve alterar regras de classificação nesta rodada.
- O conjunto de normalização atual em `backend/app/domains/imports/normalization/asset_normalizer.py` cobre:
  - placeholders globais e por coluna;
  - normalização de `Name`/hostname versus IP;
  - `Barcode`/patrimônio;
  - `Custom1` versus `Type`;
  - `lastuser` como hint em metadados;
  - fabricante, modelo, SO, localização e `source_metadata`;
  - identidade forte/fraca via `identity_for()`, hoje como fachada temporária.

## Identidade e classificação mapeadas no `service.py`

- `_build_internal_duplicate_plan()` foi o bloco de deduplicação interna por identidade.
- `_classify_row()` combinava validação, duplicidade e conflito com ativos existentes.
- `identity_for()` hoje existe em `backend/app/domains/imports/normalization/lansweeper_normalizer.py` como fachada temporária.
- A regra real de identidade será centralizada em `backend/app/domains/imports/classification/identity_classifier.py`.
- A regra de conflito/deduplicação será centralizada em `backend/app/domains/imports/classification/conflict_detector.py`.
- A combinação final de decisão por linha será centralizada em `backend/app/domains/imports/classification/row_classifier.py`.

## Blocos extraíveis

- Parsing/leitura de planilha.
- Normalização Lansweeper.
- Classificação e identidade.
- Report e métricas.
- Apply e merge seguro.

## Módulos propostos

- `backend/app/domains/imports/parsing/spreadsheet_reader.py`
- `backend/app/domains/imports/normalization/lansweeper_normalizer.py`
- `backend/app/domains/imports/classification/identity_classifier.py`
- `backend/app/domains/imports/classification/conflict_detector.py`
- `backend/app/domains/imports/reporting/staging_reporter.py`
- `backend/app/domains/imports/apply/apply_executor.py`
- `backend/app/domains/imports/apply/merge_policy.py`

## Ordem de extração

1. Parsing e leitura de planilha.
2. Normalização Lansweeper.
3. Classificação e identidade.
4. Report e métricas.
5. Apply e merge seguro.

## Riscos por etapa

- Parsing: baixo, se mantiver DataFrame/sheet compatíveis.
- Identidade/classificação: médio/alto, porque afeta estados, conflitos e duplicidade.
- Report: médio, porque afeta contrato com frontend/API.
- Apply: alto, porque toca persistência e auditoria.

## Testes que protegem cada etapa

- Parsing:
  - CSV válido
  - XLSX com aba `report`
  - aba ausente
  - arquivo vazio
  - extensão inválida
- Normalização:
  - IP no `Name`
  - `lastuser` como hint
  - `Barcode` vazio
  - `Undefined` e `Not scanned`
  - `Custom1` vence `Type`
  - `Name` válido preservado como hostname
  - `Name` com IP não vira hostname
  - placeholders numéricos
- Identidade:
  - serial válido é forte
  - patrimônio válido é forte
  - hostname válido e não-IP
  - IP-only é fraca/revisão
- Conflitos:
  - serial duplicado
  - hostname duplicado
  - duplicata equivalente
  - IP-only em revisão
  - reason/conflict_key/recommended_action
- Classificação:
  - CREATE
  - SAFE_UPDATE
  - REVIEW_REQUIRED
  - CONFLICT
  - INVALID
  - SKIPPED_DUPLICATE_IN_FILE
- Report:
  - contadores e avisos
  - conflitos e erros
  - duplicates e quality
- Apply:
  - parcial
  - falha isolada
  - preservação de campos operacionais
  - auditoria

## Extração executada nesta rodada

- Somente parsing e leitura de planilha.
- `backend/app/domains/imports/service.py` passou a delegar leitura para `backend/app/domains/imports/parsing/spreadsheet_reader.py`.
- O fluxo de serviço permaneceu como orquestrador; normalização, classificação, conflito, report e apply não foram alterados.
- O parser preserva o fallback atual para a primeira aba quando `report` não existe no uso do serviço, enquanto o modo estrito foi coberto por teste isolado para validar o erro funcional sem mudar o contrato validado.

## Extração 2 executada nesta rodada

- A normalização Lansweeper passou a ser consumida pelo módulo `backend/app/domains/imports/normalization/lansweeper_normalizer.py`.
- `service.py` agora usa a fachada nova para `normalize_asset_row()`, `identity_for()` e `normalize_column_name()`.
- O comportamento de normalização permaneceu o mesmo:
  - IP em `Name` segue virando `ip_address` e não hostname;
  - `lastuser` continua como hint em `source_metadata`;
  - `Barcode` vazio continua não criando patrimônio;
  - `Custom1` continua vencendo `Type`.

## Extração 3 planejada nesta rodada

- A identidade será movida para `backend/app/domains/imports/classification/identity_classifier.py`.
- A duplicidade e o conflito serão centralizados em `backend/app/domains/imports/classification/conflict_detector.py`.
- A decisão por linha será centralizada em `backend/app/domains/imports/classification/row_classifier.py`.
- `identity_for()` continuará como fachada temporária em `normalization/lansweeper_normalizer.py` para compatibilidade, sem duplicar regra efetiva.

## Extração 3 executada nesta rodada

- `backend/app/domains/imports/classification/identity_classifier.py` foi criado para centralizar identidade forte/fraca, IP-only, validade de hostname/serial/patrimony e estrutura de análise.
- `backend/app/domains/imports/classification/conflict_detector.py` foi criado para centralizar deduplicação interna, conflitos e enriquecimento de motivos/recomendações.
- `backend/app/domains/imports/classification/row_classifier.py` foi criado para centralizar a decisão final por linha.
- `service.py` passou a delegar essas decisões para os módulos novos, mantendo a orquestração e os contratos.
- `identity_for()` permaneceu como fachada de compatibilidade em `normalization/lansweeper_normalizer.py`, mas a regra efetiva ficou centralizada no módulo de identidade.
- Os testes novos cobrem serial/patrimônio/hostname/IP-only, conflito, duplicata equivalente, `CREATE`, `SAFE_UPDATE`, `REVIEW_REQUIRED`, `CONFLICT`, `INVALID` e `SKIPPED_DUPLICATE_IN_FILE`.
