# Quality Macros Project Inventory

## Resumo executivo

Fonte oficial atual inspecionada:

```text
C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project
```

Conclusao:

- A fonte atual das macros e `quality_macros_project\assets\macros.json`.
- A fonte atual de hints/autocomplete e `quality_macros_project\assets\colaboradores.json`.
- O motor atual carrega dados via `quality_macros/core/storage.py`.
- O renderer atual esta em `quality_macros/core/macros.py`.
- O arquivo antigo `C:\Users\estevao.quality\Desktop\Desktop\[PROJETO]\MACRO\macros.json` esta obsoleto e nao deve ser usado como seed oficial.
- Nenhum Apply foi executado.

## Estrutura resumida

```text
quality_macros_project/
  assets/
    macros.json
    colaboradores.json
  quality_macros/
    __init__.py
    core/
      macros.py
      paths.py
      storage.py
      logging_conf.py
    ui_flet/
      app_flet.py
  template/
    contact.html
    index.html
    topics-detail.html
    topics-listing.html
  flet.json
  requirements.txt
  run_web.py
  .venv/
```

## Arquivos Python encontrados

| Caminho | Classificacao | Observacao |
| --- | --- | --- |
| `quality_macros/__init__.py` | MACRO_ENGINE_KEEP | Exposicao de funcoes publicas do projeto legado atual. |
| `quality_macros/core/macros.py` | MACRO_ENGINE_KEEP | Renderer textual e utilitarios de placeholder/autocomplete. |
| `quality_macros/core/storage.py` | MACRO_ENGINE_KEEP | Carregamento de macros/hints, migracao de formato legado e persistencia local. |
| `quality_macros/core/paths.py` | MACRO_ENGINE_KEEP | Define `macros.json` e `colaboradores.json`; prioriza `assets/` quando solicitado. |
| `quality_macros/core/logging_conf.py` | ARCHIVE_REFERENCE | Logging do app antigo. |
| `quality_macros/ui_flet/app_flet.py` | LEGACY_ONLY | UI Flet antiga; nao deve ser copiada para a SPA atual. |
| `run_web.py` | LEGACY_ONLY | Launcher do projeto antigo. |
| `.venv/` | DO_NOT_COPY | Ambiente virtual local. |

## Arquivos JSON/YAML/TOML/CSV encontrados

| Caminho | Classificacao | Observacao |
| --- | --- | --- |
| `assets/macros.json` | MACRO_TEMPLATE_SOURCE | Fonte canonica atual para seed de macros. |
| `assets/colaboradores.json` | AUTOCOMPLETE_SOURCE | Fonte de hints; nao cria usuarios canonicos. |
| `flet.json` | LEGACY_ONLY | Configuracao Flet. |

Nenhum YAML/TOML/CSV de macros foi identificado como fonte atual.

## Motor de renderizacao encontrado

Arquivo:

```text
quality_macros/core/macros.py
```

Comportamento:

- placeholders no formato `{Campo}`;
- substituicao textual simples;
- valores ausentes preservam o placeholder original;
- validacao de campos obrigatorios via `campos_obrigatorios_ok`;
- campos de autocomplete detectados por nome contendo colaborador/usuario.

Decisao para ENS ITAM Platform:

- reaproveitar o comportamento conceitual;
- manter renderer proprio em `backend/app/domains/macros/renderer.py`;
- nao copiar o projeto inteiro;
- nao usar `eval`/`exec`;
- nao usar JSON local como runtime definitivo.

## Lista de macros atuais

Fonte:

```text
quality_macros_project\assets\macros.json
```

| Macro | Categoria | Campos |
| --- | --- | --- |
| `[Suporte] Contato inicial` | Suporte | `Nome` |
| `[Suporte] Resolvido` | Suporte | `Nome`, `Chamado`, `Assunto`, `Solução`, `Kcs` |
| `[Suporte] Continuar atendimento` | Suporte | `Nome` |
| `[Suporte] Agendamento de Prova 0800` | Suporte | `Nome`, `Chamado`, `Data`, `Hora` |
| `[Suporte] Tentativa de contato` | Suporte | `Nome`, `Chamado` |
| `[Ativos] Atualizar inventário` | Ativos | `Patrimônio`, `Unidade`, `Equipamento`, `Usuário Anterior`, `Local de`, `Usuário Atual`, `Local para`, `Status` |
| `[Infraestrutura] Encaminhamento` | Infraestrutura | `Nome` |

## Comparacao com macros antigas

Fonte antiga obsoleta:

