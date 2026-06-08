# Pipeline de Importacao por Planilha

## Objetivo

Permitir que a equipe de TI importe inventario por CSV/XLSX com staging, validacao, preview, decisao humana, merge seguro, auditoria e relatorio final. A planilha e a fonte operacional temporaria ate futura integracao com Lansweeper API.

## Formatos Suportados

- `.csv`
- `.xlsx`

Nao suportado nesta fase:

- `.xlsm`
- arquivos compactados
- executaveis
- arquivos acima de `UPLOAD_MAX_MB`
- planilhas acima de `IMPORT_MAX_ROWS`

## Fluxo

```text
Upload
-> Raw rows
-> Staging
-> Validacao
-> Normalizacao
-> Deteccao de conflitos
-> Decisao de merge
-> Confirmacao humana
-> Apply seguro
-> Auditoria + relatorio
```

O upload nao grava automaticamente na tabela final de ativos. A aplicacao so ocorre via `POST /api/v1/imports/{id}/apply`.

## Endpoints

- `POST /api/v1/imports/spreadsheet/upload`
- `GET /api/v1/imports`
- `GET /api/v1/imports/{id}`
- `GET /api/v1/imports/{id}/preview`
- `GET /api/v1/imports/{id}/staging`
- `GET /api/v1/imports/{id}/conflicts`
- `GET /api/v1/imports/{id}/validation-errors`
- `POST /api/v1/imports/{id}/mapping`
- `POST /api/v1/imports/{id}/apply`
- `POST /api/v1/imports/{id}/cancel`
- `GET /api/v1/imports/{id}/report`
- `POST /api/v1/imports/lansweeper` permanece compativel e usa o mesmo staging.

## Campos Aceitos

O sistema aceita variacoes comuns:

- Hostname: `Hostname`, `Host`, `Computer`, `AssetName`, `Nome do computador`, `Nome do ativo`
- Serial: `Serial`, `Serial Number`, `Service Tag`, `Numero de serie`, `SN`
- Patrimonio: `Patrimonio`, `Asset Tag`, `AssetTag`, `Numero Patrimonio`
- Usuario: `Usuario`, `User`, `Last User`, `Last Logged On User`, `Colaborador`
- E-mail: `Email`, `E-mail`, `E-mail do usuario`
- Modelo: `Modelo`, `Model`, `Device Model`
- Fabricante: `Fabricante`, `Manufacturer`, `Marca`, `Vendor`
- Localizacao: `Localizacao`, `Location`, `Unidade`, `Site`
- SO/IP/ultimo login/status/observacoes tambem sao aceitos.

## Preset Lansweeper Assets Export

Preset: `Lansweeper Assets Export`  
Versao: `2026.06.ENS.1`

O preset e detectado automaticamente quando a planilha possui colunas como `Name`, `Type`, `Custom1`, `Serialnumber`, `State` e `Scanserver`.

Mapping oficial:

- `hostname <- Name`
- `asset_type <- Custom1`
- `fallback_asset_type <- Type`
- `manufacturer/brand <- Manufacturer`
- `model <- Model`
- `serial <- Serialnumber`
- `patrimony <- Barcode`, somente se houver valores uteis
- `status/source_state <- State`
- `location <- Location`
- `source_metadata.unit <- Building`
- `source_metadata.network_location <- IP Location`
- `ip_address <- IP Address`
- `operating_system <- OS`
- `source_metadata.imported_user_hint <- lastuser`
- `source_metadata.first_seen/last_seen/last_tried/fqdn/dns_name/source_notes/source`

Se `Barcode` estiver 100% vazio, o sistema nao mapeia patrimonio, nao usa patrimonio na deduplicacao e exibe:

```text
Coluna de patrimônio vazia nesta planilha. Os ativos serão identificados por serial e hostname.
```

`Name` deve ser usado como hostname somente quando parecer um identificador de
ativo. Se o valor for um IP ou outro identificador nao confiavel, deve ser
preservado como IP/metadado e nao deve virar hostname operacional.

O destino canonico do apply e o PostgreSQL. A planilha nao cria banco paralelo e
nao reativa SQLite legado.

## Modos de Importacao

