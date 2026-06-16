# GIT_H2_UNTRACKED_DECISION_MATRIX

Matriz conservadora por grupo/path. Nenhuma decisão aqui executa commit, ignore ou delete.

## 123 e 123.pub

Classificação: SENSITIVE_DO_NOT_OPEN
Risco: Alto
Motivo: Nome compatível com chave/artefato sensível; conteúdo não aberto.
Pode abrir conteúdo? não
Pode commitar? não
Pode ignorar? não
Pode deletar? não
Boundary necessária: SEC-H2
Aprovação humana necessária: sim
Observação: Não imprimir, não hashear, não abrir no chat.

## imports/

Classificação: LOCAL_DATA_DO_NOT_COMMIT
Risco: Alto
Motivo: Entrada operacional/imports pode conter dados reais.
Pode abrir conteúdo? não
Pode commitar? não
Pode ignorar? talvez após decisão
Pode deletar? não
Boundary necessária: SEC-H2 ou IMPORT-H2
Aprovação humana necessária: sim
Observação: Se precisar fixture, criar amostra anonimizadas em outra boundary.

## _migration_proposals/

Classificação: HUMAN_REVIEW_REQUIRED
Risco: Médio/Alto
Motivo: Árvore grande de proposta seletiva, com docs de segurança/plugins/memória.
Pode abrir conteúdo? somente revisão filtrada
Pode commitar? não agora
Pode ignorar? talvez
Pode deletar? não
Boundary necessária: DOCS-H2/SEC-H2
Aprovação humana necessária: sim
Observação: Não misturar com produto.

## assets/legacy/

Classificação: HUMAN_REVIEW_REQUIRED
Risco: Médio/Alto
Motivo: Árvore legacy grande com Laravel, JS, assets e possíveis referências externas.
Pode abrir conteúdo? somente metadados/inventário
Pode commitar? não agora
Pode ignorar? não antes de mapa
Pode deletar? não
Boundary necessária: LEGACY-H2
Aprovação humana necessária: sim
Observação: Boundary própria com dependency map.

## assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx

Classificação: HUMAN_REVIEW_REQUIRED
Risco: Médio
Motivo: DOCX grande 11.7 MB; binário não aberto.
Pode abrir conteúdo? não
Pode commitar? somente se aprovado
Pode ignorar? talvez
Pode deletar? não
Boundary necessária: LEGACY-H2
Aprovação humana necessária: sim
Observação: Decidir Git LFS/artifact/storage/ignore.

## assets/static/icons/*

Classificação: COMMIT_CANDIDATE_LEGACY
Risco: Médio
Motivo: Ícones de identidade/social untracked; dependência não confirmada nesta boundary.
Pode abrir conteúdo? não necessário
Pode commitar? somente LEGACY-H2
Pode ignorar? talvez
Pode deletar? não
Boundary necessária: LEGACY-H2
Aprovação humana necessária: sim
Observação: Não commitar em massa.

## docs/audit/HERMES_*_H1.md e docs/audit GIT_H2*

Classificação: COMMIT_CANDIDATE_DOCS
Risco: Baixo/Médio
Motivo: Relatórios de auditoria gerados; precisam revisão de sensibilidade.
Pode abrir conteúdo? sim, como docs
Pode commitar? sim após revisão
Pode ignorar? não
Pode deletar? não
Boundary necessária: DOCS-H2 ou commit docs
Aprovação humana necessária: sim
Observação: H2 atuais são candidatos mais fortes.

## docs/audit/screenshots/*

Classificação: IGNORE_CANDIDATE
Risco: Médio
Motivo: Screenshots podem conter dados visuais de UI; alguns paths incluem imports.
Pode abrir conteúdo? não
Pode commitar? não sem revisão
Pode ignorar? sim após política
Pode deletar? talvez manual
Boundary necessária: DOCS-H2/IGNORE-H2
Aprovação humana necessária: sim
Observação: Não abrir/OCR nesta boundary.

## .github/workflows/docker-build-push.yml

Classificação: COMMIT_CANDIDATE_CI
Risco: Alto
Motivo: Workflow de build/push pode publicar imagem ou depender de secrets.
Pode abrir conteúdo? sim em CI-H2
Pode commitar? somente CI-H2
Pode ignorar? não
Pode deletar? não
Boundary necessária: CI-H2
Aprovação humana necessária: sim
Observação: Revisar permissions/triggers/secrets antes.

## frontend/package-lock.json

Classificação: DO_NOT_TOUCH
Risco: Médio
Motivo: Lockfile altera reprodutibilidade/dependências.
Pode abrir conteúdo? sim em DEPS-H2
Pode commitar? não agora
Pode ignorar? não
Pode deletar? não
Boundary necessária: DEPS-H2/CI-H2
Aprovação humana necessária: sim
Observação: Não alterar package-lock nesta boundary.

## tests/test_import_conflict_detector.py

Classificação: COMMIT_CANDIDATE_TESTS
Risco: Médio
Motivo: Teste untracked relacionado a import conflict; conteúdo não revisado nesta boundary.
Pode abrir conteúdo? sim em TEST-H2
Pode commitar? somente após revisão
Pode ignorar? não
Pode deletar? não
Boundary necessária: TEST-H2
Aprovação humana necessária: sim
Observação: Garantir que não depende de dados reais.

## tests/test_security_headers.py

Classificação: COMMIT_CANDIDATE_TESTS
Risco: Médio
Motivo: Teste untracked citado por docs anteriores; conteúdo não revisado nesta boundary.
Pode abrir conteúdo? sim em TEST-H2
Pode commitar? somente após revisão
Pode ignorar? não
Pode deletar? não
Boundary necessária: TEST-H2
Aprovação humana necessária: sim
Observação: Validar contra backend atual.

## ai-lab/

Classificação: HUMAN_REVIEW_REQUIRED
Risco: Médio
Motivo: Resultados/model labs locais; podem ser úteis mas não produto.
Pode abrir conteúdo? somente filtrado
Pode commitar? não agora
Pode ignorar? talvez
Pode deletar? não
Boundary necessária: AI-LAB-H2
Aprovação humana necessária: sim
Observação: Separar docs/scripts/resultados.

## _audit_findings/

Classificação: HUMAN_REVIEW_REQUIRED
Risco: Médio
Motivo: CSV de achados agregado; pode conter paths/contexto.
Pode abrir conteúdo? sim em DOCS-H2
Pode commitar? talvez
Pode ignorar? talvez
Pode deletar? não
Boundary necessária: DOCS-H2
Aprovação humana necessária: sim
Observação: Não misturar com relatório H2.

## docx/pptx sample md outputs

Classificação: DELETE_CANDIDATE_MANUAL_ONLY
Risco: Baixo/Médio
Motivo: Amostras/outputs locais aparentes.
Pode abrir conteúdo? sim se não sensível
Pode commitar? não provável
Pode ignorar? talvez
Pode deletar? somente aprovação
Boundary necessária: IGNORE-H2
Aprovação humana necessária: sim
Observação: Não apagar agora.

