# Spreadsheet Import UAT Report

Data da validacao: 2026-06-02  
Ambiente: Docker Compose project `itam_spreadsheet_uat` em `http://127.0.0.1:8080`  
Responsavel tecnico: validacao automatizada por API autenticada, com PostgreSQL e Redis reais.

## Resumo Executivo

Resultado: **APROVADO COM RESSALVAS CONTROLADAS**.

O pipeline de importacao por CSV/XLSX foi validado com fixtures pequenas e com uma amostra real de 50 linhas extraida da planilha fornecida. A planilha original possui 2025 linhas e 56 colunas; ela **nao foi importada integralmente**, conforme regra de nao aceitar importacao completa antes da validacao pequena.

Foram validados:

- backup antes da importacao;
- upload CSV valido;
- upload XLSX valido;
- upload duplicado;
- upload invalido;
- upload com payload de formula maliciosa;
- mapping manual;
- apply explicito;
- busca no modulo Ativos;
- reflexo no Dashboard;
- auditoria de upload e apply;
- backup pos-importacao;
- preservacao de campos protegidos em reimportacao.

## Backups

Backup pre-importacao final:

- `backups/itam_backup_20260602_112308.dump`
- `backups/itam_backup_20260602_112308.manifest.json`

Backup pos-importacao final:

- `backups/itam_backup_20260602_112701.dump`
- `backups/itam_backup_20260602_112701.manifest.json`

Tambem houve backups intermediarios durante a preparacao do ambiente:

- `backups/itam_backup_20260602_111946.dump`
- `backups/itam_backup_20260602_112128.dump`
- `backups/itam_backup_20260602_112458.dump`

## Arquivos Testados

| Cenario | Arquivo | Linhas | Colunas | Status | Criadas | Atualizadas | Invalidas | Conflitos |
|---|---|---:|---:|---|---:|---:|---:|---:|
| CSV valido | `tests/fixtures/imports/itam_valid.csv` | 2 | 14 | APPLIED | 2 | 0 | 0 | 0 |
| XLSX valido | `tests/fixtures/imports/itam_valid.xlsx` | 1 | 14 | APPLIED | 1 | 0 | 0 | 0 |
| CSV duplicado | `tests/fixtures/imports/itam_duplicate.csv` | 2 | 11 | READY_TO_APPLY | 0 | 0 | 0 | 1 |
| CSV invalido | `tests/fixtures/imports/itam_invalid.csv` | 1 | 11 | REVIEW_REQUIRED | 0 | 0 | 1 | 0 |
| CSV formula | `tests/fixtures/imports/itam_formula_injection.csv` | 2 | 11 | REVIEW_REQUIRED | 0 | 0 | 2 | 0 |
| XLSX real amostra | `uat_evidence/spreadsheet_import_20260602_111907/Assets_sample_50.xlsx` | 50 | 56 | APPLIED | 50 | 0 | 0 | 0 |

Total aplicado no cenario controlado: **53 ativos criados**.

## Planilha Real

Arquivo original informado:

- `C:\Users\estevao.quality\Downloads\Assets_09afc1b5-060c-48e4-902f-7ee1dab58bac.xlsx`

Caracteristicas detectadas:

- Aba: `report`
- Linhas de dados: 2025
- Colunas: 56
- Amostra criada: `uat_evidence/spreadsheet_import_20260602_111907/Assets_sample_50.xlsx`

Colunas detectadas na planilha real:

`Name`, `Type`, `Scanning Issues`, `Domain`, `lastuser`, `OS`, `Model`, `Manufacturer`, `IP Address`, `IP Location`, `MAC Address`, `OU`, `State`, `Firstseen`, `Lastseen`, `LastTried`, `Description`, `Purchase Date`, `Warranty Date`, `FQDN`, `DNS Name`, `Last Patched`, `Last Full Backup`, `Last Full Image`, `Location`, `Building`, `Department`, `Branchoffice`, `Barcode`, `Contact`, `Serialnumber`, `Order Number`, `Custom1` ... `Custom20`, `ScannedByFeature`, `SccmServers`, `Not Affected by Cleanup Options`, `Scanserver`.

Mapping detectado na amostra real:

| Coluna externa | Campo interno |
|---|---|
| `Name` | `hostname` |
| `Type` | `asset_type` |
| `lastuser` | `user` |
| `OS` | `operating_system` |
| `Model` | `model` |
| `Manufacturer` | `manufacturer` |
| `IP Address` | `ip_address` |
| `Lastseen` | `last_login` |
| `Location` | `location` |
| `Barcode` | `patrimony` |
| `Serialnumber` | `serial` |

Observacao: `State` nao foi usado automaticamente como `status`. Isso e intencionalmente conservador, pois status operacional do inventario interno e campo protegido.

## Preview, Staging E Paginacao

Validacao:

- Preview da amostra real retornou **20 itens**, mesmo com 50 linhas importadas.
- Staging foi validado com pagina de 10 itens e total 50.
- Endpoint de staging aceita paginacao e nao exige carregar a planilha inteira no frontend.
- O contrato correto do preview usa `items`, `columns` e `detected_mapping`.

Evidencias:

- `uat_evidence/spreadsheet_import_20260602_111907/spreadsheet_import_api_validation.json`
- `uat_evidence/spreadsheet_import_20260602_111907/spreadsheet_import_api_validation_complement.json`

## Conflitos E Erros

CSV duplicado:

- 2 linhas processadas.
- 1 linha valida.
- 1 conflito detectado.
- Conflito classificado por identidade duplicada no arquivo.

CSV invalido:

- 1 linha processada.
- 1 linha invalida.
- Erros retornam linha, campo e motivo via `/validation-errors`.

CSV com formula maliciosa:

