# Mapeamento ens.db Legado para PostgreSQL

Data: 2026-06-02

Fonte: `LEGACY_SQLITE_SEED_SOURCE`

Destino canonico: tabela `users` no PostgreSQL.

## Decisao

O `ens.db` pode popular colaboradores temporariamente no PostgreSQL ate a
integracao futura com AD/Entra ID. Ele nao vira dependencia runtime e nao e
consultado pelo renderer novo de assinaturas.

## Modelo PostgreSQL atual

Campos existentes em `users`:

- `id`
- `name`
- `email`
- `job_title`
- `department`
- `business_unit`
- `manager_name`
- `phone`
- `password_hash`
- `status`
- `role`
- `created_at`
- `updated_at`
- `created_by`
- `updated_by`

Campos adicionados nesta fase:

- `source`
- `source_metadata`

Migration:

- `backend/alembic/versions/0004_add_user_source_metadata.py`

Campos esperados, mas ainda ausentes:

- `login`
- `user_principal_name`
- `location`
- `mobile`
- `manager` como FK

Decisao nesta fase:

- Nao criar migration destrutiva.
- Nao adicionar campos de AD/Entra ainda.
- Guardar dados de origem em `source_metadata`, descartando campos sensiveis.
- Propor migration conservadora futura para `login`, `mobile` e
  `user_principal_name` se a reconciliacao com AD/Entra exigir.

## Mapeamento aplicado pelo script

| SQLite `colaboradores` | PostgreSQL `users` | Regra |
|---|---|---|
| `nome_exibicao` | `name` | Preferencial. |
| `name` | `name` | Fallback. |
| `first_name + last_name` | `name` | Fallback final. |
| `email` | `email` | Identidade primaria, normalizada lowercase. |
| `campo_assinatura` | `job_title` | Preferencial para assinatura. |
| `role` | `job_title` | Fallback. |
| `posicao_organograma` | `job_title` | Fallback. |
| `department` | `department` | Preferencial. |
| `diretoria` | `department` | Fallback. |
| `uf` | `business_unit` | Preferencial para unidade. |
| `local_descricao` | `business_unit` | Fallback. |
| `manager` | `manager_name` | Texto legado. |
| `telefone_ad` | `phone` | Preferencial. |
| `phone` | `phone` | Fallback. |
| `status=on` | `status=ACTIVE` | Novo colaborador. |
| `status=off` | `status=INACTIVE` | Novo colaborador. |
| `matricula` | relatorio/metadado | Nao ha coluna `login` ainda. |
| `id` | relatorio/metadado | `source_record_id`. |
| `updated_at` | relatorio/metadado | `legacy_updated_at`. |
| `password_hash` | nao migrar | Auth legado nao entra no auth novo. |
| `eh_admin` | nao migrar | RBAC novo nao deve ser inferido automaticamente. |
| `must_change` | nao migrar | Controle legado de senha. |
| origem | `source` | Valor fixo `legacy_ens_db`. |
| metadados seguros | `source_metadata` | `source_record_id`, `matricula`, `login`, `status_legacy`, `source_database`, `legacy_imported_at`. |

## Politica de merge

Identidade:

1. E-mail valido.
2. Login/matricula apenas como identidade secundaria futura.

Criacao:

- Criar apenas colaborador com nome e e-mail validos.
- Criar com `role=VIEWER`.
- Criar com `status` derivado de `on/off`.

Atualizacao:

- Nao sobrescrever campo existente com vazio.
- Nao sobrescrever status manual de colaborador existente.
- Preencher apenas campos permitidos que estejam vazios no PostgreSQL.
- Preservar senha/RBAC do sistema novo.
- Preencher `source=legacy_ens_db`.
- Preencher `source_metadata` somente com dados nao sensiveis.

Ignorar/revisar:

- Sem e-mail.
- Sem nome.
- E-mail invalido.
- Duplicidade por e-mail dentro do SQLite.
- Conflitos operacionais com usuario PostgreSQL existente.

## Auditoria

Em modo `Apply`, o script registra evento `IMPORT` em `audit_logs` com:

- `entity=User`
- `source=legacy_ens_db_seed`
- resumo de contadores
- sem dados pessoais completos
- descartando `password_hash`, `eh_admin` e `must_change`

## Relatorios

Relatorios sao gerados em:

`uat_evidence/legacy_ens_db_import/`

Essa pasta deve permanecer ignorada pelo Git.
## Politica para contas sensiveis

Contas existentes com papel `ADMIN` ou e-mail informado via `--sensitive-email` sao tratadas como sensiveis.

Politica padrao:

```text
skip_sensitive_existing_users = true
```

Comportamento:

- o importador nao atualiza campos cadastrais de conta admin/sensivel;
- nao altera `role`, permissoes, senha, hash, status, `source` ou `source_metadata`;
- marca a linha como `SKIPPED_SENSITIVE_ACCOUNT_UPDATE`;
- permite que os demais colaboradores validos continuem planejados para criacao;
- registra o skip no relatorio DryRun/Apply.

Duplicidade por matricula/login permanece warning, pois e-mail e a identidade primaria.
