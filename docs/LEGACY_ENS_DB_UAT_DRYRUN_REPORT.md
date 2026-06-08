# Relatorio UAT DryRun - ens.db legado para PostgreSQL

Data: 2026-06-02

## 1. Objetivo

Validar em UAT real que o ambiente esta preparado para importar colaboradores
do `ens.db` legado para PostgreSQL com rastreabilidade, sem executar `Apply` e
sem alterar dados por importacao.

## 2. Ambiente usado

- Projeto Docker Compose: `itam_uat`
- URL: `http://127.0.0.1:8080`
- Servicos esperados: `postgres`, `redis`, `app`
- Estado apos subida:
  - `postgres`: healthy
  - `redis`: healthy
  - `app`: healthy

Endpoints validados:

| Endpoint | Resultado |
|---|---:|
| `/health` | 200 |
| `/` | 200 |
| `/assinaturas/` | 200 |
| `/admin/` | 302 |
| `/api/v1/assets` sem token | 401 |

## 3. Migration aplicada

Alembic:

- `current`: `0004_user_source_metadata (head)`
- `heads`: `0004_user_source_metadata (head)`

Migration validada:

- `backend/alembic/versions/0004_add_user_source_metadata.py`

## 4. Colunas confirmadas em `users`

Consulta via `information_schema`, sem listar usuarios:

| Coluna | Tipo | Nullable |
|---|---|---|
| `source` | `character varying` | YES |
| `source_metadata` | `jsonb` | YES |

## 5. Backup criado

Backup executado antes do DryRun:

- Arquivo: `backups/itam_backup_20260602_194750.dump`
- Manifesto: `backups/itam_backup_20260602_194750.manifest.json`
- Tamanho: `552692` bytes
- SHA256 registrado no manifesto.
- Status: `created`

Nenhum dado do backup foi inspecionado ou impresso.

## 6. Comando DryRun usado

Comando executado sem `Apply` e sem confirmação de Apply:

```powershell
python scripts/import_legacy_ens_db_to_postgres.py `
  --sqlite-path "C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\data\ens.db" `
  --mode DryRun
```

`DATABASE_URL` foi definido apenas no ambiente do processo para apontar ao
PostgreSQL UAT exposto localmente. A connection string completa nao foi
registrada neste documento.

## 7. Contagem de usuarios antes/depois

| Momento | Count |
|---|---:|
| Antes do DryRun | 5 |
| Depois do DryRun | 5 |

Checagem adicional:

- `users where source = 'legacy_ens_db'`: `0`

Conclusao: o DryRun nao criou usuarios, nao alterou a contagem e nao persistiu
marcacao `source=legacy_ens_db`.

## 8. Resultado do DryRun

Relatorio local gerado:

`uat_evidence/legacy_ens_db_import/legacy_ens_db_dryrun_20260602_224801.json`

Resumo:

| Metrica | Valor |
|---|---:|
| Total lido | 123 |
| Candidatos validos | 123 |
| Invalidos | 0 |
| Previstos para criacao | 122 |
| Previstos para atualizacao | 1 |
| Ignorados | 0 |
| Duplicados por e-mail | 0 |
| Duplicados por matricula/login | 2 |
| Sem e-mail | 0 |
| Sem nome | 0 |
| Falhas | 0 |

## 9. Campos previstos para importacao

Campos canônicos:

- `name`
- `email`
- `job_title`
- `department`
- `business_unit`
- `manager_name`
- `phone`
- `status`
- `source`
- `source_metadata`

`source` previsto:

- `legacy_ens_db`

`source_metadata` previsto:

- `source_record_id`
- `legacy_imported_at`
- `matricula`
- `login`
- `status_legacy`
- `import_mode`
- `source_database`
- metadados organizacionais nao sensiveis.

## 10. Campos descartados

Campos sensiveis descartados:

- `password_hash`
- `eh_admin`
- `must_change`

Esses campos nao devem ser migrados para o auth/RBAC novo.

## 11. Segurança e privacidade

- O arquivo `ens.db` foi lido somente como `LEGACY_SQLITE_SEED_SOURCE`.
- O SQLite nao foi copiado para o backend.
- O SQLite nao foi adicionado ao runtime FastAPI.
- O DryRun nao usou `--confirm-apply`.
- Nao houve impressao de nomes/e-mails em massa.
- Relatorios foram gravados em `uat_evidence/`, pasta ignorada pelo Git.

## 12. Validacoes obrigatorias

Executado com sucesso:

- `python -m compileall -q backend/app backend/alembic tests scripts`
- `python -m unittest discover -s tests`
  - `29 tests`, `OK`, `5 skipped`
- `ruff check backend tests scripts/import_legacy_ens_db_to_postgres.py`
- `cd frontend/itam-platform && npm run build`
- `docker compose config --services`

## 13. Decisao

Status: **pronto tecnicamente para etapa de Apply controlado, com ressalvas operacionais**.

Ressalvas:

- `Apply` ainda nao foi executado.
- O relatorio DryRun deve ser revisado por responsavel da TI.
- A atualizacao prevista de 1 usuario existente deve ser aceita antes do Apply.
- Duplicidades por matricula/login devem ser conhecidas, mas nao bloqueiam porque
  e-mail e a identidade primaria.

## 14. Recomendacao para proxima etapa

1. Manter UAT sem remover volumes.
2. Revisar o relatorio JSON do DryRun.
3. Confirmar se `122 created` e `1 updated` sao aceitaveis.
4. Fazer novo backup imediatamente antes do Apply.
5. Executar Apply apenas com autorizacao explicita:

```powershell
python scripts/import_legacy_ens_db_to_postgres.py `
  --sqlite-path "C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\data\ens.db" `
  --mode Apply `
  --confirm-apply APPLY_LEGACY_ENS_DB
```

6. Validar colaboradores, assinaturas e auditoria.
7. Fazer backup pos-importacao.
## Atualizacao de politica - contas sensiveis

Foi executado novo DryRun com `skip_sensitive_existing_users=true`.

Resultado:

- colaboradores previstos para criacao: `122`;
- atualizacoes aplicaveis: `0`;
- conta admin/sensivel ignorada: `1`;
- motivo: `SKIPPED_SENSITIVE_ACCOUNT_UPDATE`;
- usuarios no banco antes/depois: inalterado;
- usuarios com `source = legacy_ens_db`: `0`;
- decisao pre-Apply atual: `APPROVED_WITH_WARNINGS`.

Apply do `ens.db` nao foi executado.

Relatorio DryRun com politica:

```text
uat_evidence\legacy_ens_db_import\legacy_ens_db_dryrun_20260603_023712.json
```

Relatorio de revisao pre-Apply:

```text
docs\LEGACY_ENS_DB_PRE_APPLY_REVIEW.md
```
