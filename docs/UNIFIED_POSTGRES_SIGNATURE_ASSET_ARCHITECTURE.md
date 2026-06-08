# Arquitetura Unificada PostgreSQL + FastAPI + React/Vite

Data: 2026-06-02

## Decisao

O PostgreSQL e a fonte unica da verdade para a plataforma ENS ITAM.

SQLite legado fica restrito ao fallback `/assinaturas/` e `/admin/` enquanto
existir necessidade operacional temporaria. O arquivo `ens.db` tambem pode ser
lido por script operacional controlado como `LEGACY_SQLITE_SEED_SOURCE` para
popular colaboradores no PostgreSQL ate AD/Entra. Ele nao e banco operacional do
fluxo novo.

## Por que PostgreSQL e canonico

PostgreSQL permite modelar integridade relacional entre:

- colaboradores;
- ativos;
- movimentacoes;
- auditoria;
- importacoes;
- assinaturas geradas.

Tambem permite constraints, chaves unicas, chaves estrangeiras, indices,
transacoes e evolucao com Alembic. Isso e necessario para um sistema ITAM
auditavel. SQLite continua adequado apenas como origem historica simples.

## Como Lansweeper alimenta ativos

A planilha exportada do Lansweeper entra pelo pipeline atual:

```text
upload -> preset -> preview -> mapping -> staging -> validacao -> conflitos -> apply confirmado -> auditoria
```

Preset oficial:

- Nome: `Lansweeper Assets Export`
- Versao: `2026.06.ENS.1`

Regras preservadas:

- `Name` vira hostname apenas quando for identificador valido.
- `Serialnumber` e usado somente se valido.
- `Barcode` vazio nao vira patrimonio.
- `Custom1` e tipo principal.
- `Type` e fallback.
- `State` vira estado de origem e status operacional conforme politica.
- `lastuser` permanece apenas `imported_user_hint`.
- Nenhum colaborador e vinculado automaticamente por `lastuser`.

## Como colaboradores alimentam assinaturas

O fluxo novo de assinatura usa o cadastro `users` no PostgreSQL via
`UserService`. O renderer recebe um `User` canonico e gera HTML. Ele nao le:

- SQLite;
- `data/ens.db`;
- pasta externa `static` como banco;
- Flask legado;
- Graph/SMTP legado.

Campos usados nesta etapa:

- `name`;
- `email`;
- `job_title`;
- `department`;
- `business_unit`;
- `phone`.

Campos futuros recomendados, se houver necessidade real:

- `login`;
- `user_principal_name`;
- `mobile`;

Campos de rastreabilidade adicionados para seed legado:

- `source`;
- `source_metadata`.

O importador do `ens.db` preenche `source=legacy_ens_db` e metadados seguros
para reconciliacao futura com AD/Entra.

## Motor legado reaproveitado

A pasta externa foi analisada como fonte de conhecimento. O motor util esta em:

- `src/legacy/flask_app.py`
- `src/legacy/signature_model_spec.py`
- `src/legacy/assets_base64.py`
- `assets/templates/*`
- `assets/static/icons/*`
- modelos `.docx` em `assets/static/`

Foi reaproveitada a decisao tecnica do legado:

- HTML em tabelas;
- CSS inline;
- logo e icones;
- cores ENS;
- aviso bilingue;
- compatibilidade com Outlook por HTML simples.

Nao foi portado:

- SQLite;
- admin Flask;
- autenticacao Flask;
- SMTP;
- Graph/MSAL;
- `.env`;
- `secrets`;
- bancos `.db` como dependencia runtime;
- `.venv`;
- `node_modules`.

Excecao controlada: `data/ens.db` pode ser analisado e importado por script em
modo `AnalyzeOnly`, `DryRun` ou `Apply` confirmado, sem ser versionado ou
consultado pelo runtime.

## Frontend unico

O frontend oficial continua sendo `frontend/itam-platform`.

Fluxo esperado:

1. Listar colaboradores via API nova.
2. Selecionar colaborador.
3. Gerar preview via `/api/v1/signatures/{user_id}`.
4. Gerar/auditar via `/api/v1/signatures/generate/{user_id}`.
5. Baixar HTML via `/api/v1/signatures/{user_id}/download-html`.
6. Mostrar `/assinaturas/` apenas como fallback temporario.

## Legado como fallback

`/assinaturas/` e `/admin/` continuam montados para compatibilidade, mas nao sao
o fluxo canonico novo. Qualquer uso de SQLite fica limitado a esse fallback.

## Riscos e proximos passos

- O renderer novo ainda nao implementa DOCX. Habilitar DOCX exige avaliar
  `python-docx`, modelo Word e fidelidade visual.
- O modelo `users` ainda nao possui todos os campos de AD/Entra que podem ser
  necessarios futuramente.
- O fallback Flask ainda contem SQLite/SMTP/Graph e deve ser isolado
  progressivamente.
- Uma migracao futura pode adicionar `source` e `source_metadata` em
  colaboradores, mas isso nao deve ser destrutivo.
## Macros e Service Desk

O modulo de macros segue a mesma decisao arquitetural: PostgreSQL e a fonte operacional.

- `macros.json` e fonte temporaria de seed para `macro_templates`.
- `colaboradores.json` e fonte temporaria de hints para autocomplete.
- Nenhum JSON local e runtime definitivo.
- Nenhum usuario canonico e criado a partir de `colaboradores.json`.
- Macros de movimentacao usam ativos, usuarios e movimentacoes canonicas do PostgreSQL.
