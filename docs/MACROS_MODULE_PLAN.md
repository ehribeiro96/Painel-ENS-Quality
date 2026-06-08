# Macros Module Plan

## Objetivo

O modulo de macros transforma templates reais do Service Desk em registros controlados no PostgreSQL. O foco inicial e apoiar atendimentos operacionais e gerar macro de movimentacao de ativos apos uma movimentacao registrada.

## Fontes de seed

- `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json`: fonte oficial atual de seed para `macro_templates`.
- `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json`: fonte oficial atual de autocomplete/hint para `macro_autocomplete_hints`.

Esses arquivos nao sao runtime definitivo. PostgreSQL continua sendo a fonte operacional.

O `macros.json` antigo em `C:\Users\estevao.quality\Desktop\Desktop\[PROJETO]\MACRO\macros.json` esta obsoleto e nao deve ser usado como seed oficial.

## Colaboradores.json

`colaboradores.json` contem apenas nomes. Ele nao cria usuarios canonicos em `users`.

Uso permitido:

- autocomplete de nomes no painel de macros;
- hint temporario para campos manuais.

Quando colaboradores forem populados via `ens.db` ou AD/Entra, a aplicacao deve preferir os registros canonicos em PostgreSQL.

## Modelo de dados

Tabelas criadas pela migration `0005_macros_module`:

- `macro_templates`
- `macro_generations`
- `macro_autocomplete_hints`

Campos principais de `macro_templates`:

- `name`
- `slug`
- `category`
- `description`
- `template_text`
- `required_fields`
- `optional_fields`
- `context_type`
- `source`
- `version`
- `is_active`

## Placeholders

Templates usam placeholders textuais no formato:

```text
{Campo}
```

O renderer apenas substitui texto. Ele nao usa `eval`, nao usa `exec` e nao interpreta template como codigo.

## Seed de macros

Comandos:

```powershell
python scripts/import_quality_macros_to_postgres.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json" --mode AnalyzeOnly
python scripts/import_quality_macros_to_postgres.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json" --mode DryRun
python scripts/import_quality_macros_to_postgres.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json" --mode Apply --confirm-apply APPLY_MACROS_JSON
```

Por padrao, template existente por `slug` e ignorado. Para atualizar template existente:

```powershell
python scripts/import_quality_macros_to_postgres.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json" --mode Apply --update-existing --confirm-apply APPLY_MACROS_JSON
```

## Validacao com arquivo real localizado

Arquivo atual analisado:

```text
C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json
```

DryRun gerado:

```text
uat_evidence\macros_import\macros_json_dryrun_20260603_025326.json
```

Resultado do DryRun:

- total lido: `7`;
- validos: `7`;
- previstos para criacao: `7`;
- atualizados: `0`;
- invalidos: `0`;
- Apply executado posteriormente em UAT com confirmacao explicita `APPLY_MACROS_JSON`.

Relatorio do Apply UAT:

```text
docs/MACROS_APPLY_UAT_REPORT.md
```

Macro prioritaria detectada:

```text
[Ativos] Atualizar inventario
slug: ativos-atualizar-inventario
```

## Seed de hints

Comandos:

```powershell
python scripts/import_colaboradores_json_to_macro_hints.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json" --mode AnalyzeOnly
python scripts/import_colaboradores_json_to_macro_hints.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json" --mode DryRun
python scripts/import_colaboradores_json_to_macro_hints.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json" --mode Apply --confirm-apply APPLY_COLABORADORES_HINTS
```

Arquivo analisado:

```text
C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json
```

DryRun gerado:

```text
uat_evidence\macro_hints_import\colaboradores_hints_dryrun_20260603_025328.json
```

Resultado do DryRun:

- total lido: `111`;
- validos: `111`;
- previstos para criacao: `111`;
- invalidos: `0`;
- Apply executado posteriormente em UAT com confirmacao explicita `APPLY_COLABORADORES_HINTS`.

Resultado do Apply UAT:

- `111` hints criados em `macro_autocomplete_hints`;
- `users` permaneceu inalterado;
- `colaboradores.json` continua sendo hint/autocomplete, nao fonte canonica de usuarios.

## Macro de movimentacao

Template prioritario:

```text
[Ativos] Atualizar inventario
```

Slug esperado:

```text
ativos-atualizar-inventario
```

Campos esperados:

- `Patrimônio`
- `Unidade`
- `Equipamento`
- `Usuário Anterior`
- `Local de`
- `Usuário Atual`
- `Local para`
- `Status`

O endpoint `GET /api/v1/movements/{movement_id}/suggested-macro` usa dados reais da movimentacao e do ativo para montar sugestao. Campo ausente permanece pendente; o sistema nao inventa dados.

## Frontend

Rota criada:

```text
/macros
```

Funcionalidades iniciais:

- listar templates;
- filtrar por categoria;
- buscar macro;
- preencher placeholders obrigatorios;
- renderizar preview;
- copiar texto renderizado.

Apos movimentacao de ativo, o modal tenta buscar macro sugerida e permite copiar o texto.

## Auditoria

Eventos de criacao/atualizacao de template e uso operacional de macro sao registrados em `audit_logs` com acoes existentes (`CREATE`/`UPDATE`) e evento granular em `after.event`.

Eventos operacionais confirmados:

- `macro_generated`
- `macro_copied`
- `asset_movement_macro_generated`

Geracoes visuais ficam persistidas em `macro_generations`. Copias marcam `copied=true` e `copied_at`. Macros geradas por movimentacao usam `context_type=asset_movement` e `context_id=<movement_id>`.

## Segurança

- Templates sao tratados como texto.
- Nao ha execucao de codigo.
- Nao ha criacao de usuarios a partir de `colaboradores.json`.
- Apply dos seeds exige confirmacao explicita.
- PostgreSQL e a fonte operacional.
