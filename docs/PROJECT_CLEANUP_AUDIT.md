# Project Cleanup Audit

Data: 2026-06-01

Esta revisao foi executada em modo conservador. O objetivo foi reduzir ruido operacional sem reescrever a arquitetura, sem remover em massa e sem quebrar o legado de assinaturas.

## Resumo Executivo

- O projeto nao possui repositorio Git inicializado neste diretorio. Foi criado `_cleanup_backup_manifest.md` antes das movimentacoes.
- Foi criada a quarentena `_archive_cleanup_candidates/` com manifesto reversivel em `_archive_cleanup_candidates/MANIFEST.md`.
- Nenhum arquivo foi removido definitivamente.
- O backend enterprise, a SPA React/Vite atual, o legado de assinaturas, migrations, dados SQLite do legado, assets reais e templates foram preservados.
- A limpeza aplicada ficou restrita a logs locais, metadados de download do Windows, um build antigo fora do fluxo atual e uma duplicata historica de requirements.

## Entry Points Reais

- `run.py`: entrypoint local oficial. Ajusta `PYTHONPATH`, valida ou gera o build de `frontend/itam-platform` e sobe `app.main:app`.
- `backend/app/main.py`: aplica middleware, monta `/api/v1`, `/health`, metricas, SPA React/Vite e legado Flask.
- `backend/app/core/frontend.py`: serve `frontend/itam-platform/dist`, incluindo assets em `/_assets`.
- `backend/app/core/legacy.py`: monta o legado Flask em `/assinaturas` e `/admin`.
- `backend/Dockerfile`: build multi-stage do frontend atual e runtime Python.
- `docker-compose.yml`: orquestra `app`, `postgres` e `redis`.

## Rotas Criticas Preservadas

- `GET /`
- `GET /_assets/*`
- `GET /health`
- `GET /api/v1/assets`
- `GET /assinaturas/`
- `GET /admin/`

## Estrutura Atual

```text
backend/
  app/
    api/
    core/
    domains/
    integrations/
    shared/
  alembic/
frontend/
  itam-platform/
    src/
    dist/
src/
  legacy/
assets/
  templates/
  static/
docs/
scripts/
run.py
docker-compose.yml
```

## Classificacao

### CORE_ENTERPRISE

- `backend/app/api`
- `backend/app/core`
- `backend/app/domains`
- `backend/app/integrations`
- `backend/app/shared`
- `backend/alembic`
- `backend/requirements.txt`
- `backend/Dockerfile`

Justificativa: estrutura atual do FastAPI enterprise, dominios ITAM, auth, auditoria, imports, dashboard, migrations e configuracao operacional.

### FRONTEND_CURRENT

- `frontend/itam-platform/src`
- `frontend/itam-platform/public`, se houver assets publicos
- `frontend/itam-platform/package.json`
- `frontend/itam-platform/package-lock.json`
- `frontend/itam-platform/vite.config.ts`
- `frontend/itam-platform/dist`

Justificativa: SPA atual servida pelo FastAPI. O `dist` atual e usado em execucao local quando `ENS_BUILD_FRONTEND=0` e no container final.

### SIGNATURE_RUNTIME_REQUIRED

- `src/legacy`
- `assets/templates`
- `assets/static`
- `data/ens.db`
- `requirements.txt` da raiz

Justificativa: o legado Flask e montado por `backend/app/core/legacy.py` e depende de templates, assets, SQLite historico e dependencias Python proprias como Flask, requests, MSAL e python-docx.

### SIGNATURE_ADMIN_REQUIRED

- Rotas e handlers em `src/legacy/flask_app.py`
- Assets e templates compartilhados em `assets/`
- Banco legado em `data/ens.db`

Justificativa: `/admin/` continua montado no app principal. Nada relacionado ao admin legado foi removido.

### CONFIG_REQUIRED

- `.env.example`
- `config/.env.example`
- `docker-compose.yml`
- `backend/Dockerfile`
- `run.py`
- `scripts/create-local-secrets.ps1`

Justificativa: arquivos de configuracao ou apoio que ainda ajudam a operacao local e Docker.

### DOCUMENTATION_CURRENT

- `README.md`
- `docs/ARCHITECTURE_REVIEW_ITAM.md`
- `docs/IMPORT_PIPELINE_REVIEW.md`
- `docs/UX_OPERATIONAL_REVIEW.md`
- `docs/MONOLITHIC_ARCHITECTURE.md`
- `docs/PROJECT_CLEANUP_AUDIT.md`

### TESTS_CURRENT

- `tests/`

Justificativa: testes existentes foram preservados, inclusive os que validam assinatura legada.

### BUILD_OUTPUT

- `frontend/itam-platform/dist`: mantido, pois e build atual.
- `frontend/dist`: movido para quarentena, pois e build antigo fora do fluxo oficial.

### LEGACY_UNCERTAIN

- `frontend/app`
- `frontend/legacy`
- `assets/legacy`
- `scripts/ops`
- `infra/nginx`
- `requirements-lock.txt`

Justificativa: estes itens parecem historicos ou auxiliares, mas podem conter referencia, documentacao ou material de compatibilidade. Foram preservados nesta etapa.

### LEGACY_UNUSED_CONFIRMED / DELETE_CANDIDATE

- Nenhum codigo de negocio foi classificado como remocao definitiva.
- Metadados `*Zone.Identifier*` e logs locais foram classificados como nao usados pelo runtime, mas ainda assim foram movidos para quarentena por reversibilidade.

## Arquivos Movidos Para Quarentena