- `INITIAL_LOAD`: permite preencher `status` e `location` em ativos novos.
- `SAFE_REIMPORT`: preserva `status`, `location` e `current_user_id` de ativos existentes.
- `PREVIEW_ONLY`: gera staging e relatorio, mas bloqueia apply.

Ativos existentes nunca tem usuario, status ou localizacao sobrescritos por importacao.

## Regras Lansweeper

Valores nulos globais: vazio, `Undefined`, `Not scanned`, `nan`, `none`, `null`, `N/A`, `NA`, `-`.

O valor `66` so vira null em colunas onde foi comprovado como placeholder: `Model`, `Manufacturer`, `Location`, `Contact`, `Custom1`, `Custom2`.

Seriais invalidos nao sao usados como identidade forte:

- `Undefined`
- `Not scanned`
- `To be filled by O.E.M.`
- `System Serial Number`
- `Default String`
- `00000000`
- `123456789`
- `N/A`
- `None`
- `Null`

Conversao de `State`:

- `Active`: `IN_USE` apenas para `NOTEBOOK`/`DESKTOP` com identidade minima; caso contrario `CONFIG_PENDING`.
- `Stock`: `STOCK`.
- `Broken`: `DEFECTIVE`.
- `Sold`: `DISCARDED` com `source_disposal_reason=sold`.
- `Donate`: `DISCARDED` com `source_disposal_reason=donated`.
- `Stolen`: `DISCARDED` com `source_disposal_reason=stolen`.
- `Non-active`: `CONFIG_PENDING`.

`lastuser` e preservado somente como `source_metadata.imported_user_hint`. Ele nao cria usuario, nao vincula `current_user_id` e nao gera movimentacao.

## Qualidade do Preview

O report inclui:

- `preset_name`, `preset_version`, `detected_sheet`, `schema_signature`.
- `detected_columns`, `missing_expected_columns`, `empty_columns`, `warnings`.
- `summary`: linhas com/sem serial, hostname, patrimonio, user hint, localizacao, status e tipo reconhecidos.
- `distributions`: `state`, `custom1`, `asset_family`, `location`, `building`.
- `quality`: percentuais de qualidade e decisoes.

Cada linha de staging inclui `identity_confidence`:

- `HIGH`: serial ou patrimonio valido.
- `MEDIUM`: hostname valido.
- `LOW`: acessorio/periferico sem serial/patrimonio, mas com nome coerente.
- `NONE`: sem identificador util.

## Validacao

Cada linha precisa ter pelo menos um identificador forte:

- serial
- patrimonio
- hostname

Sem identificador, a linha vira `INVALID`.

Tambem sao validados:

- prefixo de formula perigosa: `=`, `+`, `-`, `@`, `*`
- e-mail minimamente valido
- IP valido quando informado
- tipo de ativo conhecido
- tamanho dos identificadores

## Normalizacao

- Trim em campos.
- Espacos duplicados removidos.
- Hostname, serial e patrimonio em maiusculo.
- Fabricante padronizado, por exemplo `HP Inc.` -> `HP`.
- Valores vazios viram `null`.
- Tipo de equipamento normalizado para enum interno.

## Duplicidade e Decisao

Prioridade:

1. serial
2. patrimonio
3. hostname
4. `source_external_key` de origem Lansweeper para linhas sem identidade forte

Regras especificas Lansweeper:

- `Barcode` 100% vazio nao e mapeado como patrimonio.
- `Name` em formato de IP nao vira hostname; o valor vai para `ip_address`.
- Linhas IP-only recebem `source_external_key` em staging/report e ficam `REVIEW_REQUIRED`.
- `lastuser` fica somente em `source_metadata.imported_user_hint`.
- `Custom1` vence `Type`; `Type` e fallback.
- `Undefined`, `Not scanned`, `nan`, `none`, `null`, `N/A`, `NA`, `-`, vazio e `66` viram `null`.

Classificacoes:

- `CREATE`: novo ativo seguro para criacao.
- `SAFE_UPDATE`: ativo existente com atualizacao tecnica segura.
- `REVIEW_REQUIRED`: precisa revisao humana.
- `CONFLICT`: conflito operacional.
- `INVALID`: linha invalida.
- `SKIPPED`: nao aplicada.

## Politica de Merge

Pode atualizar automaticamente:

