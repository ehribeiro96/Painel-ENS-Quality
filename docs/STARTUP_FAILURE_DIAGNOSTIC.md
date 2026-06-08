# Diagnóstico de Falha de Startup FastAPI/Uvicorn

Data: 2026-06-02  
Project Compose: `itam_uat`  
Sintoma: container `app` saía com `ExitCode=3` após logs do Alembic, sem traceback claro.

## 1. Sintoma Inicial

Ao executar:

```powershell
.\scripts\ops\start-uat.ps1
```

o build passava, PostgreSQL e Redis ficavam healthy, mas o app não ficava pronto:

```text
Application did not become ready at http://127.0.0.1:8080
```

Estado observado:

- `itam_uat-postgres-1`: healthy.
- `itam_uat-redis-1`: healthy.
- `itam_uat-app-1`: `Exited (3)`.

Logs antigos paravam depois de:

```text
Waiting for application startup.
Context impl PostgresqlImpl.
Will assume transactional DDL.
```

## 2. Evidências

Comandos executados:

```powershell
docker compose -p itam_uat ps -a
docker compose -p itam_uat logs app --no-color --tail=500
docker inspect itam_uat-app-1 --format "ExitCode={{.State.ExitCode}} Status={{.State.Status}} Error={{.State.Error}} FinishedAt={{.State.FinishedAt}}"
docker compose -p itam_uat run --rm app sh -lc "cd /app/backend && alembic current && alembic heads && alembic upgrade head"
```

Resultados relevantes:

- `ExitCode=3`.
- Alembic em `0003_startup_auth_obs (head)`.
- `alembic upgrade head` sem erro visível.
- Import de `app.main` passava.
- Falha acontecia dentro do lifespan/startup.

Ao chamar `enterprise_startup()` diretamente:

```text
RuntimeError: ADMIN_PASSWORD must have at least 10 characters
```

## 3. Hipóteses Descartadas

- DNS do Postgres.
- Postgres offline.
- Redis offline.
- Migration pendente.
- Build Docker.
- Requirements.
- Import do FastAPI app.
- Frontend dist ausente.
- Legado `/assinaturas/` e `/admin/` desmontado.

## 4. Causa Raiz

O valor de `ADMIN_PASSWORD` presente no ambiente do container tinha menos de 10 caracteres.

A política de senha do bootstrap admin estava correta, mas a exceção era lançada durante o lifespan do FastAPI sem log estruturado. O Uvicorn encerrava com `ExitCode=3`, deixando o operador sem a etapa exata e sem traceback.

Etapa que falhava:

```text
bootstrap_admin
```

Mensagem:

```text
ADMIN_PASSWORD must have at least 10 characters
```

## 5. Correção Aplicada

Arquivos alterados:

- `backend/app/core/startup.py`
- `scripts/ops/start-uat.ps1`
- `tests/test_startup_diagnostics.py`
- `docs/STARTUP_FAILURE_DIAGNOSTIC.md`
- `docs/KNOWN_ISSUES.md`

Melhorias em `startup.py`:

- Logs estruturados por etapa:
  - `startup_begin`
  - `settings_validation_begin`
  - `settings_validation_ok`
  - `database_wait_begin`
  - `database_wait_ok`
  - `redis_wait_begin`
  - `redis_wait_ok`
  - `migrations_begin`
  - `migrations_ok`
  - `bootstrap_admin_begin`
  - `bootstrap_admin_ok`
  - `frontend_check_begin`
  - `frontend_check_ok`
  - `legacy_mount_check_begin`
  - `legacy_mount_check_ok`
  - `startup_complete`
- Em falha:
  - `startup_failed`
  - `failed_step`
  - `exception_type`
  - `exception_message`
  - `traceback`
- Snapshot seguro sem segredos:
  - `admin_password_set`
  - `jwt_secret_key_set`
  - `database_url_set`
  - `redis_url_set`

Melhorias em `start-uat.ps1`:

- Valida `ADMIN_PASSWORD` com mínimo de 10 caracteres antes do Compose.
- Se readiness falhar, imprime:
  - `docker compose ps -a`
  - `docker compose logs app --tail=200`
  - `docker inspect` com ExitCode/Status/FinishedAt
- Não imprime senha.

## 6. Validação Executada

Volume limpo:

```powershell
docker compose -p itam_uat down -v --remove-orphans
$env:ADMIN_EMAIL="estevao.quality@ens.edu.br"
$env:ADMIN_PASSWORD="<senha-temporaria-local-com-10-ou-mais-caracteres>"
$env:ADMIN_NAME="Estevão Ribeiro"
.\scripts\ops\start-uat.ps1
```

Resultado:

- Postgres healthy.
- Redis healthy.
- App healthy.
- `/health` 200.
- `/` 200.
- `/assinaturas/` 200.
- `/admin/` 302.
- `/api/v1/assets` sem token 401.
- Alembic no head.

Volume preservado:

- Reexecutado `start-uat.ps1` com senha diferente da usada na criação inicial.
- App subiu.
- Bootstrap permaneceu idempotente.
- Admin existente não foi duplicado.
- Roles/migrations não quebraram startup.

Falha controlada:

```powershell
docker compose -p itam_uat run --rm -e ADMIN_PASSWORD=short app ...
```

Resultado esperado obtido:

```text
startup_failed failed_step=bootstrap_admin exception_type=RuntimeError exception_message='ADMIN_PASSWORD must have at least 10 characters'
```

Validação final:

- `python -m compileall -q backend/app backend/alembic tests`: passou.
- `python -m unittest discover -s tests`: passou, 11 testes OK, 5 skips esperados sem env operacional.
- `npm run build`: passou.
- `docker compose config --services`: passou.
- `docker compose -p itam_uat ps -a`: app/postgres/redis healthy.

## 7. Como Diagnosticar Novamente

Se `start-uat.ps1` falhar:

1. Ler a saída automática do próprio script.
2. Procurar `startup_failed` nos logs:

```powershell
docker compose -p itam_uat logs app --no-color --tail=200
```

3. Conferir a etapa:

```text
failed_step
exception_type
exception_message
traceback
```

4. Conferir estado seguro de env:

```text
admin_password_set
jwt_secret_key_set
database_url_set
redis_url_set
frontend_index_exists
frontend_assets_exists
```

## 8. Riscos Restantes

- O operador ainda precisa fornecer `ADMIN_PASSWORD` localmente.
- Volumes preservados mantêm a senha original do admin; trocar a env depois não altera automaticamente a senha persistida.
- Restore continua sendo operação destrutiva no project informado e deve seguir o runbook.