```text
C:\Users\estevao.quality\Desktop\Desktop\[PROJETO]\MACRO\macros.json
```

| Macro | Existe no antigo? | Existe no atual? | Foi removida/alterada? | Novos campos | Campos removidos | Categoria | Acao recomendada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Iniciar chamado` -> `[Suporte] Contato inicial` | Sim | Sim, renomeada | Alterada | `Nome` | `Nome do colaborador` | Suporte | Usar atual. |
| `Resolver chamado` -> `[Suporte] Resolvido` | Sim | Sim, renomeada | Alterada | `Nome`, `Chamado`, `Assunto`, `Solução`, `Kcs` | `Nome do colaborador`, `Problema`, `Ação realizada`, `KCS` | Suporte | Usar atual. |
| `Agendar chamado` -> `[Suporte] Agendamento de Prova 0800` | Sim | Sim, renomeada | Alterada | `Nome`, `Chamado`, `Data`, `Hora` | `Nome do colaborador` | Suporte | Usar atual. |
| `Tentativa de contato` -> `[Suporte] Tentativa de contato` | Sim | Sim | Alterada | `Nome`, `Chamado` | `Nome do colaborador` | Suporte | Usar atual. |
| `Retornar atendimento` -> `[Suporte] Continuar atendimento` | Sim | Sim, renomeada | Alterada | `Nome` | `Nome do colaborador` | Suporte | Usar atual. |
| `Atualização de inventário` -> `[Ativos] Atualizar inventário` | Sim | Sim, renomeada | Alterada no texto e titulo | Sem novos campos | Nenhum campo removido | Ativos | Usar atual; e a macro oficial de movimentacao. |
| `[Infraestrutura] Encaminhamento` | Nao | Sim | Nova | `Nome` | - | Infraestrutura | Importar da fonte atual. |

## Macro de ativos/movimentacao

Macro oficial atual:

```text
[Ativos] Atualizar inventário
```

Slug esperado no ENS ITAM:

```text
ativos-atualizar-inventario
```

Essa e a macro que deve ser usada por `GET /api/v1/movements/{movement_id}/suggested-macro`.

## DryRun da fonte atual

Comando executado:

```powershell
python scripts/import_quality_macros_to_postgres.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json" --mode DryRun
```

Relatorio:

```text
uat_evidence\macros_import\macros_json_dryrun_20260603_025326.json
```

Resultado:

- total lido: `7`;
- validos: `7`;
- previstos para criacao: `7`;
- invalidos: `0`;
- Apply nao executado.

## DryRun de autocomplete/hints

Fonte:

```text
quality_macros_project\assets\colaboradores.json
```

Relatorio:

```text
uat_evidence\macro_hints_import\colaboradores_hints_dryrun_20260603_025328.json
```

Resultado:

- total lido: `111`;
- validos: `111`;
- previstos para criacao: `111`;
- invalidos: `0`;
- Apply nao executado.

## Itens reaproveitaveis

| Item | Classificacao | Decisao |
| --- | --- | --- |
| `assets/macros.json` | MACRO_TEMPLATE_SOURCE | Usar como fonte oficial de seed. |
| `assets/colaboradores.json` | AUTOCOMPLETE_SOURCE | Usar somente para hints. |
| `quality_macros/core/macros.py` | MACRO_ENGINE_KEEP | Reaproveitar comportamento, nao copiar runtime. |
| `quality_macros/core/storage.py` | MACRO_ENGINE_KEEP | Reaproveitar regra de fonte, nao copiar persistencia local. |

## Itens que nao devem ser reaproveitados

| Item | Classificacao | Motivo |
| --- | --- | --- |
| `.venv/` | DO_NOT_COPY | Ambiente local. |
| `ui_flet/` | LEGACY_ONLY | UI antiga, nao e frontend oficial. |
| `template/*.html` | ARCHIVE_REFERENCE | Material visual/landing antigo, nao runtime ENS ITAM. |
| `flet.json` | LEGACY_ONLY | Configuracao do app antigo. |
| `macros.json` antigo em `[PROJETO]\MACRO` | ARCHIVE_REFERENCE | Fonte obsoleta. |

## Riscos

- Existem multiplas copias de `macros.json` no desktop; usar apenas `quality_macros_project\assets\macros.json`.
- Apply de macros ainda nao foi executado em UAT.
- `colaboradores.json` possui apenas nomes e nao deve contaminar `users`.
- Qualquer mudanca futura feita no app antigo em user data local pode divergir de `assets/macros.json`; para ENS ITAM, a fonte aprovada desta fase e `assets/macros.json`.
