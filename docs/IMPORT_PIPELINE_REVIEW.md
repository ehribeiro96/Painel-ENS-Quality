# Revisao do Pipeline de Importacao Lansweeper

Data: 2026-05-15

## Objetivo

Transformar a importacao CSV/XLSX em uma fundacao enterprise de ingestao de inventario: resiliente, auditavel, transacional e preparada para futura integracao com Lansweeper API.

## Diagnostico da Importacao Anterior

O fluxo anterior fazia upload, parse do arquivo e criava um `ImportJob` com preview basico. Isso era adequado para demonstracao inicial, mas fragil para inventario corporativo.

Riscos encontrados:

- Aplicacao direta nao tinha staging persistente.
- Nao havia deduplicacao contra inventario principal.
- Nao havia classificacao de conflito por linha.
- Nao havia politica clara de merge.
- Relatorio nao separava criados, atualizados, ignorados, conflitos e falhas.
- Preview nao era auditavel em tabelas.
- Falhas durante merge poderiam ser dificeis de explicar operacionalmente.
- Arquivos com payload suspeito de formula nao eram bloqueados.
- Limite de linhas nao estava configurado.

## Arquitetura Implementada

Fluxo atual:

```text
Upload
-> Raw Import Record
-> Staging Validation
-> Normalization
-> Conflict Detection
-> Merge Decision
-> Apply Changes
-> Audit + Report
```

Camadas criadas em `backend/app/domains/imports/`:

- `normalization/`: normalizacao de colunas, serial, patrimonio, hostname, fabricante, modelo, usuario e tipo.
- `validators/`: validacoes de identidade, tamanho e payload suspeito.
- `conflict_detection/`: classificacao por linha.
- `merge_engine/`: politica de merge seletivo.
- `staging/`: reservado para evolucao de queries/repositories de staging.
- `future_ai/`: ponto de extensao documentado, sem IA implementada.

## Staging Layer

Foram adicionadas as tabelas:

- `import_staging_assets`
- `import_conflicts`
- `import_validation_errors`

Objetivos atendidos:

- Preview real persistente.
- Revisao posterior de conflitos.
- Relatorio por linha.
- Inventario principal protegido contra linhas invalidas.
- Base para retry/reprocessamento futuro.

## Normalizacao

Implementado:

- `trim`
- uppercase consistente para identificadores
- normalizacao unicode `NFKC`
- compactacao de espacos
- padronizacao de delimitadores em serial/patrimonio/hostname
- aliases de colunas externas
- aliases de fabricantes:
  - `HP Inc.`, `Hewlett-Packard` -> `HP`
  - `Dell Inc.` -> `DELL`
  - variações Lenovo -> `LENOVO`

## Deduplicacao

Prioridade implementada:

1. `serial`
2. `patrimony`
3. `hostname`

Classificacoes:

- `SAFE_MERGE`: linha pode criar ativo ou atualizar campos confiaveis.
- `REVIEW_REQUIRED`: existe match, mas ha divergencia operacional protegida.
- `CONFLICT`: duplicidade no arquivo ou match contra mais de um ativo.
- `INVALID`: linha sem identidade ou com payload inseguro/invalido.

## Merge Policy

Campos que podem ser atualizados por importacao:

- `hostname`
- `patrimony`
- `serial`
- `manufacturer`
- `model`
- `asset_type`
- `operating_system`
- `ip_address`
- `last_login`

Campos protegidos:

- `current_user_id`
- `location`
- `status`
- `notes`
- `movements`

Justificativa: importacao de inventario nao deve sobrescrever estado operacional controlado por movimentacoes auditaveis.

## Auditoria

Toda importacao registra:

- arquivo
- usuario
- origem
- total processado
- criados
- atualizados
- ignorados
- conflitos
- invalidos
- falhas
- `request_id`
- `correlation_id`

Toda criacao/atualizacao de asset por importacao gera auditoria em `AuditLog` com `source = lansweeper_import`.

## Performance e Escalabilidade

Melhorias aplicadas:

- prefetch dos ativos existentes por serial/patrimonio/hostname
- limite configuravel `IMPORT_MAX_ROWS`
- limite configuravel `UPLOAD_MAX_MB`
- indices em staging por job, decisao e identidade
- indices em conflitos por job/severidade

Ainda intencionalmente nao implementado:

- streaming real de XLSX
- fila assíncrona
- processamento distribuido
- particionamento de tabelas

Esses itens devem entrar quando volumes reais justificarem.

## Seguranca

Protecoes adicionadas:

- bloqueio por extensao permitida `.csv`/`.xlsx`
- limite de tamanho
- limite de linhas
- parsing com `dtype=str`
- bloqueio de valores iniciando com `=`, `+`, `-`, `@` para reduzir risco de formula injection em relatórios/exportacoes futuras
- nao confiar em nomes de colunas externas; aliases passam por normalizacao

## Impacto Operacional

O operador passa a ter:

- preview real de linhas processadas
- contagem de criados/atualizados/conflitos/invalidos
- decisao por linha
- conflitos revisaveis
- merge seguro sem sobrescrever usuario/status/local

## Divida Tecnica Restante

- Adicionar testes unitarios para normalizacao, deduplicacao e merge policy.
- Adicionar teste de integracao com Postgres para rollback de importacao.
- Criar tela conectada aos endpoints reais de staging/conflitos.
- Criar comando de reprocessamento de linhas `REVIEW_REQUIRED`.
- Evoluir para job assíncrono quando arquivos reais passarem de dezenas de milhares de linhas.

## Proximos Passos Recomendados

1. Criar suite de regression tests com arquivos CSV/XLSX reais anonimizados.
2. Adicionar endpoint controlado para aplicar manualmente linhas `REVIEW_REQUIRED`.
3. Implementar repository dedicado para queries de staging se o service crescer.
4. Adicionar mecanismo de idempotencia por hash de arquivo.
5. Preparar importacao incremental da API Lansweeper usando as mesmas camadas.
