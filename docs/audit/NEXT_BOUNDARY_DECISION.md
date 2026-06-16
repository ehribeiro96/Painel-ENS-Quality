# Next Boundary Decision

Boundary atual concluída/esperada: `CI-H2 — GitHub Actions docker build/push review without publishing`.

## Estado consolidado

- `AUDIT-H1`: `PARTIAL` por untracked antigos, mas os relatórios H1 são a base ativa de auditoria.
- `GIT-H2`: `PARTIAL` por grande volume de untracked, com triagem e matriz de decisão preservadas.
- `SEC-H2`: `GO COM RESSALVAS`; artefatos locais sensíveis seguem sem abertura de conteúdo e exigem revisão humana/manual.
- `DOCS-H2`: `GO`; consolidou os documentos ativos em `AUDIT_REPORT_INDEX_H2.md` e separou documentos antigos em `SUPERSEDED_AUDIT_DOCS_H2.md`.
- `IGNORE-H2`: `GO`; protege via ignore artefatos locais/sensíveis já classificados, sem ocultar candidatos de boundaries futuras.
- `CI-H2`: `GO` documental; workflow `.github/workflows/docker-build-push.yml` foi auditado sem versionar e sem publicar. Decisão: `NEEDS_CI_H3_HARDENING` e `MANUAL_ONLY_REQUIRED`.
- `QA-C1`: `PARTIAL` por backend HTTP indisponível no momento da validação.
- `QA-C2`: `GO`; relatório runtime HTTP atual.

## Decisão objetiva

Não versionar `.github/workflows/docker-build-push.yml` como está. Ele combina trigger `push` em `main`/`master`, `packages: write` e `docker/build-push-action` com `push: true`, podendo publicar imagem automaticamente após push se entrar no Git.

A próxima etapa deve reescrever o workflow em boundary própria como manual-only/build-only antes de qualquer versionamento.

## Próximas boundaries recomendadas

1. `CI-H3 — harden docker build workflow as manual-only, no publish`
   - Objetivo: reescrever o workflow CI como `workflow_dispatch` manual-only e inicialmente sem publish.
   - Escopo: editar/versionar workflow somente após remover publish automático, revisar permissões, definir `file: backend/Dockerfile` se aplicável e documentar tags.
   - Não deve executar `docker push`, `docker login`, publicar imagem, criar tag ou configurar secrets.

2. `LEGACY-H2 — legacy assets and DOCX large artifact decision`
   - Objetivo: decidir o destino de `assets/legacy/`, ícones sem referência comprovada e `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`.
   - Escopo: inventário por metadado, decisão humana e eventual commit seletivo.
   - Não deve abrir DOCX/binários grandes sem autorização explícita.

3. `TEST-H2 — pytest markers and validation standardization`
   - Objetivo: padronizar marcadores/comandos de validação sem misturar feature.
   - Escopo: testes e documentação de validação, com cuidado para não quebrar import discovery.
   - Não deve tocar importação Lansweeper, migrations ou fluxo Ativo -> Movimentação -> Macro.

4. `SEC-H3 — manual sensitive artifact remediation`
   - Condição: somente se revisão humana confirmar necessidade.
   - Objetivo: remediar artefato sensível real ou exposição histórica comprovada.
   - Escopo: segurança/manual; não imprimir segredos e não commitar valores sensíveis.

## O que não fazer agora

- Não fazer `git add .`, `git add -A` ou stage amplo.
- Não stagear `.github/workflows/docker-build-push.yml` como está.
- Não publicar imagem.
- Não rodar `docker push` ou `docker login`.
- Não criar tag.
- Não chamar GitHub API ou executar Actions.
- Não limpar untracked antigos.
- Não apagar, mover ou renomear documentos antigos.
- Não alterar código funcional.
- Não alterar migrations, Docker/Compose, `.env*`, package-lock, AI Chat/Ollama, imports, assets, frontend ou backend fora de boundary própria.
- Não commitar screenshots antigas, assets, imports, samples, package-lock ou outputs de laboratório fora de suas boundaries.

## Decisão final

Próxima boundary recomendada: `CI-H3 — harden docker build workflow as manual-only, no publish`.

Motivo: o workflow CI atual deve ficar fora do Git até ser endurecido; versioná-lo como está pode publicar `latest` automaticamente em GHCR após push para `main`/`master`.
