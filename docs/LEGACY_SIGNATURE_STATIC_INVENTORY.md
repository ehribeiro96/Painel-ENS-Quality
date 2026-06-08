# Inventario da Pasta Externa de Assinatura

Data: 2026-06-02

Fonte analisada:

`C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\`

## Regra de seguranca aplicada

A pasta externa foi analisada em modo conservador. Os seguintes itens foram
identificados, mas nao tiveram conteudo sensivel lido, copiado ou portado:

- `.env` - `SENSITIVE_REVIEW` / `DO_NOT_COPY`
- `secrets\ens_secret_key` - `SENSITIVE_REVIEW` / `DO_NOT_COPY`
- `secrets\ms_client_secret` - `SENSITIVE_REVIEW` / `DO_NOT_COPY`
- `data\ens.db` - `LEGACY_SQLITE_SEED_SOURCE`
- `data\backups\ens.bkp.db` - `SQLITE_DATA_SOURCE_DO_NOT_PORT`
- `data\backups\ens.legacy.db` - `SQLITE_DATA_SOURCE_DO_NOT_PORT`
- `.venv\` - dependencia local vendorizada, `DO_NOT_COPY`
- `frontend\app\node_modules\` - dependencia local vendorizada, `DO_NOT_COPY`

Nenhum valor de segredo foi impresso ou copiado.

## Arvore resumida

```text
static/
├── .github/
├── .venv/                         DO_NOT_COPY
├── .vscode/
├── assets/
│   ├── legacy/
│   ├── static/
│   │   ├── js/
│   │   ├── v4/
│   │   └── vendor/
│   └── templates/
├── config/
├── data/                          SQLITE_DATA_SOURCE_DO_NOT_PORT
├── docs/
├── frontend/
├── scripts/
├── secrets/                       SENSITIVE_REVIEW
├── src/
│   ├── api/
│   ├── config/
│   └── legacy/
└── tests/
```

## Arquivos Python relevantes

| Caminho | Classificacao | Observacao |
|---|---|---|
| `src/legacy/flask_app.py` | SIGNATURE_ENGINE_KEEP + LEGACY_UI_FALLBACK_ONLY | Contem renderer HTML/DOCX, rotas Flask, SQLite, SMTP e Graph misturados. Portar apenas funcoes puras. |
| `src/legacy/assets_base64.py` | SIGNATURE_ASSET_KEEP | Fallback de assets embutidos. Pode ser referencia, nao exige port integral. |
| `src/legacy/signature_model_spec.py` | SIGNATURE_ENGINE_KEEP | Define cores, tamanhos, marcadores canonicos e especificacao do modelo. |
| `src/legacy/render_public.py` | SIGNATURE_ENGINE_KEEP | Script auxiliar de renderizacao publica. |
| `src/legacy/render_public_icons.py` | SIGNATURE_ASSET_KEEP | Script auxiliar de assets publicos. |
| `src/api/fastapi_app.py` | LEGACY_UI_FALLBACK_ONLY | Monta Flask em FastAPI no legado antigo. Nao portar para o novo runtime. |
| `src/config/settings.py` | SQLITE_DATA_SOURCE_DO_NOT_PORT | Resolve caminhos, inclusive `data/ens.db`. Usar apenas como referencia historica. |

## Templates HTML encontrados

| Caminho | Classificacao | Observacao |
|---|---|---|
| `assets/templates/index.html` | LEGACY_UI_FALLBACK_ONLY | UI publica de assinatura legada. |
| `assets/templates/admin.html` | LEGACY_UI_FALLBACK_ONLY | Admin legado dependente de SQLite. |
| `assets/templates/admin_edit.html` | LEGACY_UI_FALLBACK_ONLY | Edicao legada dependente de SQLite. |
| `assets/templates/base.html` | SIGNATURE_TEMPLATE_KEEP | Referencia visual/base HTML. |
| `assets/templates/hero_outlook.html` | SIGNATURE_TEMPLATE_KEEP | Referencia do guia Outlook. |
| `assets/templates/login.html` | LEGACY_UI_FALLBACK_ONLY | Auth Flask legado. |
| `assets/templates/change_password.html` | LEGACY_UI_FALLBACK_ONLY | Auth Flask legado. |
| `assets/templates/oauth_not_configured.html` | GRAPH_LEGACY_REVIEW | Fallback de Graph/OAuth legado. |

## CSS, JS e assets

| Caminho | Classificacao | Observacao |
|---|---|---|
| `assets/static/js/signature-copy.js` | SIGNATURE_ASSET_KEEP | Logica de copia usada pelo legado. |
| `assets/static/v4/hero-outlook.css` | SIGNATURE_TEMPLATE_KEEP | Estilo do guia Outlook. |
| `assets/static/v4/hero-outlook.js` | SIGNATURE_TEMPLATE_KEEP | Interacao do guia Outlook. |
| `assets/static/vendor/tpl/*` | LEGACY_UI_FALLBACK_ONLY | Bootstrap/vendor do legado. |
| `assets/static/icons/*.png` | SIGNATURE_ASSET_KEEP | Logos e icones sociais usados em assinatura. |
| `assets/static/*.docx` | SIGNATURE_TEMPLATE_KEEP | Modelo Word e guia ilustrado do legado. DOCX novo fica pendente ate avaliacao especifica. |

## Componentes que parecem gerar assinatura

| Funcao/modulo | Classificacao | Decisao |
|---|---|---|
| `assinatura_html_precisa(person)` | SIGNATURE_ENGINE_KEEP | Referencia principal para Outlook classico. |
| `assinatura_html_outlook_new(person)` | SIGNATURE_ENGINE_KEEP | Referencia principal para Novo Outlook/Web. |
| `_resolver_contexto_assinatura(dados)` | SIGNATURE_ENGINE_KEEP | Normaliza nome, cargo, telefone e endereco. |
| `gerar_documento_word_assinatura(person)` | SIGNATURE_ENGINE_KEEP | Existe suporte DOCX legado, mas depende de `python-docx` e modelo Word. Nao habilitado no fluxo novo nesta etapa. |
| `_assert_html_assinatura_canonica(html)` | SIGNATURE_ENGINE_KEEP | Validacao de marcadores do HTML legado. |

## Componentes que nao devem ser portados como fonte canonica

| Item | Classificacao | Motivo |
|---|---|---|
| `sqlite3` e consultas em `src/legacy/flask_app.py` | SQLITE_DATA_SOURCE_DO_NOT_PORT | PostgreSQL e o cadastro `users` sao fonte canonica nova. |
| `ENS_DB_PATH` em runtime novo | SQLITE_DATA_SOURCE_DO_NOT_PORT | O novo fluxo nao deve consultar SQLite. |
| `data/ens.db` em importacao controlada | LEGACY_SQLITE_SEED_SOURCE | Pode ser lido apenas para inventario e seed de colaboradores no PostgreSQL. |
| Admin Flask | LEGACY_UI_FALLBACK_ONLY | Mantido apenas como fallback temporario. |
| Auth/sessao Flask | LEGACY_UI_FALLBACK_ONLY | Novo auth e RBAC ficam no FastAPI. |
| SMTP legado | SMTP_LEGACY_REVIEW | Nao portar sem decisao de seguranca. |
| MSAL/Graph legado | GRAPH_LEGACY_REVIEW | Fora de escopo nesta fase. |
| `.env` e `secrets/` | SENSITIVE_REVIEW | Nao copiar. Recomendada rotacao se houve exposicao previa. |

## Dependencias relevantes

Dependencias diretas observadas no legado:

- Flask / Werkzeug
- pandas
- requests
- msal
- python-docx
- SQLite via biblioteca padrao

Para o novo fluxo FastAPI/PostgreSQL, nenhuma dessas dependencias deve ser
adicionada automaticamente apenas por existir no legado. O renderer novo deve
continuar puro e sem SQLite. DOCX permanece pendente ate decisao especifica.

## Riscos

- `src/legacy/flask_app.py` mistura renderer, persistencia SQLite, UI, SMTP,
  Graph e autenticacao. Portar o arquivo inteiro recriaria acoplamento legado.
- Bancos `.db` contem dados antigos e nao devem ser usados como fonte
  operacional paralela. O `data/ens.db` pode ser lido apenas por script
  operacional controlado para popular PostgreSQL ate AD/Entra.
- A existencia de `.env` e `secrets/` exige tratamento como material sensivel.
- DOCX legado existe, mas habilitar download DOCX novo sem teste de fidelidade
  pode criar suporte incompleto.
