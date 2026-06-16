# GIT-C5 — Legacy Assets Dependency Triage

Data/hora: 2026-06-16T10:17:11-03:00

Branch: `main`

Commit de assets runtime: `b76c5c4 chore(legacy): track required legacy assets`

## 1. Objetivo

Classificar os arquivos untracked em `assets/` e versionar somente o mínimo necessário para manter as rotas legadas `/admin/` e `/assinaturas/` funcionais, sem staged amplo e sem incluir arquivos sensíveis, dumps, bancos, backups ou artefatos legados sem dependência comprovada.

## 2. Escopo executado

- Inventário dos assets já rastreados.
- Inventário dos assets untracked.
- Busca de referências em `src/legacy/flask_app.py`, `backend/app/core/legacy.py` e templates legados.
- Scanner redigido para termos sensíveis em candidatos de commit.
- Staging seletivo por lista explícita de pathspec.
- Commit separado dos assets runtime mínimos.
- Documentação desta triagem.

## 3. Assets já rastreados antes do GIT-C5

- `assets/templates/base.html`
- `assets/static/vendor/tpl/css/templatemo-topic-listing.css`

Esses arquivos já faziam parte do runtime legado após `B4-E`.

## 4. Dependências comprovadas

- `src/legacy/flask_app.py` monta `assets/templates` como raiz de templates e `assets/static` como raiz estática.
- `backend/app/core/legacy.py` monta os apps Flask legados sob `/admin` e `/assinaturas`.
- `base.html` referencia Bootstrap local, Bootstrap Icons local, CSS `templatemo`, Header/Favicon e JavaScript vendor local.
- `admin.html`, `admin_edit.html`, `change_password.html`, `login.html`, `oauth_not_configured.html` são templates renderizados pelas rotas administrativas.
- `index.html` é template da rota pública de assinatura.
- `hero_outlook.html`, `v4/hero-outlook.css` e `v4/hero-outlook.js` são usados quando o guia visual/hero está habilitado.
- `signature-copy.js` é usado por templates de assinatura/admin para fluxo de cópia.
- O arquivo `ASSINATURAS DE E-MAIL (ENS_LOGO_AZUL_LGPD_semTWITTER)_v21.23.docx` é usado para geração/download do Word de assinatura.

## 5. Arquivos commitados

Categoria `REQUIRED_LEGACY_TEMPLATE`:

- `assets/templates/admin.html`
- `assets/templates/admin_edit.html`
- `assets/templates/change_password.html`
- `assets/templates/hero_outlook.html`
- `assets/templates/index.html`
- `assets/templates/login.html`
- `assets/templates/oauth_not_configured.html`

Categoria `REQUIRED_LEGACY_CSS`:

- `assets/static/vendor/tpl/css/bootstrap.min.css`
- `assets/static/vendor/tpl/css/bootstrap-icons.css`
- `assets/static/v4/hero-outlook.css`

Categoria `REQUIRED_LEGACY_JS`:

- `assets/static/vendor/tpl/js/bootstrap.bundle.min.js`
- `assets/static/vendor/tpl/js/jquery.min.js`
- `assets/static/vendor/tpl/js/jquery.sticky.js`
- `assets/static/vendor/tpl/js/click-scroll.js`
- `assets/static/vendor/tpl/js/custom.js`
- `assets/static/js/signature-copy.js`
- `assets/static/v4/hero-outlook.js`

Categoria `REQUIRED_LEGACY_FONT`:

- `assets/static/vendor/tpl/fonts/bootstrap-icons.woff`
- `assets/static/vendor/tpl/fonts/bootstrap-icons.woff2`

Categoria `REQUIRED_LEGACY_ICON_OR_IMAGE`:

- `assets/static/icons/Favicon.png`
- `assets/static/icons/Header.png`

Categoria `REQUIRED_PUBLIC_DOWNLOAD`:

- `assets/static/ASSINATURAS DE E-MAIL (ENS_LOGO_AZUL_LGPD_semTWITTER)_v21.23.docx`

## 6. Arquivos deixados fora

