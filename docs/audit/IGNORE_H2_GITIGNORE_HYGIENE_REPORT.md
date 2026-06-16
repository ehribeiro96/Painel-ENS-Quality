# IGNORE-H2 — Gitignore Hygiene for Local Artifacts

Boundary: `IGNORE-H2 — gitignore hygiene for local artifacts`

## Resumo executivo

Status: `GO` esperado após commit seletivo, se stage final ficar vazio e nenhum segredo real for identificado.

Stage inicial/final:

- Stage inicial: vazio em `main...origin/main [ahead 16]` na FASE 0.
- Stage final esperado: vazio após o commit seletivo IGNORE-H2; evidência final deve ser registrada no chat.

Arquivos alterados:

- `.gitignore`
- `.dockerignore`
- `docs/audit/IGNORE_H2_GITIGNORE_HYGIENE_REPORT.md`
- `docs/audit/README.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`

## Escopo

Esta boundary aplicou hygiene mínima de ignore para artefatos locais/sensíveis já classificados em `SEC-H2` e `DOCS-H2`. Não houve abertura de conteúdo sensível, remoção, movimentação, renomeação, stage em massa ou alteração de código funcional.

## Padrões adicionados em .gitignore

```gitignore
# Local sensitive artifacts — IGNORE-H2
123
123.pub
*.pem
*.key
*.pfx
*.p12
*.crt
*.cer
*.der
*.kdbx

# Local data/imports — IGNORE-H2
imports/
*.sqlite
*.sqlite3
*.db
*.dump
*.bak
*.sql

# Local generated samples — IGNORE-H2
docx_sample.md
docx_template_output.md
pptx_sample.md
pptx_template_output.md

# Local tool/audit outputs — IGNORE-H2
_audit_findings/
ai-lab/

# Wrong-level generated lockfile — IGNORE-H2
frontend/package-lock.json
```

## Padrões adicionados em .dockerignore

```dockerignore
# Local sensitive artifacts — IGNORE-H2
123
123.pub
*.pem
*.key
*.pfx
*.p12
*.crt
*.cer
*.der
*.kdbx

# Local data/imports — IGNORE-H2
imports/
*.sqlite
*.sqlite3
*.db
*.dump
*.bak
*.sql

# Local generated samples — IGNORE-H2
docx_sample.md
docx_template_output.md
pptx_template_output.md
pptx_sample.md

# Local tool/audit outputs — IGNORE-H2
_audit_findings/
ai-lab/
```

Observação conservadora: `.dockerignore` já existia antes da boundary e já continha regras próprias fora do escopo de IGNORE-H2. Esta boundary não removeu regras existentes.

## Itens agora protegidos

- `123`
- `123.pub`
- `imports/`
- extensões sensíveis: `*.pem`, `*.key`, `*.pfx`, `*.p12`, `*.crt`, `*.cer`, `*.der`, `*.kdbx`
- bancos/dumps locais: `*.sqlite`, `*.sqlite3`, `*.db`, `*.dump`, `*.bak`, `*.sql`
- outputs locais:
  - `docx_sample.md`
  - `docx_template_output.md`
  - `pptx_sample.md`
  - `pptx_template_output.md`
  - `_audit_findings/`
  - `ai-lab/`
- lockfile gerado no nível errado: `frontend/package-lock.json`

## Itens propositalmente NÃO ignorados

- `.github/workflows/docker-build-push.yml`
- `assets/legacy/` no Git ignore desta boundary
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`
- testes pendentes:
  - `tests/test_import_conflict_detector.py`
  - `tests/test_security_headers.py`
- docs/audit antigos
- screenshots antigas

Esses itens continuam visíveis para boundaries próprias: `CI-H2`, `LEGACY-H2` e `TEST-H2`.

## Validação git check-ignore

Validações executadas sem abrir conteúdo sensível:

- `git check-ignore -v 123 123.pub` confirmou proteção por `.gitignore`.
- `find imports -maxdepth 2 -type f ... git check-ignore -v` confirmou proteção de arquivos em `imports/` por `imports/`.
- `git check-ignore -v _audit_findings/all_findings.csv ai-lab/docx_to_md.py docx_sample.md docx_template_output.md pptx_sample.md pptx_template_output.md frontend/package-lock.json` confirmou proteção dos outputs locais e do lockfile gerado no nível errado.
- `git check-ignore -v .github/workflows/docker-build-push.yml`, testes pendentes e DOCX do guia não retornaram match, confirmando que não foram ocultados pelo Git ignore.
- `git check-ignore -v assets/legacy/hero.js` não retornou match, confirmando que `assets/legacy/` não foi ignorado pelo Git nesta boundary.

## Riscos restantes

- `.github/workflows/docker-build-push.yml` continua untracked e visível para `CI-H2`.
- `assets/legacy/`, ícones estáticos e DOCX grande continuam visíveis para `LEGACY-H2`.
- Testes pendentes continuam visíveis para `TEST-H2`.
- Docs/audit históricos e screenshots antigas continuam visíveis/deferidos conforme `DOCS-H2`.
- Se revisão humana confirmar segredo real em artefato local ou histórico, abrir `SEC-H3`.

## Próximas boundaries recomendadas

1. `CI-H2 — GitHub Actions docker build/push review`
2. `LEGACY-H2 — legacy assets and DOCX large artifact decision`
3. `TEST-H2 — pytest markers and validation standardization`
4. `SEC-H3 — manual sensitive artifact remediation`, somente se revisão humana confirmar necessidade

## Decisão final

`GO` para commit seletivo dos arquivos de ignore e documentação desta boundary se:

- scanner redigido dos candidatos não identificar segredo real;
- stage seletivo contiver somente `.gitignore`, `.dockerignore`, relatório e índices autorizados;
- `git diff --cached --check` passar;
- commit for criado;
- stage final ficar vazio.
