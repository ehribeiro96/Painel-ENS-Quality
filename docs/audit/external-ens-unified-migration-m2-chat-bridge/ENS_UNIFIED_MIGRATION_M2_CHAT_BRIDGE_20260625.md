# ENS Unified Migration M2 — Chat Bridge Hermes Adapter

## 1. Status
PARTIAL-GO

## 2. Objetivo
Definir o contrato seguro de Chat Bridge Hermes Adapter para o Painel ENS-Quality/Apoema sem copiar o serviço inteiro, sem reintroduzir frontend legado e sem permitir chamada direta do frontend a Hermes.

## 3. Base M0/M1
- Commit M0: `af184b7`
- Commit M1: `e7841cb`
- Artifact contract status: `M1A_CONTRACT_ONLY`
- Runtime Apoema: porta `5175`, helper `scripts/dev-apoema-vite.sh`, proxy `http://[::1]:8080`

## 4. Fonte externa analisada
- CHAT_BRIDGE_EXTERNAL_ROOT: `/tmp/ens-unificado-analysis/projeto-ens-unificado-main/services/chat-bridge`
- Arquivos principais: `src/server.js`, `src/hermes-events.js`, `src/hermes-payloads.js`, `src/hermes-state.js`, `src/artifacts.js`, `src/attachments.js`, `src/hermes-sessions.js`, `test/hermes-events.test.js`, `test/artifacts.test.js`, `test/server-runtime-scope.test.js`
- Endpoints encontrados: `/health`, `POST /api/artifacts/{artifact_id}/access-link`, `POST /api/chat/session/delete`, `POST /api/chat/runs`, `POST /api/chat/stream`, `GET /api/chat/runs/{run_id}`, `GET /api/chat/runs/{run_id}/events`

## 5. Decisão da fase
- M2A_CONTRACT_ONLY
- Justificativa: M1 continua em contract-only, o chat bridge externo depende de attachments/artifacts e de streaming/SSE, e o backend atual já possui um AI chat separado que não deve ser acoplado diretamente ao runtime Hermes. O resultado mais seguro é fechar o contrato e adiar qualquer adapter executável até o Artifact Server sair do estado contratual.

## 6. Contrato externo
O serviço externo é um bridge HTTP/streaming que cria runs, reusa sessões Hermes, normaliza eventos SSE, lê anexos do storage e importa arquivos para artifact storage quando configurado.

## 7. Eventos externos
- `run.created`
- `message.delta`
- `assistant.delta`
- `response.output_text.delta`
- `message.completed`
- `assistant.completed`
- `run.completed`
- `response.completed`
- `run.failed`
- `response.failed`
- `error`
- `status`
- `tool.completed`
- `done`

## 8. Contrato alvo
- `POST /api/v1/ai-chat/conversations`
- `GET /api/v1/ai-chat/conversations`
- `GET /api/v1/ai-chat/conversations/{conversation_id}`
- `POST /api/v1/ai-chat/runs`
- `GET /api/v1/ai-chat/runs/{run_id}`
- `GET /api/v1/ai-chat/runs/{run_id}/events`
- `POST /api/v1/ai-chat/runs/{run_id}/cancel`
- `POST /api/v1/ai-chat/runs/{run_id}/attachments`
- `GET /api/v1/ai-chat/providers`

## 9. Eventos alvo
- `run.created`
- `run.started`
- `message.delta`
- `message.completed`
- `tool.call.started`
- `tool.call.delta`
- `tool.call.completed`
- `artifact.created`
- `artifact.updated`
- `run.completed`
- `run.failed`
- `run.cancelled`
- `error`
- `heartbeat`

## 10. Estado/sessões/runs
A bridge externa persiste o vínculo entre sessão do chat, estado Hermes e run atual, com ownership por usuário. O contrato alvo mantém essa separação: conversation ownership, run ownership, session binding e replay com cursor.

## 11. Integração com Artifact Contract M1
A integração é conceitualmente definida, mas operacionalmente parcial porque o Artifact Server ainda está em contract-only. Qualquer upload, download, delete ou signed-link minting continua bloqueado até a implementação segura do M1.

## 12. Segurança: auth/RBAC/audit/rate limit
- AUTH_REQUIRED: sim no contrato alvo
- RBAC_REQUIRED: sim, especialmente em mutate/cancel/attachment flows
- AUDIT_LOG_REQUIRED: sim
- RATE_LIMIT_REQUIRED: sim
- NO_DIRECT_FRONTEND_PROVIDER_CALL: sim
- SERVER_SIDE_PROVIDER_KEYS_ONLY: sim

## 13. Provider isolation
O contrato reforça isolamento de provider no backend: o frontend só consome `/api/v1`, e o backend decide Hermes/provider/model/timeout/routing.

## 14. Streaming/cancelamento/timeout
- Streaming/SSE definido: sim
- Fallback não-streaming definido: sim
- Cancelamento definido: sim
- Timeout definido: sim
- Heartbeat definido: sim

## 15. O que foi implementado
- inventário do chat bridge externo
- mapa de endpoints
- mapa de eventos
- mapa de envs
- mapa de controles de segurança
- mapa de dependências com Artifact M1
- contrato alvo backend-owned
- contrato de eventos
- contrato de estado/sessão
- contrato de integração com Artifact
- teste estático de contrato documental

## 16. O que NÃO foi implementado
- backend Chat Bridge adapter
- frontend Apoema
- Docker/Compose changes
- copy direta do services/chat-bridge
- backend changes de ai-chat nesta fase
- migration de storage/artifacts

## 17. Validações
- `git diff --check`: PASS
- `PYTHONPATH=backend .venv/bin/python -m pytest`: PASS (272 passed, 22 skipped)
- `.venv/bin/python -m ruff check backend tests scripts`: PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: PASS
- `cd frontend/itam-platform && PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`: PASS
- Secret scan on M2 docs/test: PASS (no matches)

## 18. Limitações
- M1 ainda está em contract-only.
- Streaming externo depende de sessões Hermes e de parsing SSE/transient state.
- Artefatos e anexos continuam bloqueados por dependência da fase M1.
- O runtime atual já possui AI Chat próprio; este trabalho não tenta substituí-lo.

## 19. Próxima fase recomendada
`M3_RAG_MCP_EXTERNAL_SERVICE`
