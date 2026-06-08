# Inventario Seguro do ens.db Legado

Data: 2026-06-02

Classificacao: `LEGACY_SQLITE_SEED_SOURCE`

## Arquivo analisado

Origem:

`C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\data\ens.db`

Tamanho: `69632` bytes

Modo de leitura: SQLite read-only.

O banco nao foi copiado para o projeto novo, nao foi versionado e nao foi
adicionado como dependencia runtime do FastAPI.

## Resultado geral

Tabela principal identificada:

- `colaboradores`

Tabelas internas:

- `sqlite_sequence`

Total de registros em `colaboradores`: `123`

## Schema encontrado

Tabela `colaboradores`:

| Coluna | Tipo | Observacao |
|---|---|---|
| `id` | INTEGER | Chave primaria autoincremental. |
| `name` | TEXT | Nome base do colaborador. |
| `department` | TEXT | Departamento. |
| `role` | TEXT | Cargo/função. |
| `phone` | TEXT | Telefone de assinatura. |
| `email` | TEXT | E-mail unico no SQLite. |
| `status` | TEXT | `on`/`off`, default `on`. |
| `updated_at` | TEXT | Atualizacao legada. |
| `eh_admin` | TEXT | Controle de admin legado, nao migrar como RBAC novo. |
| `password_hash` | TEXT | Sensivel; nao migrar para auth novo. |
| `must_change` | TEXT | Controle de senha legado; nao migrar. |
| `matricula` | TEXT | Login/matricula candidata. |
| `posicao_organograma` | TEXT | Metadado/cargo alternativo. |
| `first_name` | TEXT | Nome. |
| `last_name` | TEXT | Sobrenome. |
| `nome_exibicao` | TEXT | Nome preferencial para assinatura. |
| `diretoria` | TEXT | Diretoria/metadado organizacional. |
| `campo_assinatura` | TEXT | Campo de cargo/assinatura. |
| `manager` | TEXT | Gestor. |
| `telefone_ad` | TEXT | Telefone vindo de AD. |
| `local_descricao` | TEXT | Localidade textual. |
| `endereco` | TEXT | Endereco usado no legado. |
| `uf` | TEXT | Unidade/UF. |

Indices:

- `idx_colaboradores_matricula` em `matricula`.
- `sqlite_autoindex_colaboradores_1`, associado ao `email TEXT UNIQUE`.

## Qualidade dos dados

Resumo:

- Total lido: `123`
- Sem e-mail: `0`
- Sem nome: `0`
- `nome_exibicao` vazio: `5`
- `matricula` vazia: `1`
- `phone` vazio: `0`
- `telefone_ad` vazio: `1`
- `department` vazio: `0`
- `role` vazio: `0`
- Duplicidades por e-mail: `0`
- Duplicidades por matricula/login: `2`

Distribuicao de status:

- `on`: `111`
- `off`: `12`

Amostras mascaradas:

- `ad***@ens.edu.br`
- `al***@ens.edu.br`

Nao foram registrados no documento e-mails completos, telefones completos ou
massa completa de dados pessoais.

## Campos candidatos por uso

| Uso canonico | Campos candidatos no SQLite |
|---|---|
| Nome | `nome_exibicao`, `name`, `first_name + last_name` |
| E-mail | `email` |
| Cargo | `campo_assinatura`, `role`, `posicao_organograma` |
| Departamento | `department`, `diretoria` |
| Unidade/localidade | `uf`, `local_descricao` |
| Telefone | `telefone_ad`, `phone` |
| Login/matricula | `matricula` |
| Gestor | `manager` |
| Status | `status` |
| Assinatura | `campo_assinatura`, `nome_exibicao`, `phone`, `telefone_ad`, `endereco`, `uf` |
| Metadados | `id`, `updated_at`, `diretoria`, `local_descricao`, `endereco` |

## Campos sensiveis detectados

- `password_hash`
- `eh_admin`
- `must_change`

Decisao:

- `password_hash` nao deve ser migrado.
- `eh_admin` nao deve virar RBAC novo automaticamente.
- `must_change` nao deve ser migrado para auth novo.

## Registros que nao devem ser migrados automaticamente

- Registros sem e-mail valido.
- Registros sem nome.
- Registros com duplicidade operacional por e-mail.
- Registros com conflito com colaborador PostgreSQL existente que tenha dados
  manuais mais recentes.

Na leitura atual, nao foram encontrados registros sem e-mail ou sem nome, mas a
regra permanece implementada no script.

## Riscos

- O banco contem dados pessoais e deve permanecer fora do repositorio.
- `matricula` possui duplicidades e nao deve ser identidade primaria.
- O modelo PostgreSQL atual nao possui colunas `source`, `source_metadata`,
- O modelo PostgreSQL agora possui `source` e `source_metadata`. Ele ainda nao
  possui `login`, `mobile` ou `user_principal_name`; esses campos ficam em
  `source_metadata` ate uma migration conservadora futura.
- O SQLite nao deve ser usado em runtime pelo fluxo novo de assinaturas.
