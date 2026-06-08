# Runbook de Backup e Restore

## Objetivo

Validar reversibilidade do ambiente UAT com PostgreSQL em Docker, sem usar produção.

## Backup

```powershell
.\scripts\ops\backup-db.ps1 -ProjectName itam_uat
```

Resultado esperado:

- `backups/itam_backup_YYYYMMDD_HHMMSS.dump`
- `backups/itam_backup_YYYYMMDD_HHMMSS.manifest.json`
- Manifesto com SHA256, tamanho e status `created`.

## Restore

O restore substitui o banco do project informado. Antes de restaurar, o script gera backup de segurança em `backups/pre_restore`.

```powershell
.\scripts\ops\restore-db.ps1 -ProjectName itam_uat -BackupFile .\backups\itam_backup_YYYYMMDD_HHMMSS.dump
```

Para automação controlada:

```powershell
.\scripts\ops\restore-db.ps1 -ProjectName itam_uat -BackupFile .\backups\itam_backup_YYYYMMDD_HHMMSS.dump -Force
```

## Procedimento de Validação

1. Subir UAT: `.\scripts\ops\start-uat.ps1`.
2. Criar massa pequena: `.\scripts\ops\seed-uat-data.ps1`.
3. Rodar backup.
4. Registrar caminho e SHA256 do manifesto.
5. Alterar o banco criando ou movimentando um ativo UAT.
6. Rodar restore com o backup salvo.
7. Validar smoke:
   - `/health` retorna 200.
   - `/` retorna 200.
   - `/assinaturas/` retorna 200.
   - `/admin/` retorna 200 ou 302.
   - `/api/v1/assets` sem token retorna 401.
8. Fazer login e listar ativos.
9. Conferir histórico e auditoria dos dados presentes no backup.

## Regras de Segurança

- Nunca usar restore em produção nesta fase.
- Nunca remover volumes sem confirmação explícita.
- Nunca imprimir senha em logs.
- Conferir `ProjectName` antes de rodar restore.
- Manter pelo menos um backup de segurança pré-restore.