Ver `_archive_cleanup_candidates/MANIFEST.md` para lista completa e comandos de restauracao.

Categorias movidas:

- `runtime_logs`: logs locais em `data/*.log`.
- `old_build_outputs`: `frontend/dist`.
- `config_legacy`: `config/requirements.txt`.
- `orphaned_files/zone_identifier`: metadados Windows `*Zone.Identifier*`.

## Arquivos Removidos Definitivamente

Nenhum.

## Requirements

Estado apos limpeza:

- `backend/requirements.txt`: requirements principal do backend enterprise.
- `requirements-legacy.txt`: requirements direto do legado de assinaturas, necessario para Docker e execucao integrada.
- `requirements.txt`: wrapper de compatibilidade que aponta para `requirements-legacy.txt`.
- `requirements-dev.txt`: local reservado para dependencias futuras de desenvolvimento/teste; atualmente sem pacotes.
- `requirements-lock.txt`: mantido como referencia historica/lock informativo.
- `config/requirements.txt`: arquivado em quarentena como duplicata historica.

O `backend/Dockerfile` instala explicitamente:

```text
backend/requirements.txt
requirements-legacy.txt
```

Por isso a raiz continua necessaria.

## Riscos De Remocao

- `frontend/app`, `frontend/legacy` e `assets/legacy` podem parecer antigos, mas ainda representam legado visual/prototipos/documentacao. Permaneceram preservados.
- `scripts/ops` pode estar obsoleto em relacao a `python run.py`, mas ainda documenta operacao Windows/Linux e foi mantido.
- `infra/nginx` nao e necessario no fluxo atual, mas pode ser util em deploy futuro com reverse proxy.
- `src/config/settings.py` ainda possui fallback antigo para `frontend/dist`; como esse modulo faz parte do legado, foi mantido sem refactor para evitar mudanca comportamental ampla.

## Como Restaurar Quarentena

Cada item possui comando de restauracao em `_archive_cleanup_candidates/MANIFEST.md`.

Exemplo:

```powershell
Move-Item -LiteralPath '_archive_cleanup_candidates\old_build_outputs\frontend\dist' -Destination 'frontend/dist'
```

## Validacoes Recomendadas

Executar sempre apos mudancas de limpeza:

```powershell
python -m compileall -q backend/app backend/alembic
python -c "import sys; sys.path.insert(0, 'backend'); from app.main import app; print(app.title)"
pip install -r backend/requirements.txt
pip install -r requirements-legacy.txt
cd frontend/itam-platform
npm install
npm run build
cd ../..
docker compose config --services
```

Se o banco e Redis estiverem disponiveis:

```powershell
python run.py
```

Validar manualmente:

- `http://127.0.0.1:8080/health`
- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/assinaturas/`
- `http://127.0.0.1:8080/admin/`

## Validacoes Executadas Nesta Limpeza

- `python -m compileall -q backend/app backend/alembic`: passou.
- `python -c "import sys; sys.path.insert(0, 'backend'); from app.main import app; print(app.title)"`: passou e confirmou montagem de `/assinaturas` e `/admin`.
- `pip install -r backend/requirements.txt`: passou; dependencias ja estavam satisfeitas no ambiente local.
- `pip install -r requirements-legacy.txt`: passou.
- `pip install -r requirements.txt`: passou e confirmou o wrapper de compatibilidade para o legado.
- `npm install`: passou em `frontend/itam-platform`.
- `npm run build`: passou em `frontend/itam-platform`.
- `docker compose config --services`: passou e retornou `postgres`, `redis`, `app`.
- Checagem temporaria de rotas em `APP_PORT=18080`, com `APP_STARTUP_CHECKS=false` e `APP_AUTO_MIGRATE=false` para nao depender de banco local:
  - `GET /health`: 200
  - `GET /`: 200
  - `GET /assinaturas/`: 200
  - `GET /admin/`: 302, comportamento esperado de redirecionamento/login do admin legado
  - `GET /api/v1/assets`: 401, comportamento esperado sem JWT

O processo temporario usado para checagem de rotas foi encerrado ao final.

## Decisoes Tecnicas

- Preservar o legado util de assinaturas acima de qualquer economia de arquivos.
- Usar quarentena para itens provaveis, em vez de exclusao.
- Separar `requirements-legacy.txt` do backend sem remover o wrapper `requirements.txt`, porque backend e legado tem responsabilidades diferentes e scripts antigos ainda podem chamar o nome historico.
- Nao mover `frontend/app` nesta etapa, pois documentacao existente declara que o legado em `frontend/app` permanece preservado.
- Nao alterar migrations, banco legado, assets reais ou templates.

## Divida Tecnica Restante

- Atualizar gradualmente `src/config/settings.py` para refletir apenas o frontend atual quando o legado antigo de frontend for formalmente aposentado.
- Definir se `frontend/app`, `frontend/legacy` e `assets/legacy` sao artefatos historicos ou material de suporte ainda necessario.
- Decidir se `scripts/ops` deve virar documentacao arquivada ou fluxo suportado.
- Revisar periodicamente `requirements-lock.txt` como snapshot informativo, sem transforma-lo no requirements principal.

## Proxima Etapa Recomendada

Manter a quarentena por pelo menos um ciclo de validacao operacional. Depois, se nenhuma rota ou processo depender dos itens arquivados, promover apenas os metadados `Zone.Identifier` e logs antigos para exclusao definitiva. O build antigo `frontend/dist` deve permanecer em quarentena ate a equipe confirmar que nenhum script legado usa `src/config/settings.resolve_frontend_dist()`.
