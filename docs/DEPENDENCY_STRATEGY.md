# Dependency Strategy

Data: 2026-06-01

Esta estrategia organiza dependencias Python sem remover codigo, sem apagar legado e sem alterar a arquitetura funcional.

## Contextos Python Reais

### Backend Enterprise Atual

Escopo:

- `backend/app`
- `backend/alembic`
- `run.py`

Responsabilidades:

- FastAPI
- SQLAlchemy async
- Alembic
- PostgreSQL/asyncpg
- Redis
- JWT/Auth
- Auditoria
- Importacao Lansweeper
- SPA Vite servida pelo FastAPI

Arquivo oficial:

```text
backend/requirements.txt
```

### Legado De Assinaturas

Escopo:

- `src/legacy`
- rotas `/assinaturas/`
- rota `/admin/`
- templates/assets em `assets/`
- banco legado `data/ens.db`

Arquivo oficial:

```text
requirements-legacy.txt
```

O arquivo `requirements.txt` da raiz permanece somente como wrapper de compatibilidade:

```text
-r requirements-legacy.txt
```

## Comandos Oficiais

Ambiente integrado local:

```powershell
pip install -r backend/requirements.txt
pip install -r requirements-legacy.txt
```

Compatibilidade historica:

```powershell
pip install -r requirements.txt
```

O comando acima instala o legado porque `requirements.txt` aponta para `requirements-legacy.txt`.

## Mapa De Imports

### Backend Enterprise

Imports externos observados:

- `fastapi`
- `starlette.middleware.wsgi`
- `pydantic`
- `pydantic_settings`
- `sqlalchemy`
- `alembic`
- `asyncpg` via SQLAlchemy URL
- `redis`
- `jose`
- `bcrypt`
- `structlog`
- `pandas`
- `openpyxl` via processamento Excel com pandas
- `uvicorn` via `run.py`
- `email-validator` via `EmailStr`
- `python-multipart` via upload FastAPI

### Legado De Assinaturas

Imports externos observados:

- `flask`
- `jinja2`
- `markupsafe`
- `werkzeug`
- `pandas`
- `openpyxl` via `pd.read_excel(..., engine="openpyxl")` e `to_excel`
- `requests`
- `msal`
- `docx` via `python-docx`
- `dotenv` via `src.config.settings`

### Scripts Operacionais

- `scripts/ops/start_windows.ps1`
- `scripts/ops/start_linux.sh`

Ambos instalam:

- `backend/requirements.txt`
- `requirements-legacy.txt`

### Testes

Os testes Python atuais usam `unittest` da biblioteca padrao e importam o legado. Nao ha dependencia test-only obrigatoria hoje.

## Classificacao

### BACKEND_ENTERPRISE_REQUIRED

- `alembic==1.15.2`
- `asyncpg==0.31.0`
- `bcrypt==4.3.0`
- `email-validator==2.2.0`
- `fastapi==0.115.12`
- `greenlet==3.2.4`
- `openpyxl==3.1.5`
- `pandas==2.2.3`
- `pydantic==2.11.5`
- `pydantic-settings==2.10.1`
- `python-jose[cryptography]==3.4.0`
- `python-multipart==0.0.20`
- `redis==5.2.1`
- `SQLAlchemy==2.0.49`
- `structlog==25.3.0`
- `uvicorn[standard]==0.34.2`

### SIGNATURE_LEGACY_REQUIRED

- `Flask==3.1.2`
- `Jinja2==3.1.6`
- `MarkupSafe==3.0.3`
- `Werkzeug==3.1.8`
- `pandas==2.2.3`
- `openpyxl==3.1.5`
- `python-docx>=0.8.11`
- `msal==1.36.0`
- `requests==2.34.2`
- `python-dotenv==1.2.2`

### DEV_ONLY

- Nenhum pacote obrigatorio atualmente.
- `requirements-dev.txt` foi criado como local reservado para ferramentas futuras.

### TEST_ONLY

- Nenhum pacote externo obrigatorio atualmente.
- Testes existentes usam `unittest`.

### TRANSITIVE_DO_NOT_PIN_DIRECTLY

Exemplos presentes no `requirements-lock.txt`, mas nao nos requirements diretos:

