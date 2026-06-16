# SEC-H2 — Gitignore Proposal

Este arquivo é uma proposta documental. Nenhuma alteração foi aplicada em `.gitignore` nesta boundary.

## Objetivo

Evitar que artefatos locais sensíveis, dados de importação, bancos/dumps, chaves/certificados e outputs temporários apareçam como untracked candidatos a commit.

## Padrões recomendados

```gitignore
# Local sensitive artifacts
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

# Local data/imports
imports/
*.sqlite
*.sqlite3
*.db
*.dump
*.bak
*.sql

# Local generated samples
docx_sample.md
docx_template_output.md
pptx_sample.md
pptx_template_output.md

# Local audit/tool outputs, only if approved
_audit_findings/
ai-lab/
```

## Motivos

- `123` e `123.pub` são artefatos locais potencialmente sensíveis.
- `imports/` pode conter dados reais ou material operacional.
- Extensões de chave/certificado/dump/banco não devem entrar no Git.
- Samples docx/pptx parecem outputs locais.
- `_audit_findings/` e `ai-lab/` podem ser úteis, mas devem ser versionados apenas após revisão humana.

## Risco de falso positivo

- `123.pub` poderia ser apenas uma chave pública não secreta, mas ainda não deve ser commitada sem intenção explícita.
- `*.sql` pode incluir migration ou script legítimo se usado em diretórios controlados; por isso a regra precisa revisão antes de aplicar.
- `_audit_findings/` e `ai-lab/` podem conter artefatos úteis; ignorar tudo pode esconder material que deveria virar doc.
- `imports/` pode conter manifestos úteis, mas por padrão deve ser tratado como dado local.

## Aprovação humana necessária

Sim. Aplicar estes padrões deve acontecer apenas na boundary `IGNORE-H2 — gitignore hygiene for local artifacts`.
