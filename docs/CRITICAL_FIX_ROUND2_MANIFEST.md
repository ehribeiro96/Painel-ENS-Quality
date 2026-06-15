# Critical Fix Round 2 Manifest

- Data/hora: 2026-06-08 18:21:53 -03
- Branch: `main`
- Objetivo: corrigir riscos críticos pós-auditoria com foco em rate limit compartilhado, endurecimento de CSP, higiene de release e validação do ambiente Python, sem refatoração ampla nem alteração de regra de negócio.

## Arquivos que pretendo alterar

- `backend/app/api/v1/routes/ai_chat.py`
- `backend/app/main.py`
- `backend/app/domains/ai_chat/rate_limit.py`
- `tests/test_ai_chat_api.py`
- `tests/test_ai_chat_hardening.py`
- `tests/test_ai_chat_rate_limit.py`
- `tests/test_security_headers.py`
- `.dockerignore`
- `docs/AI_CHAT_RATE_LIMIT_REDIS_REPORT.md`
- `docs/CSP_HARDENING_REPORT.md`
- `docs/RELEASE_DOCS_HYGIENE_REPORT.md`
- `docs/VISUAL_SMOKE_MANUAL_RUNBOOK.md`
- `docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md`

## Arquivos que não posso alterar

- `.env`
- qualquer arquivo de `secrets/`
- `uat_evidence/`
- bancos locais e dumps
- `backend/app/domains/imports/*`
- `backend/app/domains/signatures/*`
- `backend/app/domains/macros/*`
- `backend/app/domains/assets/*` além do necessário para segurança transversal
- `backend/app/domains/users/*` além do necessário para RBAC transversal
- `backend/app/domains/asset_movements/*`
- `backend/app/domains/import_service/*`
- `frontend/itam-platform/src/lib/api.ts`
- `frontend/itam-platform/src/lib/types.ts`
- qualquer arquivo de regra de negócio não relacionado ao risco crítico

## Comandos executados

- `git status --short`
- `git branch --show-current`
- `pwd`
- `rg -n "AI_CHAT_RATE_LIMIT|rate limit|ratelimit|redis|CSP|Content-Security-Policy|unsafe-inline|ENABLE_AI_CHAT|ai-chat" backend frontend tests docs .gitignore .dockerignore`
- `git rev-parse --abbrev-ref HEAD`
- `git log -1 --oneline --decorate`
- `sed -n '1,220p' .gitignore`
- `sed -n '1,220p' .dockerignore`
- `sed -n '1,240p' backend/app/api/v1/routes/ai_chat.py`
- `sed -n '1,280p' backend/app/domains/ai_chat/service.py`
- `sed -n '1,220p' backend/app/core/config/settings.py`
- `sed -n '1,240p' backend/app/main.py`
- `sed -n '1,200p' backend/app/domains/ai_chat/__init__.py`
- `sed -n '1,260p' tests/test_ai_chat_api.py`
- `sed -n '1,320p' tests/test_ai_chat_hardening.py`
- `sed -n '1,260p' backend/app/domains/ai_chat/providers.py`
- `sed -n '1,220p' backend/app/core/startup.py`
- `sed -n '1,220p' .env.example`
- `sed -n '1,220p' backend/app/core/legacy.py`
- `sed -n '1,220p' frontend/itam-platform/index.html`
- `sed -n '1,220p' frontend/itam-platform/vite.config.ts`
- `sed -n '1,260p' backend/app/core/frontend.py`
- `date '+%Y-%m-%d %H:%M:%S %Z'`
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `cd frontend/itam-platform && npm run build`
- `cd frontend/itam-platform && ENABLE_AI_CHAT=true npm run build`
- `cd frontend/itam-platform && ENABLE_AI_CHAT=false npm run build`
- `docker compose config >/tmp/painel-compose-config.out && echo OK`

## Riscos

- O rate limit em Redis precisa ser validado com comportamento local e multi-processo sem vazar `user_id`, prompt ou chave de API.
- A CSP pode continuar parcialmente faseada para `/admin/` e `/assinaturas/` se a remoção total de `unsafe-inline` ameaçar o legado ou o build da SPA.
- O ambiente Python pode falhar por dependência ausente ou serviços externos, e isso deve ser registrado sem mascarar o motivo.
- A higiene de release depende de garantir que `docs/audit/` possa ser versionado sem reabrir o restante de `docs/` sensível no contexto de build.

## Atualizacao desta rodada

- Estado validado no recorte B2:
  - o rate limit do AI Chat não usa `eval`;
  - a chave do rate limit é derivada de `user_id` hash + janela temporal;
  - o renderer SVG do frontend não usa `dangerouslySetInnerHTML`;
  - os testes dedicados de AI Chat e headers de segurança passaram.
- Baseline executado nesta sessão:
  - `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests`
  - `timeout 120 .venv/bin/python -m ruff check backend/app/api/v1/routes/ai_chat.py backend/app/domains/ai_chat tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_security_headers.py`
  - `PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_security_headers.py -q -o addopts=''`
- Observacao operacional:
  - a primeira execucao da suite `pytest` falhou por um problema de captura no encerramento;
  - a repeticao com `-s` passou e produziu a evidencia objetiva desta rodada;
  - o build do frontend foi rerodado no fechamento B2 com `npm run build` e falhou por limitação ambiental WSL/UNC/`tsc`;
  - isso não alterou a conclusão funcional de B2, apenas manteve a ressalva operacional.
