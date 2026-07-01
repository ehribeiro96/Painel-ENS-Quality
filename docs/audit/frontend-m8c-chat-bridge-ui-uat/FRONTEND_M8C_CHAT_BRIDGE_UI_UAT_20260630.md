# FRONTEND M8C Chat Bridge UI UAT

## Status
GO

## Escopo
- Validar a UI Apoema Chat Bridge com sessão autenticada.
- Confirmar providers e conversas vindos do backend.
- Confirmar criação de conversa, envio de mensagem e reentrada preservada via backend.
- Confirmar que `401/403/429` não são mascarados por fallback mock.
- Não validar streaming, cancelamento ou anexos como recursos reais.

## Estado Git
- Branch: `main`
- Divergência local/remota antes do UAT: `0 3`
- Stage: limpo
- Tracked diff: vazio
- Commits locais: `0ff01fe`, `f17bea5`, `6e8d6fa`

## Runtime
- Backend saudável em `http://localhost:8080/health/ready`
- Frontend preview estável em `http://127.0.0.1:5175`
- Sessão autenticada validada com storageState temporário fora do repo: `/tmp/apoema-m8c-chat-uat-storage-state.json`

## Rotas testadas
- `/apoema/chat`
- `/apoema-preview/chat`
- `/login`

## API smoke
- `GET /api/v1/ai-chat/health` autenticado: `200`
- `GET /api/v1/ai-chat/providers` autenticado: `200`
- `GET /api/v1/ai-chat/conversations` autenticado: `200`
- `GET /api/v1/ai-chat/providers` sem auth: `401 missing_token`

## UAT funcional
- Providers backend-backed: OK
- Lista de conversas backend-backed: OK
- Criação de nova conversa: OK
- Envio de mensagem sintética: OK
- Reload/reentrada preserva conversa via backend: OK
- Auth error não caiu em fallback mock: OK
- Mock/determinístico foi exibido de forma honesta quando aplicável: OK

## Segurança
- Sem provider key visível.
- Sem `storageState` commitado.
- Sem cookies/token impressos.
- Sem streaming/cancelamento/anexos simulados como recurso real.
- Sem fallback mascarando `401/403/429`.

## Screenshots
- `docs/audit/frontend-m8c-chat-bridge-ui-uat/screenshots/desktop-chat-initial.png`
- `docs/audit/frontend-m8c-chat-bridge-ui-uat/screenshots/desktop-chat-after-send.png`
- `docs/audit/frontend-m8c-chat-bridge-ui-uat/screenshots/mobile-chat-after-reload.png`
- `docs/audit/frontend-m8c-chat-bridge-ui-uat/screenshots/desktop-preview-chat.png`
- `docs/audit/frontend-m8c-chat-bridge-ui-uat/screenshots/anon-login-redirect.png`

## Gates
- `git diff --check`
- `PYTHONPATH=backend JWT_SECRET_KEY=... .venv/bin/python -m pytest -s -q`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `npm run build`
- `docker compose config --services`

## Push
- não
