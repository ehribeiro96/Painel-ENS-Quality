# Relatório Interno - Release Candidate UAT

Data base: 2026-06-02  
Decisão: GO COM RESSALVAS

## Resumo Executivo

A fase prepara a plataforma ITAM para UAT controlado por usuários reais da TI. O foco é operação segura, reversibilidade via backup/restore, documentação de cenários e preservação do legado `/assinaturas/` e `/admin/`.

## O Que Foi Preparado

- Checklist de release candidate.
- Plano e cenários de UAT.
- Registro de known issues.
- Runbook de backup/restore.
- Checklist de segurança.
- Formulário de feedback.
- Scripts de start/stop UAT, backup, restore e seed controlado.

## Scripts Criados

- `scripts/ops/start-uat.ps1`
- `scripts/ops/stop-uat.ps1`
- `scripts/ops/backup-db.ps1`
- `scripts/ops/restore-db.ps1`
- `scripts/ops/seed-uat-data.ps1`

## Ambiente Validado

Executado nesta fase:

- `python -m compileall -q backend/app backend/alembic tests`: passou.
- `npm run build`: passou.
- `docker compose config --services`: passou, serviços `redis`, `postgres`, `app`.
- `scripts/ops/start-uat.ps1`: passou, smokes iniciais aprovados.
- `scripts/ops/seed-uat-data.ps1`: passou, massa controlada criada.
- `scripts/ops/backup-db.ps1 -ProjectName itam_uat`: passou.
- `scripts/ops/restore-db.ps1 -ProjectName itam_uat -BackupFile ... -Force`: passou.
- `python -m unittest discover -s tests` com `OPERATIONAL_PROJECT_NAME=itam_uat`: 21 testes OK.

## Backup Validado

Status: Validado.  
Evidência: `backups/itam_backup_20260602_080908.dump`, tamanho 41353 bytes.  
Manifesto: `backups/itam_backup_20260602_080908.manifest.json`.  
SHA256: `5A24194AEBCA1F6BAB9286EBFD64C66BF622CB0253AC2CF4FC4729BEE0D7162B`.

## Restore Validado

Status: Validado.  
Evidência: restore em `itam_uat` com backup pré-restore em `backups/pre_restore`.  
Smoke pós-restore:

- `/health` 200.
- `/` 200.
- `/assinaturas/` 200.
- `/admin/` 302.
- `/api/v1/assets` sem token 401.

## UAT Pronto?

Sim, com ressalva de executar UAT visual por usuários reais. Usuários reais podem ser convidados para validação controlada depois de revisar:

- Regressão passando: concluído.
- Frontend buildando: concluído.
- Backup/restore testados: concluído.
- Smoke UAT aprovado: concluído.
- Senha real ausente de arquivos versionados: verificado sem valor real identificado; `.gitignore` criado para proteger `.env`.

## Riscos Restantes

- UAT visual completo ainda depende de usuários reais.
- Restore é operação destrutiva no project informado e exige disciplina operacional.
- Segredos de UAT precisam permanecer fora do repositório.
- Produção ainda não é alvo desta fase.

## Bugs Encontrados e Corrigidos Nesta Fase

- A suíte de migration estava fixa em `itam_validation`; durante a execução contra `itam_uat`, o teste falhou. Correção: `tests/test_migrations_regression.py` agora lê `OPERATIONAL_PROJECT_NAME`, mantendo `itam_validation` como padrão.
- Não havia `.gitignore`; risco de versionar `.env`, backups e caches. Correção: `.gitignore` conservador adicionado.
- `.dockerignore` não excluía `backups/`; risco de enviar dumps locais para o contexto de build. Correção: `backups/` adicionado ao `.dockerignore`.
- `scripts/ops/start_windows.ps1` tinha uma condição PowerShell inválida ao localizar `run.py` e `backend/app/main.py`. Correção: condição ajustada e todos os scripts `.ps1` parseados com sucesso.

## Known Issues

Ver `docs/KNOWN_ISSUES.md`.

## Critérios GO/NO-GO

GO:

- Todos os comandos obrigatórios passam.
- Backup e restore validados.
- Sem blocker em known issues.
- Legado responde como esperado.

NO-GO:

- Falha em login, movimentação, auditoria, importação ou legado.
- Restore não recupera ambiente.
- Senha real encontrada em arquivo versionado.
