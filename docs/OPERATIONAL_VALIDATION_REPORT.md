# Operational Validation Report

Data/hora: 2026-06-01, America/Sao_Paulo

Escopo: validacao operacional ponta a ponta em stack Docker real com PostgreSQL, Redis, migrations, bootstrap admin, autenticacao, RBAC, API, SPA integrada, importacao Lansweeper e legado de assinaturas.

## 1. Ambiente Testado

Diretorio:

```text
c:\Users\estevao.quality\Desktop\Assinatura + Ativos
```

Versoes detectadas:

```text
Docker version 29.4.3, build 055a478
Docker Compose version v5.1.3
Node.js v24.13.0
npm 11.6.2
Python global: nao disponivel pelo alias do Windows
Python do projeto: 3.12.10 em .venv
pip do projeto: 26.1.1
```

Observacao: Docker Desktop estava instalado, mas o daemon nao estava ativo no primeiro precheck. Foi iniciado via `Docker Desktop.exe` e o daemon respondeu antes da validacao Docker.

## 2. Comandos Executados

Precheck:

```powershell
docker --version
docker compose version
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
node --version
npm --version
docker compose config --services
```

Stack isolado com banco limpo:

```powershell
docker compose -p itam_validation down -v --remove-orphans
docker compose -p itam_validation up --build -d
```

Migrations:

```powershell
docker compose -p itam_validation exec -T app sh -lc "cd /app/backend && alembic upgrade head && alembic current && alembic heads"
```

