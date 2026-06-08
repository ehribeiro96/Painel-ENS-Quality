# Revisao Pre-Apply - Legacy ENS DB

## Resumo executivo

- Relatorio DryRun analisado: `C:\Users\estevao.quality\Desktop\Assinatura + Ativos\uat_evidence\legacy_ens_db_import\legacy_ens_db_dryrun_20260603_023712.json`
- Data/hora da revisao: 2026-06-02 23:38:09 -03:00
- Decisao preliminar: **APPROVED_WITH_WARNINGS**
- Apply executado nesta etapa: **nao**
- Confirmacao `APPLY_LEGACY_ENS_DB` usada nesta etapa: **nao**

## Resumo do DryRun

| Metrica | Valor |
| --- | ---: |
| total lido | 123 |
| candidatos validos | 123 |
| previstos para criacao | 122 |
| previstos para atualizacao aplicavel | 0 |
| updates sensiveis ignorados | 1 |
| invalidos | 0 |
| sem e-mail | 0 |
| sem nome | 0 |
| duplicados por e-mail | 0 |
| duplicados por matricula/login | 2 |
| falhas | 0 |

## Contas sensiveis ignoradas pela politica

| E-mail | Nome atual | Nome legado | Campos que seriam atualizados | Motivo | Decisao |
| --- | --- | --- | --- | --- | --- |
| es***@ens.edu.br | Es*** Ri*** | Es*** He*** | business_unit, department, job_title, manager_name, phone, source, source_metadata | SKIPPED_SENSITIVE_ACCOUNT_UPDATE | skipped |

Essas contas nao serao atualizadas automaticamente no Apply enquanto a politica estiver ativa.

## Usuario previsto para atualizacao

Nenhum usuario existente foi identificado para atualizacao, ou os detalhes nao puderam ser enriquecidos.

## Duplicidades por matricula/login

| Matricula/Login | Ocorrencias | E-mails | Decisao recomendada |
| --- | ---: | --- | --- |
| *** | 2 | ro***@ens.edu.br, lu***@ens.edu.br | Documentar como hint/metadado; e-mail permanece identidade primaria. |
| at*** | 6 | ma***@ens.edu.br, cr***@ens.edu.br, da***@ens.edu.br, gi***@ens.edu.br, je***@ens.edu.br, ra***@ens.edu.br | Documentar como hint/metadado; e-mail permanece identidade primaria. |

Regra aplicada: e-mail e a identidade primaria; matricula/login permanece apenas como hint/metadado.

## Seguranca

- Apply nao foi executado.
- A confirmacao `APPLY_LEGACY_ENS_DB` nao foi usada.
- `password_hash` nao sera migrado.
- `eh_admin` nao sera migrado.
- `must_change` nao sera migrado.
- `source = legacy_ens_db` sera aplicado apenas no Apply futuro.
- `source_metadata` sera preenchido apenas no Apply futuro.
- Campos vazios nao sobrescrevem campos existentes pela politica do importador.
- Status existente no PostgreSQL sera preservado pela politica do importador.
- Campos sensiveis descartados no DryRun: `password_hash, eh_admin, must_change`.

## Achados e riscos

- Ressalva: ha conta sensivel ignorada pela politica e/ou duplicidades por matricula/login, mas sem risco tecnico bloqueante detectado.

## Decisao pre-Apply

**APPROVED_WITH_WARNINGS**

Apply pode ser considerado somente apos revisao humana, novo backup UAT e autorizacao explicita. A conta sensivel marcada como skipped nao sera atualizada automaticamente.

## Proximo passo recomendado

1. Fazer novo backup UAT:

```powershell
.\scripts\ops\backup-db.ps1 -ProjectName itam_uat
```

2. Executar Apply somente com autorizacao explicita:

```powershell
python scripts/import_legacy_ens_db_to_postgres.py `
  --sqlite-path "C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\data\ens.db" `
  --mode Apply `
  --skip-sensitive-existing-users `
  --sensitive-email "<EMAIL_SENSIVEL_VALIDADO_LOCALMENTE>" `
  --confirm-apply APPLY_LEGACY_ENS_DB
```

