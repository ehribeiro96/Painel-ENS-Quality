# Ambiguous Remainers GIT-C3

Data/hora: 2026-06-15, America/Sao_Paulo

Status: `PARTIAL`

## 1. Resumo Executivo

A boundary `GIT-C3 — revisar ambíguos remanescentes` classificou e tratou os remanescentes do `GIT-C2` sem usar `git add .`, sem editar arquivos apenas para facilitar classificação e sem incluir artefatos locais/laboratório/samples/package-lock.

Comits realizados nesta boundary:

- `10daa46 chore(app): finalize app runtime integration`
- `af00925 chore(config): document local AI runtime defaults`
- `63ce5e1 test(security): cover icon sanitization`

O restante ficou fora por ser artefato local, sample, dependência ambígua, doc com EOF/whitespace legado ou arquivo que exigiria revisão humana adicional antes de qualquer commit.

## 2. Estado Inicial

- branch: `main`
- upstream: `origin/main`
- ahead/behind: `ahead 8`
- stage inicial: vazio
- worktree inicial: sujo com remanescentes do `GIT-C2`

## 3. Remanescentes Analisados

Arquivos e diretórios que permaneceram após `GIT-C2`:

- [backend/app/main.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/main.py)
- [/.env.example](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.env.example)
- [/.github/workflows/docker-build-push.yml](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.github/workflows/docker-build-push.yml)
- [docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md)
- [docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md)
- [docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md)
- [docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md)
- [docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md)
- [tests/test_hermes_icons_security.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_hermes_icons_security.py)
- [tests/test_import_conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_conflict_detector.py)
- [tests/test_security_headers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_security_headers.py)
- [frontend/package-lock.json](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/package-lock.json)
- [_migration_proposals/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/_migration_proposals/)
- [ai-lab/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/ai-lab/)
- [assets/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/assets/)
- [imports/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/)
- [docx_sample.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docx_sample.md)
- [docx_template_output.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docx_template_output.md)
- [pptx_sample.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/pptx_sample.md)
- [pptx_template_output.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/pptx_template_output.md)

## 4. Classificação por Arquivo

### Commits seguros criados

- [backend/app/main.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/main.py) -> `SAFE_COMMIT_APP_MAIN`
- [/.env.example](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.env.example) -> `SAFE_COMMIT_ENV_EXAMPLE`
- [tests/test_hermes_icons_security.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_hermes_icons_security.py) -> `SAFE_COMMIT_TEST_SECURITY`

### Defer human review

- [/.github/workflows/docker-build-push.yml](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.github/workflows/docker-build-push.yml) -> `DEFER_HUMAN_REVIEW` por whitespace/trailing format observado no `git diff --cached --check`
- [docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md) -> `DEFER_HUMAN_REVIEW` por EOF/whitespace legado
- [docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md) -> `DEFER_HUMAN_REVIEW` por EOF/whitespace legado
- [docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md) -> `DEFER_HUMAN_REVIEW` por EOF/whitespace legado
- [docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md) -> `DEFER_HUMAN_REVIEW` por mesclar recomendação e contexto operacional
- [docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md) -> `DEFER_HUMAN_REVIEW` por EOF/whitespace legado
- [tests/test_import_conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_conflict_detector.py) -> `DEFER_HUMAN_REVIEW` por blank line em EOF
- [tests/test_security_headers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_security_headers.py) -> `DEFER_HUMAN_REVIEW` por blank line em EOF

### Excluídos

- [frontend/package-lock.json](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/package-lock.json) -> `EXCLUDE_PACKAGE_LOCK`
- [/_migration_proposals/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/_migration_proposals/) -> `EXCLUDE_LOCAL_ARTIFACT`
- [/ai-lab/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/ai-lab/) -> `EXCLUDE_LOCAL_ARTIFACT`
- [/assets/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/assets/) -> `EXCLUDE_LOCAL_ARTIFACT`
- [/imports/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/) -> `EXCLUDE_LOCAL_IMPORT_DATA`
- [docx_sample.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docx_sample.md) -> `EXCLUDE_SAMPLE`
- [docx_template_output.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docx_template_output.md) -> `EXCLUDE_SAMPLE`
- [pptx_sample.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/pptx_sample.md) -> `EXCLUDE_SAMPLE`
- [pptx_template_output.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/pptx_template_output.md) -> `EXCLUDE_SAMPLE`

## 5. Commits Criados

### 10daa46

- `chore(app): finalize app runtime integration`

### af00925

- `chore(config): document local AI runtime defaults`

### 63ce5e1

- `test(security): cover icon sanitization`

## 6. Validações Executadas

- `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests`
- `PYTHONPATH=backend timeout 240 .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_security_headers.py -q -o addopts=''`
- retry com `-s`:
  - `20 passed, 1 warning`
- `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_security_headers.py tests/test_hermes_icons_security.py -q -o addopts=''`
- retry com `-s`:
  - `4 passed, 1 warning`
- `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_import_conflict_detector.py -q -o addopts=''`
- retry com `-s`:
  - `3 passed`

## 7. Scanner Redigido

Resultados esperados e seguros:

- `COMPOSIO_API_KEY`: nome de variável em docs e client, sem valor exposto.
- `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_ALLOWED_HOSTS`, `OLLAMA_MODEL`: nomes de configuração/documentação.
- `192.168.0.103` e `qwen3:1.7b-64k`: IP LAN e baseline de modelo documentados.
- `token`, `secret`, `password`, `bearer`, `api_key`: aparecem como nomes funcionais em docs/testes.

Nenhum segredo real foi impresso.

## 8. Stage Final

- stage: vazio

## 9. Worktree Final

Permanece no tree, fora dos commits:

- [/.github/workflows/docker-build-push.yml](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.github/workflows/docker-build-push.yml)
- [docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md)
- [docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D2_SAME_ORIGIN_UI_SMOKE.md)
- [docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md)
- [docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md)
- [docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md)
- [tests/test_import_conflict_detector.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_import_conflict_detector.py)
- [tests/test_security_headers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_security_headers.py)
- [frontend/package-lock.json](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/package-lock.json)
- [_migration_proposals/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/_migration_proposals/)
- [ai-lab/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/ai-lab/)
- [assets/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/assets/)
- [imports/](/home/estevaoqualityadm/projects/Painel-ENS-Quality/imports/)
- [docx_sample.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docx_sample.md)
- [docx_template_output.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docx_template_output.md)
- [pptx_sample.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/pptx_sample.md)
- [pptx_template_output.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/pptx_template_output.md)

## 10. Próxima Boundary Recomendada

`B4-E — legacy CSP and route polish`

Motivo:

- os commits seletivos de base/hardening/import/frontend/infra/Ollama já foram separados;
- os remanescentes agora são principalmente artefatos de revisão, docs com EOF/whitespace legado e exclusões explícitas;
- a próxima edição funcional documentada continua sendo o polimento de legado.