- hostname
- patrimonio, se aplicavel
- serial, se aplicavel
- fabricante
- modelo
- tipo
- sistema operacional
- IP
- ultimo login

Nao sobrescreve automaticamente:

- usuario atual
- status
- localizacao de ativo existente
- observacoes
- movimentacoes
- historico
- baixa/manutencao/defeito

Trocas de usuario/status/localizacao devem acontecer via movimentacao auditada, nao via overwrite silencioso de planilha.

## Como Importar no Frontend

1. Fazer backup.
2. Acessar `Importacao por planilha`.
3. Enviar CSV/XLSX.
4. Revisar preview.
5. Ajustar mapeamento se necessario.
6. Revisar staging, erros e conflitos.
7. Aplicar apenas se estiver seguro.
8. Conferir relatorio final.
9. Buscar ativos importados.
10. Conferir auditoria.

## Backup Antes de Planilha Real

Antes de importar planilha real:

```powershell
.\scripts\ops\backup-db.ps1 -ProjectName itam_uat
```

Nao importar inventario real sem backup recente.

## Planilha Corrigida Lansweeper 2026-06-03

Arquivo analisado localmente sem apply:

`c:\Users\estevao.quality\Desktop\Planilha.xlsx`

Resultado do pipeline:

| Metrica | Valor |
| --- | ---: |
| Aba detectada | `report` |
| Linhas | 1715 |
| Colunas | 56 |
| Preset | `Lansweeper Assets Export` |
| Barcode valido | 0 |
| Seriais validos | 1046 |
| Patrimonios normalizados | 0 |
| Hints de usuario | 273 |
| `Name` IP tratado como IP | 2 |
| `source_external_key` fraco para revisao | 2 |
| `CREATE` seguro no staging local | 1693 |
| `REVIEW_REQUIRED` | 2 |
| `CONFLICT` | 14 |
| `SKIPPED_DUPLICATE_IN_FILE` | 6 |

Validacao UAT:

- backup antes do upload: `backups\itam_backup_20260603_095548.dump`;
- import id: `bf8c7125-e0dc-4b9a-b46a-ac92bbd18b68`;
- upload/preview/staging/conflitos/erros/report responderam sem erro generico;
- staging paginado com `page_size=200` validado;
- apply nao executado.

Casos obrigatorios confirmados:

- `192.168.3.43` e `192.168.3.44` nao viram hostname.
- `RJM21896` aparece em 6 linhas e e explicado por conflito/revisao de identidade.
- 4 grupos de serial duplicado aparecem como conflito real.
- `RJM011HP` e `RJM012HP` usam `Custom1=MONITOR`, mesmo quando `Type=Windows`.
- `lastuser` continua apenas como hint.

## Validacao Por Amostras

Nao aplicar diretamente o arquivo completo de 2025 linhas. Fluxo recomendado:

1. Aplicar fixture pequena.
2. Aplicar `sample_50_lansweeper.xlsx`.
3. Validar dashboard, ativos e auditoria.
4. Aplicar `sample_200_lansweeper.xlsx`.
5. Validar performance, staging e relatorio.
6. So entao validar o arquivo completo.

## Como Interpretar Conflitos

- `duplicate_in_file`: a propria planilha repetiu identificador.
- `multiple_assets_match`: serial/patrimonio/hostname apontam para ativos diferentes.
- `location_divergence`: planilha diverge da localizacao atual.
- `user_requires_review`: planilha sugere usuario, mas ativo ja possui usuario atual.

## Como Corrigir Planilha

- Remover linhas duplicadas.
- Garantir serial/patrimonio/hostname.
- Remover formulas.
- Corrigir IP/e-mail.
- Separar movimentacoes operacionais de atualizacoes tecnicas.

## Testes Executados

- Upload CSV valido.
- Upload XLSX valido.
- CSV duplicado.
- CSV invalido.
- CSV com formula bloqueada.
- Preview.
- Staging.
- Apply seguro.
- Busca de ativo importado.
- Auditoria de importacao.

## Proximas Etapas

- Resolver revisoes manuais no fluxo de UI com politica explicita.
- Exportar relatorio em arquivo, se necessario.
- Preparar sync incremental quando a Lansweeper API for integrada.
