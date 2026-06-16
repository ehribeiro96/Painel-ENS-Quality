# PRODUCT-H1 — Do-not-touch funcional

Este mapa protege áreas já validadas ou sensíveis durante a evolução funcional do Painel ENS-Quality. Qualquer alteração nelas exige boundary própria, plano explícito, validação e aceite humano quando indicado.

## Provider `ollama-lan`

Não mexer:
- Configuração e contrato do provider local via backend.
- Fluxo same-origin browser → backend → Ollama LAN.

Motivo:
- AI Chat/Ollama LAN foi validado recentemente e não deve voltar para mock silencioso nem expor IP LAN no browser.

Pode mexer somente em:
- Boundary AI explícita com smoke test e rollback.

## Baseline `qwen3:1.7b-64k`

Não mexer:
- Modelo baseline documentado para operação local.

Motivo:
- Serve como referência de qualidade/performance; trocar modelo invalida comparações e UAT.

Pode mexer somente em:
- Boundary de benchmark local com critérios objetivos.

## Sanitização `<think>`

Não mexer:
- Remoção/sanitização de blocos `<think>` na saída do chat.

Motivo:
- Evita vazamento de raciocínio bruto/ruído e protege UX.

Pode mexer somente em:
- Boundary de AI Chat com teste de regressão dedicado.

## ImportService validado

Não mexer:
- `backend/app/domains/imports/service.py`
- normalizers/classifiers/parsing/conflict detection
- política de staging/apply seguro
- regras que impedem sobrescrita operacional insegura

Motivo:
- Pipeline de importação foi validado e tem alto blast radius sobre dados canônicos.

Pode mexer somente em:
- Boundary IMPORT dedicada com fixtures sintéticas e testes de regressão.

## CSP legado

Não mexer:
- CSP validada do legado `/admin` e `/assinaturas`.
- Remoção de dependências externas já feita.

Motivo:
- Legado é sensível e foi validado com smoke próprio.

Pode mexer somente em:
- Boundary LEGACY com screenshot/smoke antes/depois.

## Migrations estáveis

Não mexer:
- `backend/alembic/versions/*`
- `backend/alembic.ini`
- schema/migrations sem necessidade funcional aprovada.

Motivo:
- PostgreSQL é fonte canônica; migrations manuais erradas quebram dados.

Pode mexer somente em:
- Boundary DB com plano, backup/rollback e comando via venv do projeto.

## Docker volumes

Não mexer:
- `postgres_data`, `app_data` e volumes locais.
- Não rodar `docker compose down -v`.

Motivo:
- Podem conter estado local importante.

Pode mexer somente em:
- Boundary OPS com backup e aprovação humana.

## Workflow Docker manual-only

Não mexer:
- Segurança do workflow Docker manual-only.
- Não reintroduzir publish automático, `latest`, registry login, secrets ou `packages: write` sem decisão.

Motivo:
- Workflow foi endurecido como validação manual build-only.

Pode mexer somente em:
- Boundary CI/PUBLISH com política de release aprovada.

## Assets runtime já commitados

Não mexer:
- Assets mínimos usados pelo legado/runtime.

Motivo:
- Remoção pode causar 404/regressão visual no legado.

Pode mexer somente em:
- Boundary LEGACY/ASSETS com mapa de referência e smoke.

## Pytest markers

Não mexer:
- Padronização recente de markers e comandos de validação.

Motivo:
- Foi consolidada para evitar execução confusa de testes.

Pode mexer somente em:
- Boundary TEST específica.

## Untracked sensíveis ignorados

Não mexer:
- Artefatos locais/sensíveis já classificados/ignorados.
- Não abrir conteúdo de `.env*`, dumps, bancos, tokens, credenciais, chaves, backups, planilhas reais ou imports brutos.

Motivo:
- Risco de exposição de segredo/dado real.

Pode mexer somente em:
- Boundary SEC/GIT com revisão por metadados ou aprovação humana explícita.

## Assets legacy não decididos

Não mexer:
- `assets/legacy/`
- DOCX grande em `assets/static/`
- ícones/imagens remanescentes não aprovados

Motivo:
- Classificação exige decisão humana; abrir imagens/DOCX/OCR estava fora das boundaries de higiene.

Pode mexer somente em:
- Boundary LEGACY-H3 ou equivalente, com decisão humana.

## Auth/RBAC

Não mexer:
- Fluxo de login/refresh/logout, JWT, roles, guards e permissões.

Motivo:
- Mudanças de auth têm impacto transversal e podem expor rotas críticas.

Pode mexer somente em:
- Boundary AUTH/SEC com plano e testes.

## MoveAssetDialog e fluxo Ativo → Movimentação → Macro

Não mexer sem boundary específica:
- `frontend/itam-platform/src/components/MoveAssetDialog.tsx`
- `AssetDetailsPage`
- endpoints `/assets/{id}/move`, `/assets/{id}/history`, `/movements/{id}/suggested-macro`, `/macros/generations/{id}/copied`

Motivo:
- É o fluxo crítico do produto. A próxima alteração deve ser pequena, testada e derivada de UAT-H1.

Pode mexer somente em:
- MOV-H1 ou MACRO-H1 com testes e UAT.