Build/testes:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend\app backend\alembic
.\.venv\Scripts\python.exe -m unittest discover -s tests
cd frontend\itam-platform
npm run build
```

## 3. Docker

Resultado:

```text
services: redis, postgres, app
postgres: healthy
redis: healthy
app: healthy
porta app: 8080
porta postgres: 5432
porta redis: 6379
```

O build Docker compilou o frontend Vite no stage Node e instalou os requirements separados:

- `backend/requirements.txt`
- `requirements-legacy.txt`

## 4. Migrations

Resultado final:

```text
current: 0003_startup_auth_obs (head)
heads:   0003_startup_auth_obs (head)
```

Tabelas existentes:

```text
alembic_version
asset_movements
assets
audit_logs
auth_sessions
import_conflicts
import_jobs
import_staging_assets
import_validation_errors
users
```

## 5. Healthchecks

Endpoints validados:

```text
GET /health                200
GET /health/live           200
GET /health/ready          200
GET /health/dependencies   200
```

Estado reportado:

- PostgreSQL: ok
- Redis: ok
- `frontend_ready`: true
- migration: `up_to_date`
- bootstrap: `created` no primeiro startup
- `startup_complete`: true

## 6. Bootstrap Admin

Resultado:

```text
estevao.quality@ens.edu.br | ADMIN | ACTIVE
```

Idempotencia:

- App reiniciado.
- Admin permaneceu com `count = 1`.
- Migrations permaneceram no head.

Observacao: as roles sao enums no banco e no codigo, nao linhas em tabela dedicada. Foram validadas via criacao/login de usuarios `ADMIN`, `TECHNICIAN`, `MANAGER` e `VIEWER`.

## 7. Auth

Resultados:

```text
POST /api/v1/auth/login       200
GET  /api/v1/auth/me          200
POST /api/v1/auth/refresh     200
POST /api/v1/auth/logout      200
login invalido                401
rota protegida sem token      401
```

Refresh cookie:

```text
Set-Cookie: ens_itam_refresh=...; HttpOnly; Max-Age=604800; Path=/api/v1/auth; SameSite=lax
```

O refresh funcionou usando cookie HttpOnly. O cookie nao foi armazenado em localStorage durante a validacao de API.

## 8. RBAC

Validado:

- `ADMIN` criou usuarios e ativos.
- `VIEWER` tentou criar ativo e recebeu `403`.
- Sem token em `/api/v1/assets` recebeu `401`.

Lacuna observada:

- Validacao granular completa de todas as combinacoes `TECHNICIAN`, `MANAGER` e `VIEWER` por endpoint deve virar suite automatizada dedicada. Nesta etapa foi validado o bloqueio basico de escrita para `VIEWER`.

## 9. CRUD Users

Massa criada:

- `Tecnico QA`
- `Viewer QA`
- `Colaborador Teste`
- `Gestor Teste`

Resultados:

```text
POST /api/v1/users              201
GET  /api/v1/users              200, total 5
GET  /api/v1/users/{id}         200
PUT  /api/v1/users/{id}         200
GET  /api/v1/users/{id}/assets  200
email invalido                  422
```

## 10. CRUD Assets

Massa criada:

- `RJMTEST001`: notebook em uso
- `RJMTEST002`: desktop em estoque
- `RJMTEST003`: monitor em estoque
- `RJMTEST004`: notebook em manutencao
- `RJMTEST005`: notebook defeituoso

Resultados:

```text
POST /api/v1/assets                 201
GET  /api/v1/assets?search=...      total 1
GET  /api/v1/assets?status=STOCK    total 2
GET  /api/v1/assets/{id}            200
PUT  /api/v1/assets/{id}            200
```

Soft delete nao foi exercitado nesta massa para preservar os dados usados no dashboard e auditoria durante a mesma validacao.

## 11. Movimentacao

Fluxo validado no ativo `RJMTEST002`:

1. Estoque para colaborador.
2. Transferencia para gestor.
3. Envio para manutencao.
4. Retorno ao estoque.
5. Marcacao como defeituoso.

Resultados:

```text
POST /api/v1/assets/{id}/move       200
GET  /api/v1/assets/{id}/history    5 registros
movimento invalido IN_USE sem user  422
```

Auditoria gerada para os movimentos.

## 12. Auditoria

Resultado:

```text
GET /api/v1/audit-logs?page=1&page_size=100 200
total: 24
```

Acoes observadas:

```text
CREATE
IMPORT
LOGIN
LOGOUT
MOVE
SIGNATURE_GENERATE
UPDATE
```

Resumo no banco:

```text
LOGIN              User       3
LOGOUT             User       1
CREATE             Asset      7
CREATE             User       4
UPDATE             Asset      1
UPDATE             User       1
MOVE               Asset      5
IMPORT             ImportJob  3
SIGNATURE_GENERATE User       1
```

## 13. Importacao Lansweeper

Arquivos pequenos gerados em `%TEMP%`:

- `valid.csv`: 2 registros validos.
- `duplicate.csv`: serial/patrimonio repetidos.
- `invalid.csv`: campos com prefixos de formula (`=cmd`, `+SUM`).

Resultados:

```text
POST /api/v1/imports/lansweeper valid       201, total_rows 2
POST /api/v1/imports/lansweeper duplicate   201
POST /api/v1/imports/lansweeper invalid     201
GET /api/v1/imports/{id}/staging            total 2
GET /api/v1/imports/{id}/conflicts          1 conflito
GET /api/v1/imports/{id}/validation-errors  3 erros
```

O inventario principal nao foi corrompido pelos invalidos; erros ficaram em staging/validation.

## 14. Dashboard

Resultados:

```text
GET /api/v1/dashboard/summary            total_assets 5
GET /api/v1/dashboard/assets-by-status   4 grupos
GET /api/v1/dashboard/assets-by-type     3 grupos
GET /api/v1/dashboard/recent-movements   5 registros
```

Os totais bateram com a massa minima criada antes das importacoes.

## 15. Assinaturas

API enterprise:

```text
GET  /api/v1/signatures/{user_id}                200, contem nome do usuario
POST /api/v1/signatures/generate/{user_id}       200
GET  /api/v1/signatures/{user_id}/download-html  200
```

Legado:

```text
GET /assinaturas/ 200
GET /admin/       302
```

## 16. Frontend Integrado

Validados:

```text
GET /                  200
GET /dashboard          200
GET /assets/example-id  200
GET /users              200
GET /imports            200
GET /signatures         200
GET /audit              200
GET /audit-logs         200
GET /_assets/*.js       200
```

Todos os deep links retornaram o shell da SPA. Asset Vite carregou com tamanho esperado.

Validacao visual em navegador nao foi automatizada nesta etapa; a validacao feita foi HTTP/API/build.

## 17. Testes Automatizados

Executado:

```text
python -m unittest discover -s tests
```

Resultado:

```text
Ran 9 tests
OK
```

Adicionado:

- `tests/test_operational_contracts.py`

Cobertura nova:

- IDs Alembic cabem no `VARCHAR(32)` padrao.
- `requirements.txt` continua wrapper do legado.
- rotas criticas FastAPI/mounts existem.

## 18. Bugs Encontrados

### Bug 1: migration inicial duplicava ENUM PostgreSQL

Sintoma:

```text
DuplicateObjectError: type "userstatus" already exists
```

Causa:

- A migration `0001` criava os ENUMs manualmente e as colunas tentavam criar os mesmos tipos novamente.

Correcao:

- `backend/alembic/versions/0001_initial_itam.py`: ENUMs definidos com `create_type=False` e criados explicitamente uma unica vez.

### Bug 2: revision id Alembic excedia limite padrao

Sintoma:

```text
value too long for type character varying(32)
```

Causa:

- Revision ID `0003_enterprise_startup_auth_observability` maior que o `alembic_version.version_num` padrao.

Correcao:

- `backend/alembic/versions/0003_enterprise_startup_auth_observability.py`: revision reduzida para `0003_startup_auth_obs`.

### Bug 3: admin default anterior nao conseguia login

Sintoma:

```text
e-mail local/reservado rejeitado por EmailStr
```

Causa:

- Bootstrap criava e-mail com dominio especial/reservado `.local`, mas login valida `EmailStr`.

Correcao:

- `docker-compose.yml` e `.env.example`: default operacional alterado para `estevao.quality@ens.edu.br`, com senha obrigatoria via ambiente local.

### Bug 4: criacao de asset com usuario atual retornava 500

Sintoma:

- `POST /api/v1/assets` funcionava sem `current_user_id`, mas falhava com `current_user_id`.

Causa:

- Relacionamento `current_user` nao estava carregado antes da serializacao da resposta.

Correcao:

- `backend/app/domains/assets/service.py`: refresh do relacionamento `current_user` apos flush quando o asset nasce vinculado.

## 19. Bugs Pendentes / Riscos

- O check completo de RBAC por matriz de permissoes ainda deve virar teste automatizado.
- A validacao frontend foi por HTTP/build; nao houve navegacao browser automatizada com Playwright.
- O Dockerfile instala `build-essential` no runtime final. Funciona, mas aumenta imagem; otimizar depois sem mexer nesta validacao.
- O default anterior de senha local foi removido em etapa posterior de regressao. Use `ADMIN_PASSWORD` apenas via variavel de ambiente local e nunca em arquivos versionados.
- O fluxo de refresh emite cookie HttpOnly corretamente, mas testes automatizados de revogacao/rotacao devem ser ampliados.

## 20. Status Final

Criterios de aceite:

- Docker Compose sobe o sistema: aprovado.
- PostgreSQL funciona: aprovado.
- Redis funciona: aprovado.
- Migrations aplicam corretamente: aprovado apos correcao.
- Bootstrap admin funciona: aprovado apos correcao do e-mail default.
- Login real funciona: aprovado.
- Rota protegida sem token retorna 401: aprovado.
- Usuario autenticado acessa `/me`: aprovado.
- Usuario pode ser criado: aprovado.
- Ativo pode ser criado: aprovado apos correcao de relacionamento.
- Ativo pode ser movimentado: aprovado.
- Historico e gerado: aprovado.
- Auditoria e gerada: aprovado.
- Importacao pequena funciona: aprovado.
- Dashboard mostra dados reais: aprovado.
- Assinatura renderiza: aprovado.
- `/assinaturas/` continua funcionando: aprovado.
- `/admin/` continua funcionando/redirecionando: aprovado.
- SPA funciona com deep links: aprovado.

## 21. Proximos Passos Recomendados

- Criar suite de integracao Docker reutilizavel para auth/users/assets/movements/imports.
- Automatizar browser smoke com Playwright para login, tabela de ativos, movimentacao e importacao.
- Testar matrix RBAC completa por endpoint.
- Testar rollback transacional de movimentacao com falha induzida.
- Adicionar fixture de CSV/XLSX em `tests/fixtures/imports/`.

## 22. Atualizacao De Regressao

Etapa posterior criou a suite operacional minima documentada em:

- `docs/REGRESSION_SAFETY_SUITE.md`
- `docs/OPERATIONAL_TEST_MATRIX.md`

O admin operacional padrao para validacao passou a ser:

```text
ADMIN_EMAIL=estevao.quality@ens.edu.br
ADMIN_PASSWORD=<DEFINIR_LOCALMENTE_NO_ENV>
ADMIN_NAME=Estevão Ribeiro
```

Nenhuma senha real deve aparecer em codigo, docs, testes, scripts ou `.env.example`.
# Atualização - Release Candidate UAT 2026-06-02

Validação complementar para preparar UAT controlado:

- `python -m compileall -q backend/app backend/alembic tests`: passou.
- `python -m unittest discover -s tests` com UAT real: 21 testes OK.
- `npm run build`: passou.
- `docker compose config --services`: `redis`, `postgres`, `app`.
- `scripts/ops/start-uat.ps1`: passou.
- `scripts/ops/backup-db.ps1 -ProjectName itam_uat`: passou.
- `scripts/ops/restore-db.ps1 -ProjectName itam_uat ... -Force`: passou.
- Smoke pós-restore: `/health` 200, `/` 200, `/assinaturas/` 200, `/admin/` 302, `/api/v1/assets` sem token 401.

Correção de regressão feita nesta fase:

- `tests/test_migrations_regression.py` agora aceita `OPERATIONAL_PROJECT_NAME`, mantendo `itam_validation` como padrão e permitindo validar `itam_uat`.
