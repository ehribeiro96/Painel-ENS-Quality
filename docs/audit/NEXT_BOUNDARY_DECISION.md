# Next Boundary Decision

Boundary atual concluída: `LEGACY-H2 — legacy assets and DOCX large artifact decision`.

## Estado consolidado

- `AUDIT-H1`: `PARTIAL` por untracked antigos, mas os relatórios H1 são a base ativa de auditoria.
- `GIT-H2`: `PARTIAL` por grande volume de untracked, com triagem e matriz de decisão preservadas.
- `SEC-H2`: `GO COM RESSALVAS`; artefatos locais sensíveis seguem sem abertura de conteúdo e exigem revisão humana/manual.
- `DOCS-H2`: `GO`; consolidou os documentos ativos em `AUDIT_REPORT_INDEX_H2.md` e separou documentos antigos em `SUPERSEDED_AUDIT_DOCS_H2.md`.
- `IGNORE-H2`: `GO`; protege via ignore artefatos locais/sensíveis já classificados, sem ocultar candidatos de boundaries futuras.
- `CI-H2`: `GO` documental; workflow `.github/workflows/docker-build-push.yml` foi auditado sem versionar e sem publicar. Decisão: `NEEDS_CI_H3_HARDENING` e `MANUAL_ONLY_REQUIRED`.
- `CI-H3`: `PARTIAL` aceitável por ausência de `actionlint`; workflow Docker foi reescrito e versionado como validação manual build-only, sem publish, sem registry login, sem GHCR, sem `latest`, sem `packages: write`, sem trigger automático e sem secrets.
- `LEGACY-H2`: `GO` documental; `assets/legacy/`, DOCX grande e ícones remanescentes foram inventariados por metadados. Nenhum asset foi commitado, nenhum DOCX/imagem foi aberto e nenhuma alteração funcional foi feita.
- `QA-C1`: `PARTIAL` por backend HTTP indisponível no momento da validação.
- `QA-C2`: `GO`; relatório runtime HTTP atual.

## Decisão objetiva

Não versionar assets remanescentes nesta etapa. A decisão LEGACY-H2 separa os grupos assim:

- `assets/legacy/`: `LEGACY_ARCHIVE_DEFER`, sem commit até decisão humana.
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`: `BINARY_LARGE_HUMAN_REVIEW`, sem abertura e sem commit.
- `assets/static/icons/Logo.png`: provável `REQUIRED_RUNTIME_ASSET` por referência no backend atual, mas exige `IMAGE_HUMAN_REVIEW` e boundary futura antes de commit.
- Ícones sociais: `IMAGE_HUMAN_REVIEW`, sem uso local runtime comprovado; podem ser candidatos futuros para reduzir dependência externa do legado.
- Referências externas em legado: `EXTERNAL_REFERENCE_RISK`, documentadas sem correção nesta boundary.

## Próximas boundaries recomendadas

1. `TEST-H2 — pytest markers and validation standardization`
   - Objetivo: padronizar marcadores/comandos de validação sem misturar feature.
   - Escopo: testes e documentação de validação, com cuidado para não quebrar import discovery.
   - Não deve tocar importação Lansweeper, migrations ou fluxo Ativo -> Movimentação -> Macro.

2. `LEGACY-H3 — legacy archive/manual artifact handling`
   - Condição: somente se decisão humana aprovar.
   - Objetivo: decidir operacionalmente se `assets/legacy/`, DOCX grande, `Logo.png` e ícones sociais serão arquivados, ignorados, descartados manualmente ou versionados seletivamente.
   - Não deve abrir DOCX/imagens sem autorização explícita, nem misturar archive legado com alteração funcional.

3. `CI-H4 — publish workflow design`
   - Condição: somente se houver decisão humana explícita para publicar imagem.
   - Objetivo: desenhar publish seguro com proteção manual, permissões mínimas, política de tags e nome de imagem aprovado.
   - Não deve reintroduzir publish automático, `latest` sem política, login sem proteção, secrets sem necessidade ou `packages: write` fora de fluxo aprovado.

4. `SEC-H3`
   - Condição: somente se revisão humana confirmar necessidade.
   - Objetivo: remediar artefato sensível real ou exposição histórica comprovada.
   - Escopo: segurança/manual; não imprimir segredos e não commitar valores sensíveis.

## O que não fazer agora

- Não fazer `git add .`, `git add -A` ou stage amplo.
- Não commitar `assets/legacy/`.
- Não commitar `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`.
- Não commitar `assets/static/icons/Logo.png` ou ícones sociais sem boundary futura.
- Não abrir DOCX grande.
- Não usar OCR.
- Não analisar imagens visualmente sem autorização.
- Não publicar imagem.
- Não rodar `docker push` ou `docker login`.
- Não criar tag.
- Não chamar GitHub API ou executar Actions.
- Não limpar untracked antigos.
- Não apagar, mover ou renomear documentos antigos.
- Não alterar código funcional.
- Não alterar migrations, Dockerfile, Docker Compose, `.env*`, package-lock, AI Chat/Ollama, imports, frontend ou backend fora de boundary própria.

## Decisão final

Próxima boundary recomendada: `TEST-H2 — pytest markers and validation standardization`.

`LEGACY-H3 — legacy archive/manual artifact handling` fica condicionada a decisão humana explícita sobre o destino dos assets legados e do DOCX grande.

`CI-H4 — publish workflow design` fica condicionado a decisão humana explícita de publicação de imagem. `SEC-H3` fica condicionado a confirmação humana de necessidade de revisão/remediação de segurança.
