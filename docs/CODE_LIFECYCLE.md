# Code Lifecycle

## ACTIVE

- `backend/app`
- `backend/alembic`
- `frontend/itam-platform`
- `run.py`
- `docker-compose.yml`
- `backend/Dockerfile`
- `scripts/ops`

## LEGACY_SUPPORTED

- `src/legacy`
- `assets/templates`
- `assets/static`
- Rotas `/assinaturas/`
- Rota `/admin/`

Esses itens sao preservados para compatibilidade do portal de assinaturas.
Correcoes pequenas de seguranca sao permitidas; refatoracao ampla deve ocorrer
em fase dedicada.

## SIGNATURE_ENGINE_KEEP

- `src/legacy/signature_model_spec.py`
- Funcoes puras de renderizacao identificadas em `src/legacy/flask_app.py`
- Renderer novo em `backend/app/domains/signatures/service.py`

Esses itens representam conhecimento tecnico util do motor de assinatura. O
fluxo novo deve consumir colaboradores do PostgreSQL e nao deve depender de
SQLite, Flask, SMTP ou Graph.

## SIGNATURE_TEMPLATE_KEEP

- `assets/templates/hero_outlook.html`
- `assets/templates/base.html`
- `assets/static/v4/hero-outlook.css`
- `assets/static/v4/hero-outlook.js`
- Modelos `.docx` em `assets/static/`, apenas como referencia ate validacao
  especifica de DOCX.

## SIGNATURE_ASSET_KEEP

- `assets/static/icons/Logo.png`
- `assets/static/icons/linkedin.png`
- `assets/static/icons/instagram.png`
- `assets/static/icons/youtube.png`
- demais icones sociais usados em assinatura.

## SQLITE_DATA_SOURCE_DO_NOT_PORT

- `data/backups/*.db` no legado externo
- qualquer uso de `ENS_DB_PATH` como fonte canonica nova

SQLite fica restrito ao fallback legado enquanto necessario. PostgreSQL e a
fonte canonica da plataforma.

## LEGACY_SQLITE_SEED_SOURCE

- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\data\ens.db`

Pode ser lido apenas por script operacional controlado para inventario,
`DryRun` e importacao confirmada de colaboradores para PostgreSQL. Nao deve ser
copiado, versionado ou chamado pelo runtime FastAPI.

## AD_EXPORT_DATA_SOURCE_DO_NOT_PORT

- Dados antigos extraidos de AD para SQLite.

Esses dados devem ser migrados para colaboradores no PostgreSQL por fluxo
auditavel futuro, nao por dependencia operacional paralela.

## LEGACY_FALLBACK

- `/assinaturas/`
- `/admin/`
- admin Flask legado
- UI publica Flask legada

Mantidos temporariamente para compatibilidade.

## FUTURE_STUB

- `backend/app/integrations/lansweeper`
- `backend/app/integrations/azure`
- `backend/app/integrations/microsoft_graph`
- `backend/app/core/permissions/rbac.py`

Stubs futuros devem permanecer desacoplados e nao devem simular dados de
producao.

## ARCHIVED

- `frontend/app`
- `frontend/legacy/Base44`

Esses prototipos foram movidos para `_archive_cleanup_candidates/` porque nao
participam do runtime ativo e possuem imports/dependencias quebradas.

## REMOVED

Nenhuma remocao definitiva de codigo legado foi executada nesta rodada. Itens
incertos foram preservados ou arquivados.

## NEEDS_MANUAL_REVIEW

- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\.env`
- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\secrets\`
- SMTP legado
- MSAL/Graph legado
- DOCX legado antes de habilitar endpoint novo

Esses itens nao devem ser copiados para o projeto novo sem decisao explicita.
## Macros operacionais

Classificacao:

- `backend/app/domains/macros/`: `ACTIVE_RUNTIME`
- `backend/app/api/v1/routes/macros.py`: `ACTIVE_RUNTIME`
- `scripts/import_quality_macros_to_postgres.py`: `CONFIG_REQUIRED`
- `scripts/import_macros_json_to_postgres.py`: `CONFIG_REQUIRED_COMPATIBILITY`
- `scripts/import_colaboradores_json_to_macro_hints.py`: `CONFIG_REQUIRED`
- `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json`: `MACRO_TEMPLATE_SOURCE`
- `colaboradores.json`: `HINT_SOURCE_REVIEW`

Regras:

- `quality_macros_project\assets\macros.json` alimenta `macro_templates` no PostgreSQL.
- `quality_macros_project\assets\colaboradores.json` alimenta apenas `macro_autocomplete_hints`.
- `colaboradores.json` nao cria registros canonicos em `users`.
- PostgreSQL segue como fonte operacional.
- O `macros.json` antigo em `[PROJETO]\MACRO` e `ARCHIVE_REFERENCE` e nao deve ser usado como seed oficial.
