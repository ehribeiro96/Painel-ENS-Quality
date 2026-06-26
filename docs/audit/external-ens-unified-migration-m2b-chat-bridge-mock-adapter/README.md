# M2B_CHAT_BRIDGE_MOCK_ADAPTER

Status final: GO

## 1. Status
GO

## 2. Objetivo
Consolidar a ponte do Apoema Chat com um adaptador mock determinístico no backend e uma cópia honesta no frontend, mantendo autenticação, RBAC e fallback local explícito.

## 3. Base M2A
A base M2A já havia fechado a superfície do chat no Painel ENS-Quality com:
- rota `/api/v1/ai-chat/*` protegida por autenticação/RBAC;
- provider mock disponível no backend;
- contrato de frontend apontando para o backend do Painel;
- fallback local preservado para indisponibilidade de rede;
- sem integração real com provedor externo nesta fase.

## 4. O que foi implementado
- Ajuste do rótulo do provider mock para "Mock adapter" no backend e no frontend.
- Copia de UI deixando explícito quando o adaptador mock local determinístico está ativo.
- Cópia de UI deixando explícito quando o backend está indisponível e o fallback local está em uso.
- Cobertura de teste reforçada para a mensagem de segurança/UX da página Apoema.
- Atualização do relatório auditável da fase M2B.

## 5. Endpoints validados
Todos os endpoints abaixo permanecem sob a política de autenticação já existente do projeto (`require_role(...)`).

- `GET /api/v1/ai-chat/health`
- `GET /api/v1/ai-chat/providers`
- `POST /api/v1/ai-chat/message`
- `GET /api/v1/ai-chat/conversations`
- `POST /api/v1/ai-chat/conversations`
- `GET /api/v1/ai-chat/conversations/{conversation_id}`
- `POST /api/v1/ai-chat/conversations/{conversation_id}/messages`

## 6. Request/response mínimo
### Request
```json
{
  "conversation_id": "apoema-test",
  "provider": "mock",
  "model": "fallback-local",
  "message": "Olá Apoema",
  "mode": "assistente_n2",
  "attachments": [],
  "context": {
    "route": "apoema-chat",
    "source": "apoema-preview"
  }
}
```

### Response
```json
{
  "conversation_id": "apoema-test",
  "message_id": "<uuid>",
  "provider": "mock",
  "model": "fallback-local",
  "status": "ok",
  "content": "Modo mock: resposta simulada ...",
  "created_at": "<timestamp ISO-8601>",
  "usage": {
    "prompt_tokens": null,
    "completion_tokens": null,
    "total_tokens": null
  },
  "error": null
}
```

## 7. Provider mock/determinístico
- O provider mock é explícito no catálogo.
- A resposta é determinística e produzida localmente.
- Não há dependência de internet nem de provider real para a fase M2B.
- O catálogo continua listando `mock`, `ollama` e `hermes`, mas a UI destaca que o caminho de UAT desta fase é o mock local.

## 8. Auth/RBAC
- A rota segue usando a autenticação existente.
- `401` sem token continua preservado com `{"detail":"missing_token"}`.
- `403` continua respeitando RBAC.
- Não houve alteração em `AuthProvider`, `ProtectedRoute`, Docker Compose ou migrations.

## 9. Fallback local do frontend
- O frontend continua com fallback local quando o backend está indisponível.
- A cópia da UI deixa isso explícito em vez de sugerir integração real.
- O fallback local é usado apenas para continuidade visual/UX quando a rede ou o backend falham.

## 10. O que não foi implementado
- Streaming de tokens.
- Integração real com OpenAI, Gemini, Ollama ou Composio.
- Chamada direta do frontend ao provider real.
- Alterações de Docker Compose.
- Alterações de migrations.
- Mudança de auth global.

## 11. Riscos restantes
- O mock continua sendo um adaptador de UAT; ele não substitui a integração produtiva futura.
- A experiência ainda depende do contrato backend/frontend permanecer sincronizado.
- Futuras fases devem manter a boundary entre mock, fallback local e provider real claramente separada.

## 12. Próxima fase recomendada
M3B_RAG_MCP_MOCK_ADAPTER

## Evidências resumidas
- Mock adapter explícito: sim.
- Fallback local explícito: sim.
- Auth/RBAC preservados: sim.
- Sem provider real nesta fase: sim.
- Sem streaming: sim.

## Resultado das validações
- `git diff --check` → OK
- `PYTHONPATH=backend .venv/bin/python -m pytest` → 293 passed, 22 skipped, 1 warning
- `.venv/bin/python -m ruff check backend tests scripts` → OK
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` → OK
- `cd frontend/itam-platform && PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` → OK
