# Next Boundary Decision

Boundary atual concluída/esperada: `DOCS-H2 — audit docs consolidation and selective commit`.

## Estado consolidado

- `AUDIT-H1`: `PARTIAL` por untracked antigos, mas os relatórios H1 são a base ativa de auditoria.
- `GIT-H2`: `PARTIAL` por grande volume de untracked, com triagem e matriz de decisão preservadas.
- `SEC-H2`: `GO COM RESSALVAS`; artefatos locais sensíveis seguem sem abertura de conteúdo e exigem revisão humana/manual.
- `QA-C1`: `PARTIAL` por backend HTTP indisponível no momento da validação.
- `QA-C2`: `GO`; relatório runtime HTTP atual.
- `DOCS-H2`: consolida os documentos ativos em `AUDIT_REPORT_INDEX_H2.md` e separa documentos antigos em `SUPERSEDED_AUDIT_DOCS_H2.md`.

## Decisão objetiva

Não iniciar feature funcional ampla enquanto houver untracked antigos, artefatos locais sensíveis e documentação histórica sem revisão. A próxima etapa deve reduzir risco operacional sem tocar código funcional.

## Próximas boundaries recomendadas

1. `IGNORE-H2 — gitignore hygiene for local artifacts`
   - Objetivo: aplicar hygiene de ignore para artefatos locais já classificados.
   - Escopo: `.gitignore`/ignore policy apenas se explicitamente autorizado nessa boundary.
   - Não deve abrir conteúdo de `123`, `123.pub` ou `imports/`.

2. `CI-H2 — GitHub Actions docker build/push review`
   - Objetivo: revisar workflow CI untracked sem publicar imagens e sem alterar runtime local.
   - Escopo: análise e eventual commit seletivo do workflow somente após revisão.
   - Não deve fazer push, release ou publicação de imagem.

3. `LEGACY-H2 — legacy assets and DOCX large artifact decision`
   - Objetivo: decidir o destino de `assets/legacy/`, ícones sem referência comprovada e DOCX grande do guia ilustrado.
   - Escopo: inventário por metadado, decisão humana e eventual commit seletivo.
   - Não deve abrir DOCX/binários grandes sem autorização explícita.

4. `TEST-H2 — pytest markers and validation standardization`
   - Objetivo: padronizar marcadores/comandos de validação sem misturar feature.
   - Escopo: testes e documentação de validação, com cuidado para não quebrar import discovery.
   - Não deve tocar importação Lansweeper, migrations ou fluxo Ativo -> Movimentação -> Macro.

5. `SEC-H3 — manual sensitive artifact remediation`
   - Condição: somente se revisão humana confirmar necessidade.
   - Objetivo: remediar artefato sensível real ou exposição histórica comprovada.
   - Escopo: segurança/manual; não imprimir segredos e não commitar valores sensíveis.

## O que não fazer agora

- Não fazer `git add .`, `git add -A` ou stage amplo de `docs/audit/`.
- Não limpar untracked antigos.
- Não apagar, mover ou renomear documentos antigos.
- Não alterar código funcional.
- Não alterar migrations, Docker/Compose, `.env*`, `.gitignore`, `.dockerignore`, package-lock, AI Chat/Ollama, imports, assets, frontend ou backend fora de boundary própria.
- Não commitar screenshots antigas, assets, imports, samples, package-lock ou outputs de laboratório.

## Decisão final

Próxima boundary recomendada: `IGNORE-H2 — gitignore hygiene for local artifacts`.

Motivo: ela reduz risco de stage acidental dos artefatos já identificados por H1/GIT-H2/SEC-H2 antes de qualquer feature funcional, CI, legado ou padronização de testes.
