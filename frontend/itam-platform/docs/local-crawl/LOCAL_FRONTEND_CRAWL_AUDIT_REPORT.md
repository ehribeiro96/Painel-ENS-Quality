# Local Frontend Crawl Audit — HermesOps Sentinel

## 1. Resumo executivo
- Status: GO técnico local com ressalvas
- GO/NO-GO: GO técnico local com ressalvas
- Frontend URL: http://127.0.0.1:5173 / http://127.0.0.1:8000
- Backend URL: http://127.0.0.1:8000
- Rotas auditadas: /login, /, /ai-chat, /docs, /openapi.json, /api/v1/auth/login, /api/v1/auth/refresh, /api/v1/ai-chat/conversations, /api/v1/ai-chat/conversations/{conversation_id}/messages
- Resultado final: login real funciona em 5173 e 8000; AI Chat deixou de retornar 404; provider local permanece mock.

## 2. Fase 1 — Correção funcional local
Correções:
- Frontend dev 5173 passou a resolver `/api/v1` corretamente contra backend 8000 via Vite proxy.
- Login real validado em 5173 e 8000.
- Investigado e corrigido o 404 do AI Chat no runtime local do backend.
- OpenAPI conferido e contém auth/login/refresh e os endpoints reais de AI Chat.
- Crawl mínimo reexecutado em login, home e AI Chat.

Limitações:
- Provider de IA pode exigir configuração separada para sair do modo mock.
- Fluxos de importação/macro ainda exigem smoke HML real com dados sintéticos.
- O AI Chat local está operacional com provider mock; provider externo não foi habilitado nesta fase.

## 3. Correções aplicadas
1. Vite dev proxy
   - Arquivo: `frontend/itam-platform/vite.config.ts`
   - Mudança: proxy de `/api/v1` para `http://127.0.0.1:8000`.
   - Efeito: chamadas relativas em 5173 deixam de bater no próprio Vite.

2. Backend AI Chat local
   - Arquivo: `backend/app/core/config/settings.py`
   - Mudança: quando `environment == 'local'`, `enable_ai_chat` é habilitado no runtime local.
   - Efeito: o backend deixa de responder `404 ai_chat_disabled` para as rotas do módulo local.

## 4. Validação funcional
- Login em 5173: OK
- Refresh em 5173: OK
- AI Chat em 8000: OK
- AI Chat em 5173: OK via proxy
- OpenAPI: OK
- Envio de mensagem sintética: OK

## 5. Evidências relevantes
- `GET /api/v1/auth/refresh` em 5173: 200
- `POST /api/v1/auth/login` em 5173: 200
- `GET /api/v1/ai-chat/health`: 200
- `GET /api/v1/ai-chat/conversations`: 200
- `POST /api/v1/ai-chat/conversations/{conversation_id}/messages`: 201
- Console errors: 0
- JS errors: 0
- Network errors: 0

## 6. Arquivos e artefatos
- Alterações de código: `frontend/itam-platform/vite.config.ts`, `backend/app/core/config/settings.py`
- Relatórios atualizados: `frontend/itam-platform/docs/local-crawl/LOCAL_FRONTEND_CRAWL_AUDIT_REPORT.md`, `frontend/itam-platform/docs/local-crawl/LOCAL_FRONTEND_CRAWL_FINDINGS.json`, `frontend/itam-platform/docs/local-crawl/LOCAL_FRONTEND_IMPROVEMENT_PLAN.md`
- Crawl after: `frontend/itam-platform/docs/local-crawl/fase1-after/`

## 7. Conclusão
GO técnico local com ressalvas. O ambiente agora entrega login real em 5173 e 8000 e o AI Chat não retorna mais 404 no runtime local.
