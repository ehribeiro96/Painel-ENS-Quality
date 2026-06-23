# Apoema AI Chat Backend Integration

## Objetivo
Conectar o chat de IA do Apoema ao backend do Painel ENS-Quality, mantendo a escolha de provedores no servidor e preservando fallback local no frontend quando o backend ficar indisponível.

## Arquitetura
Frontend Apoema -> Backend Painel ENS-Quality -> Provedor de IA

## Endpoints
- `GET /api/v1/ai-chat/providers`
- `POST /api/v1/ai-chat/message`

## Provedores
- `Mock/Fallback`
- `Ollama`
- `Hermes`

## Configuração segura
- `AI_CHAT_DEFAULT_PROVIDER=mock`
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `OLLAMA_MODEL=qwen3:4b-64k`
- `OLLAMA_TIMEOUT_SECONDS=60`
- `HERMES_BASE_URL=`
- `HERMES_MODEL=hermes-agent`

## Segurança
- O frontend não chama `localhost:11434` nem `/api/chat` diretamente.
- O frontend envia somente metadados dos anexos.
- Nenhum token, cookie ou segredo é exposto no contrato do Apoema.
- URL arbitrária de provedor não é aceita pelo client.

## Comportamento de fallback
- `mock` é sempre funcional.
- `ollama` é resolvido no backend e retorna resposta estruturada.
- `hermes` permanece como placeholder seguro quando não houver endpoint real.
- Se o backend falhar, o frontend usa fallback local para manter a conversa ativa.

## Validação executada
- `npm run build` no frontend: OK.
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`: OK.
- `.venv/bin/python -m ruff check backend tests scripts`: OK.
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: OK.
- Smoke visual do Apoema Preview em `http://127.0.0.1:18086/apoema-preview/chat`: OK com fallback local.
- Navegador com backend abortado via rota de teste confirmou banner de fallback e resposta segura no chat.

## Evidência funcional
- Provider catalog carregado na UI.
- Mensagem enviada no chat.
- Resposta fallback exibida sem expor segredos.
- O fluxo visual permaneceu utilizável mesmo sem backend ativo.

## Limitações
- Upload binário real ainda não foi implementado nesta rodada.
- Hermes real depende de um contrato de endpoint futuro.
- Validação com backend vivo ficou limitada pelo ambiente local indisponível no momento do smoke.