Categoria `DEFER_BINARY_OR_DOCX`:

- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`

Motivo: arquivo binário grande, com uso operacional separado no guia ilustrado. Não é requisito mínimo para renderizar `/admin/` e `/assinaturas/`; deve ser decidido em boundary própria de binários/downloads.

Categoria `DEFER_LEGACY_ARCHIVE`:

- `assets/legacy/`

Motivo: árvore legada ampla, incluindo projeto Laravel, bundle `hero.js`, source map e artefatos não referenciados diretamente pelo mount atual das rotas Flask. Não foi incluída para evitar liberar arquivo histórico sem triagem dedicada.

Categoria `EXCLUDE_LOCAL_OR_UNUSED`:

- `assets/static/icons/.gitkeep`
- `assets/static/icons/Logo.png`
- `assets/static/icons/facebook.png`
- `assets/static/icons/instagram.png`
- `assets/static/icons/linkedin.png`
- `assets/static/icons/tiktok.png`
- `assets/static/icons/youtube.png`

Motivo: não houve referência direta comprovada nos templates/rotas atuais analisados. Podem ser reavaliados em boundary específica caso o guia visual ou material de assinatura passe a exigir esses ícones.

## 7. Scanner redigido

Comando executado nos candidatos:

```bash
xargs -a /tmp/gitc5_required_legacy_assets.txt rg -n "api_key|token|secret|password|private_key|sk-|bearer|COMPOSIO_API_KEY|DATABASE_URL|REDIS_URL|POSTGRES_PASSWORD|JWT_SECRET|fonts\\.googleapis|fonts\\.gstatic|unsafe-eval" 2>/dev/null || true
```

Resultado:

- Foram encontrados nomes de campos esperados de formulário (`password`) e símbolos de template (`CSRF_TOKEN`, `colaborador_token`).
- Foi encontrada ocorrência de `globalEval` em `jquery.min.js`, biblioteca vendor legada local.
- Não houve exposição de valor de `.env`, API key, senha real, token real ou string de conexão.
- Nenhum arquivo de secrets, banco, dump ou backup foi adicionado.

## 8. Validação de staged diff

Antes do commit dos assets:

- `git diff --cached --name-status` listou somente os 22 arquivos selecionados.
- `git diff --cached --check` foi executado e retornou warnings de trailing whitespace/new blank line em templates/CSS legados adicionados.

Decisão: os assets foram commitados preservando conteúdo original, porque corrigir whitespace alteraria artefatos funcionais legados apenas para satisfazer higiene de diff. Esse risco fica documentado e deve ser tratado somente em boundary própria de normalização de assets legados, com validação visual.

## 9. Comandos relevantes

```bash
git status --short --branch
git diff --cached --name-status
git ls-files assets | sort
git ls-files --others --exclude-standard assets | sort
xargs -a /tmp/gitc5_required_legacy_assets.txt rg -n "<scanner redigido>" 2>/dev/null || true
git add --pathspec-from-file=/tmp/gitc5_required_legacy_assets.txt
git diff --cached --name-status
git diff --cached --check
git commit -m "chore(legacy): track required legacy assets"
```

## 10. Riscos restantes

- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` continua untracked por decisão de boundary; se a rota de guia DOCX for requisito de release, abrir boundary específica para binários/downloads.
- `assets/legacy/` continua untracked e deve permanecer fora até triagem dedicada de arquivo histórico.
- Os assets legados commitados carregam whitespace pré-existente; não foi normalizado nesta rodada.
- `hero_outlook.html` ainda contém uma referência externa de imagem; esse risco pertence a uma próxima boundary de CSP/assets remotos do legado, não à triagem de rastreabilidade.

## 11. Decisão

`GO COM RESSALVAS`

Motivo: o runtime mínimo de `/admin/` e `/assinaturas/` foi versionado seletivamente, sem staged amplo e sem inclusão de dados sensíveis. A ressalva é a presença de whitespace pré-existente nos assets legados e a pendência explícita do DOCX grande do guia ilustrado.