- `anyio`
- `blinker`
- `certifi`
- `cffi`
- `charset-normalizer`
- `click`
- `cryptography`
- `dnspython`
- `ecdsa`
- `h11`
- `httptools`
- `idna`
- `itsdangerous`
- `lxml`
- `Mako`
- `numpy`
- `pyasn1`
- `pycparser`
- `PyJWT`
- `python-dateutil`
- `pytz`
- `PyYAML`
- `rsa`
- `six`
- `starlette`
- `typing_extensions`
- `tzdata`
- `urllib3`
- `watchfiles`
- `websockets`

Observacao: alguns transitivos podem aparecer no ambiente e no lock informativo, mas nao devem virar dependencia direta sem import real ou requisito operacional explicito.

### UNUSED_CANDIDATE

- `aiofiles`: estava no requirements legado historico, mas nao ha import real encontrado em `backend/app`, `src/legacy`, `run.py`, `scripts` ou `tests`. Foi removido do requirements legado direto, mas permanece recuperavel pelo historico/quarentena e pelo lock se necessario.

### UNKNOWN_KEEP_FOR_NOW

- `requirements-lock.txt`: mantido como snapshot informativo.
- Dependencias opcionais do legado relacionadas a Microsoft Graph/MSAL e exportacao Word foram preservadas porque o codigo possui fluxos que as usam ou verificam sua disponibilidade.

## Decisoes

- Separar legado em `requirements-legacy.txt` para reduzir confusao operacional.
- Manter `requirements.txt` como wrapper para nao quebrar automacoes antigas.
- Atualizar Docker e scripts operacionais para usarem `requirements-legacy.txt` diretamente.
- Nao usar `pip freeze` como requirements principal.
- Nao remover dependencia quando existe fluxo legado ou uso opcional em runtime.

## Requirements Resultantes

```text
backend/requirements.txt       # backend enterprise atual
requirements-legacy.txt        # legado Flask de assinaturas
requirements.txt               # wrapper historico para requirements-legacy.txt
requirements-dev.txt           # reservado para ferramentas de dev/test
requirements-lock.txt          # lock informativo/snapshot
```

## Validacoes

Executar apos alteracoes:

```powershell
pip install -r backend/requirements.txt
pip install -r requirements-legacy.txt
python -m compileall -q backend/app backend/alembic
python -c "import sys; sys.path.insert(0, 'backend'); from app.main import app; print(app.title)"
cd frontend/itam-platform
npm run build
cd ../..
docker compose config --services
```

Rotas esperadas com servidor temporario sem dependencia de banco local:

- `GET /health`: 200
- `GET /`: 200
- `GET /assinaturas/`: 200
- `GET /admin/`: 302 ou pagina admin conforme sessao
- `GET /api/v1/assets`: 401 sem JWT ou 200 com JWT valido

## Validacoes Executadas Nesta Etapa

- `pip install -r backend/requirements.txt`: passou.
- `pip install -r requirements-legacy.txt`: passou.
- `pip install -r requirements.txt`: passou e confirmou o wrapper de compatibilidade.
- `python -m compileall -q backend/app backend/alembic`: passou.
- Import do app FastAPI: passou e confirmou montagem de `/assinaturas` e `/admin`.
- `npm run build` em `frontend/itam-platform`: passou.
- `docker compose config --services`: passou e retornou `postgres`, `redis`, `app`.
- Startup temporario com `python run.py`, `APP_PORT=18081`, `APP_STARTUP_CHECKS=false`, `APP_AUTO_MIGRATE=false`, `ENS_BUILD_FRONTEND=0`: passou.
- Rotas verificadas no startup temporario:
  - `GET /health`: 200
  - `GET /`: 200
  - `GET /assinaturas/`: 200
  - `GET /admin/`: 302
  - `GET /api/v1/assets`: 401 sem JWT

O processo temporario foi encerrado e a porta `18081` ficou livre ao final.

## Riscos Restantes

- `requirements-lock.txt` contem versoes de ambiente que podem divergir dos requirements diretos. Ele deve ser tratado como snapshot, nao como fonte de verdade.
- O legado tem imports opcionais (`msal`, `python-docx`) que degradam comportamento quando ausentes. Eles permanecem no requirements legado porque existem fluxos reais que dependem deles.
- `pandas` e `openpyxl` sao usados tanto no backend enterprise quanto no legado. As versoes foram alinhadas para evitar upgrade acidental entre os dois contextos.
