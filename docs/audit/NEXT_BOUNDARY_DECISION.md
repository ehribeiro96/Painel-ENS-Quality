# Next Boundary Decision

Boundary atual concluída/esperada: `IGNORE-H2 — gitignore hygiene for local artifacts`.

## Estado consolidado

- `AUDIT-H1`: `PARTIAL` por untracked antigos, mas os relatórios H1 são a base ativa de auditoria.
- `GIT-H2`: `PARTIAL` por grande volume de untracked, com triagem e matriz de decisão preservadas.
- `SEC-H2`: `GO COM RESSALVAS`; artefatos locais sensíveis seguem sem abertura de conteúdo e exigem revisão humana/manual.
- `DOCS-H2`: `GO`; consolidou os documentos ativos em `AUDIT_REPORT_INDEX_H2.md` e separou documentos antigos em `SUPERSEDED_AUDIT_DOCS_H2.md`.
- `IGNORE-H2`: protege via ignore artefatos locais/sensíveis já classificados, sem ocultar candidatos de boundaries futuras.
- `QA-C1`: `PARTIAL` por backend HTTP indisponível no momento da validação.
- `QA-C2`: `GO`; relatório runtime HTTP atual.

## Decisão objetiva

Não iniciar feature funcional ampla enquanto houver workflow CI, assets legados, DOCX grande, testes pendentes e documentação histórica sem revisão. Após IGNORE-H2, a próxima etapa deve analisar candidatos futuros ainda visíveis, sem esconder dívida técnica por ignore genérico.

## Próximas boundaries recomendadas

1. `CI-H2 — GitHub Actions docker build/push review`
   - Objetivo: revisar `.github/workflows/docker-build-push.yml` sem publicar imagens e sem alterar runtime local.
   - Escopo: análise e eventual commit seletivo do workflow somente após revisão de triggers, permissões, registry e secrets esperados.
   - Não deve fazer push, release, publicação de imagem ou configuração de secrets.

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
- Não limpar untracked antigos.
- Não apagar, mover ou renomear documentos antigos.
- Não alterar código funcional.
- Não alterar migrations, Docker/Compose, `.env*`, package-lock, AI Chat/Ollama, imports, assets, frontend ou backend fora de boundary própria.
- Não commitar screenshots antigas, assets, imports, samples, package-lock ou outputs de laboratório fora de suas boundaries.
- Não adicionar ignore genérico para `*.md`, `*.csv`, `*.docx`, `*.png` ou `*.json`.

## Decisão final

Próxima boundary recomendada: `CI-H2 — GitHub Actions docker build/push review`.

Motivo: o workflow CI continua visível propositalmente e pode ter impacto de release/publicação; deve ser revisado antes de legado, testes ou qualquer feature funcional ampla.
