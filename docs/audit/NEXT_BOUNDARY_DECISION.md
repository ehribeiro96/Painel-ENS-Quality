# Next Boundary Decision

Boundary atual concluída: `CI-H3 — harden docker build workflow as manual-only, no publish`.

## Estado consolidado

- `AUDIT-H1`: `PARTIAL` por untracked antigos, mas os relatórios H1 são a base ativa de auditoria.
- `GIT-H2`: `PARTIAL` por grande volume de untracked, com triagem e matriz de decisão preservadas.
- `SEC-H2`: `GO COM RESSALVAS`; artefatos locais sensíveis seguem sem abertura de conteúdo e exigem revisão humana/manual.
- `DOCS-H2`: `GO`; consolidou os documentos ativos em `AUDIT_REPORT_INDEX_H2.md` e separou documentos antigos em `SUPERSEDED_AUDIT_DOCS_H2.md`.
- `IGNORE-H2`: `GO`; protege via ignore artefatos locais/sensíveis já classificados, sem ocultar candidatos de boundaries futuras.
- `CI-H2`: `GO` documental; workflow `.github/workflows/docker-build-push.yml` foi auditado sem versionar e sem publicar. Decisão: `NEEDS_CI_H3_HARDENING` e `MANUAL_ONLY_REQUIRED`.
- `CI-H3`: `GO`; workflow Docker foi reescrito e versionado como validação manual build-only, sem publish, sem registry login, sem GHCR, sem `latest`, sem `packages: write`, sem trigger automático e sem secrets.
- `QA-C1`: `PARTIAL` por backend HTTP indisponível no momento da validação.
- `QA-C2`: `GO`; relatório runtime HTTP atual.

## Decisão objetiva

O workflow `.github/workflows/docker-build-push.yml` agora pode permanecer versionado como validação manual de build Docker. Ele não publica imagem e não usa credenciais.

Qualquer desenho futuro de publicação de imagem deve ser tratado em boundary separada, com decisão humana explícita, proteção de ambiente, política de tags e revisão de permissões.

## Próximas boundaries recomendadas

1. `LEGACY-H2 — legacy assets and DOCX large artifact decision`
   - Objetivo: decidir o destino de `assets/legacy/`, ícones sem referência comprovada e `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`.
   - Escopo: inventário por metadado, decisão humana e eventual commit seletivo.
   - Não deve abrir DOCX/binários grandes sem autorização explícita.

2. `TEST-H2 — pytest markers and validation standardization`
   - Objetivo: padronizar marcadores/comandos de validação sem misturar feature.
   - Escopo: testes e documentação de validação, com cuidado para não quebrar import discovery.
   - Não deve tocar importação Lansweeper, migrations ou fluxo Ativo -> Movimentação -> Macro.

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
- Não publicar imagem.
- Não rodar `docker push` ou `docker login`.
- Não criar tag.
- Não chamar GitHub API ou executar Actions.
- Não limpar untracked antigos.
- Não apagar, mover ou renomear documentos antigos.
- Não alterar código funcional.
- Não alterar migrations, Dockerfile, Docker Compose, `.env*`, package-lock, AI Chat/Ollama, imports, assets, frontend ou backend fora de boundary própria.
- Não commitar screenshots antigas, assets, imports, samples, package-lock ou outputs de laboratório fora de suas boundaries.

## Decisão final

Próxima boundary recomendada: `LEGACY-H2 — legacy assets and DOCX large artifact decision`.

Ordem seguinte: `TEST-H2 — pytest markers and validation standardization`.

`CI-H4 — publish workflow design` fica condicionado a decisão humana explícita de publicação de imagem. `SEC-H3` fica condicionado a confirmação humana de necessidade de revisão/remediação de segurança.