- 2 linhas processadas.
- 2 linhas invalidas.
- Payloads iniciados por prefixos de formula foram bloqueados.

Resultado operacional:

- Linhas invalidas e conflitos nao foram aplicados automaticamente.
- O usuario consegue consultar staging, conflitos e erros antes de qualquer apply.

## Apply E Confirmacao

O apply nao ocorre no upload. A aplicacao exige chamada explicita em:

- `POST /api/v1/imports/{id}/apply`

No frontend, o fluxo exige confirmacao antes do apply e bloqueia aplicacao quando ha linhas invalidas ou conflitos.

Relatorio final do cenario controlado:

- CSV valido: 2 criados.
- XLSX valido: 1 criado.
- XLSX real amostra 50: 50 criados.
- Duplicado/invalido/formula: nao aplicados no cenario UAT.

## Campos Protegidos

Foi executada reimportacao controlada com o mesmo serial `SN-IMP-001` e tentativa de alterar campos protegidos.

Resultado observado:

- `hostname` e `ip_address` foram atualizados como campos tecnicos confiaveis.
- `status` permaneceu `STOCK`.
- `location` permaneceu `MATRIZ`.
- `current_user_id` permaneceu `null`.
- `notes` permaneceu `null`.

Evidencia:

- `uat_evidence/spreadsheet_import_20260602_111907/protected_fields_validation.json`

Conclusao: usuario atual, status, localizacao, observacoes e movimentacoes nao sao sobrescritos automaticamente pela politica de merge.

## Ativos, Dashboard E Auditoria

Busca em Ativos:

- `RJMIMP001`: encontrado.
- `022245`: encontrado a partir da amostra real.
- A busca usa o parametro `search`; `q` nao e contrato do endpoint atual.

Dashboard:

- Antes da importacao: `total_assets = 0`.
- Depois da importacao: `total_assets = 53`, `stock = 53`, `without_user = 53`.

Auditoria:

- `import_uploaded`: registrado.
- `import_apply_finished`: registrado.
- Logs possuem action `IMPORT` e entidade `ImportJob`.

## Ajustes Aplicados

1. O upload por planilha foi mantido como staging/preview, sem apply automatico.
2. O mapping manual passou a reprocessar staging, conflitos e erros.
3. Foi corrigido bug no `update_mapping()` que poderia sobrescrever o relatorio recalculado com o estado antigo.
4. Foram ampliados aliases de normalizacao para colunas comuns do Lansweeper, incluindo `Name`, `Serialnumber`, `Barcode`, `lastuser`, `OS`, `IP Address` e `Lastseen`.
5. Validacao de CSV injection foi reforcada para prefixos de formula.
6. Foi adicionado teste de regressao para mapping manual em `tests/test_imports_regression.py`.

## Problemas Encontrados

| Severidade | Problema | Status |
|---|---|---|
| Medio | `update_mapping()` reprocessava, mas podia perder o relatorio recalculado por sobrescrita local. | Corrigido |
| Baixo | Coletor de validacao usou inicialmente `q` em vez de `search` no endpoint de Ativos. | Ajustado na validacao |
| Baixo | Coletor de validacao leu `rows` no preview, mas contrato real usa `items`. | Ajustado na validacao |

Nenhum bug bloqueante foi encontrado no apply, staging, auditoria, dashboard ou protecao de campos criticos.

## Validacoes Executadas

Comandos executados:

- `py -m compileall -q backend/app backend/alembic tests`
- `.venv\Scripts\python.exe -m compileall -q backend/app backend/alembic tests`
- `.venv\Scripts\python.exe -m unittest discover -s tests`
- `npm run build`
- `docker compose config --services`
- `.\scripts\ops\start-uat.ps1 -ProjectName itam_spreadsheet_uat`
- `.\scripts\ops\backup-db.ps1 -ProjectName itam_spreadsheet_uat`

Checks HTTP finais:

- `/health` -> 200
- `/` -> 200
- `/assinaturas/` -> 200
- `/admin/` -> 302
- `/api/v1/assets` sem token -> 401

Resultado dos testes:

- Backend unit/regression: 14 testes OK, 5 skips esperados.
- Frontend build: OK.
- Docker Compose config: `postgres`, `redis`, `app`.

## Evidencias Esperadas Para UAT Visual

Para uma sessao visual com usuario final, capturar:

- tela de upload antes do envio;
- preview com colunas detectadas e mapping;
- staging paginado;
- tela de conflitos para CSV duplicado;
- tela de erros para CSV invalido/formula;
- modal de confirmacao do apply;
- relatorio final com criados/atualizados/ignorados/invalidos/conflitos;
- busca do ativo `022245`;
- dashboard com totais atualizados;
- auditoria filtrada por importacao.

Nao capturar senha, token, cookie ou dados reais sensiveis.

## Riscos Restantes

1. A importacao completa das 2025 linhas originais ainda nao esta aprovada.
2. Ainda e necessario UAT visual com usuario real para validar clareza operacional das mensagens e do modal de confirmacao.
3. Linhas `REVIEW_REQUIRED` precisam de politica operacional antes de permitir apply seletivo futuro.
4. O campo externo `State` do Lansweeper nao deve ser mapeado para status automaticamente sem decisao de produto, pois isso pode alterar governanca de estoque.
5. A busca validada usa `search`; documentar isso para evitar chamadas com `q` por clientes externos.

## Decisao

O pipeline esta apto para **validacao pequena controlada com usuarios reais**.

Nao liberar importacao completa do inventario antes de:

- revisar amostra com equipe de TI;
- confirmar mapping esperado para `Type`, `State`, `Location`, `Barcode` e `Serialnumber`;
- executar UAT visual;
- revisar conflitos e divergencias em lote pequeno adicional.
