# FRONTEND M8B Chat Bridge UI Implementation

## Status
GO

## Escopo
- Promover a UI Apoema Chat para consumir o contrato backend `ai-chat`.
- Manter providers e conversas vindos do backend como fonte primária.
- Preservar fallback local apenas para erro de rede/backend indisponível.
- Não implementar streaming, cancelamento ou anexos nesta fase.

## Arquivos alterados
- `frontend/itam-platform/src/apoema/lib/apoemaChatBridgeApi.ts`
- `frontend/itam-platform/src/apoema/pages/ChatPage.tsx`
- `frontend/itam-platform/src/apoema/components/ChatConversationSidebar.tsx`
- `frontend/itam-platform/src/apoema/components/ChatComposer.tsx`
- `frontend/itam-platform/src/apoema/components/ChatMessage.tsx`
- `frontend/itam-platform/src/apoema/types.ts`
- `frontend/itam-platform/src/apoema/styles/apoema.css`
- `tests/test_apoema_chat_bridge_ui_contract.py`

## Endpoints consumidos
- `GET /api/v1/ai-chat/health`
- `GET /api/v1/ai-chat/providers`
- `POST /api/v1/ai-chat/message`
- `GET /api/v1/ai-chat/conversations`
- `POST /api/v1/ai-chat/conversations`
- `GET /api/v1/ai-chat/conversations/{conversation_id}`
- `POST /api/v1/ai-chat/conversations/{conversation_id}/messages`

## Gaps fechados
- Providers passaram a vir do backend.
- Conversas passaram a vir do backend.
- Nova conversa é criada no backend antes do primeiro envio.
- Leitura de conversa usa o backend.
- Envio de mensagem usa o backend.
- Sidebar de conversas foi adicionada.
- Fallback local ficou restrito a falha de rede.

## Gaps não implementados por falta de backend
- Streaming.
- Cancelamento.
- Attachments / artifacts no chat.

## Segurança
- Sem chamada direta para OpenAI/Gemini/Ollama no frontend.
- Sem provider key ou segredo de provider no client.
- Sem `VITE_*` para segredo.
- Sem mascarar `401/403/429` com fallback local.
- Sem renderizar signed token cru.
- Sem expor path interno de storage.

## Gates
- `git diff --check`
- `PYTHONPATH=backend JWT_SECRET_KEY=... .venv/bin/python -m pytest -s -q`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `npm run build`
- `docker compose config --services`
- Smoke HTTP em `/apoema/chat`, `/apoema-preview/chat` e `/login`

## Push
- não
