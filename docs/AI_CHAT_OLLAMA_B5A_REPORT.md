# AI Chat Ollama B5-A Report

## Auditoria inicial

Branch inicial: `main...origin/main [ahead 1]`.

Stage inicial: vazio (`git diff --cached --name-status` sem saída). Worktree inicial sujo, com alterações preexistentes em backend, frontend, testes e muitos arquivos não rastreados. A execução B5-A prosseguiu seletivamente sem `git add`, sem commit, sem reset, sem checkout e sem limpeza.

Backend local estava ativo em `http://127.0.0.1:8000`: `/health` respondeu HTTP 200. Dependências Docker nativas WSL estavam ativas para Postgres e Redis. `/api/v1/auth/refresh` sem sessão respondeu HTTP 404 controlado com headers de segurança, sem timeout.

## Arquivos encontrados

Arquivos AI Chat relevantes encontrados e lidos:

- `backend/app/api/v1/routes/ai_chat.py`
- `backend/app/domains/ai_chat/providers.py`
- `backend/app/domains/ai_chat/service.py`
- `backend/app/domains/ai_chat/schemas.py`
- `backend/app/domains/ai_chat/rate_limit.py`
- `tests/test_ai_chat_api.py`
- `tests/test_ai_chat_hardening.py`
- `tests/test_ai_chat_provider_mock.py`
- `tests/test_ai_chat_rate_limit.py`
- `tests/test_security_headers.py`
- `frontend/itam-platform/src/pages/AiChatPage.tsx`
- `frontend/itam-platform/src/lib/api.ts`

Docs B5-A não existiam antes desta boundary:

- `docs/AI_CHAT_OLLAMA_B5A_REPORT.md`
- `docs/AI_CHAT_OLLAMA_LOCAL_RUNBOOK.md`

Docs de auditoria existentes lidos:

- `docs/audit/README.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`

## Fluxo atual frontend -> backend

O frontend `AiChatPage.tsx` chama apenas o client `frontend/itam-platform/src/lib/api.ts`. O client usa `API_BASE` padrão `/api/v1` e as rotas:

- `GET /ai-chat/health`
- `GET /ai-chat/conversations`
- `POST /ai-chat/conversations`
- `GET /ai-chat/conversations/{id}`
- `POST /ai-chat/conversations/{id}/messages`

Não há chamada direta do frontend para Ollama, OpenAI ou Gemini.

## Endpoint backend atual

O backend expõe `APIRouter(prefix="/ai-chat")` em `backend/app/api/v1/routes/ai_chat.py`. Todas as rotas de AI Chat são protegidas por RBAC via `require_role(Role.ADMIN, Role.TECHNICIAN, Role.MANAGER, Role.VIEWER)`.

O envio de mensagem preserva:

- feature flag `enable_ai_chat`;
- validação de tamanho;
- rate limit antes de chamar o provider;
- commit/rollback;
- mapeamento sanitizado de erro de configuração para HTTP 503;
- mapeamento sanitizado de erro de provider para HTTP 502.

## Provider atual

`backend/app/domains/ai_chat/providers.py` contém:

- `MockAiProvider`, offline e determinístico;
- `GeminiProvider`, via `urllib.request` encapsulado;
- `OpenAIProvider`, via `urllib.request` encapsulado;
- `build_ai_provider(settings)` com seleção por `ai_provider`;
- `get_ai_provider_health(settings)`.

`AiChatService` monta `SYSTEM_PROMPT` em português brasileiro e persiste mensagens `user` e `assistant` no PostgreSQL via repositório.

## Rate limit/security hardening existente

`backend/app/domains/ai_chat/rate_limit.py` preserva o hardening B2:

- rate limit por usuário com chave hash SHA-256;
- Redis sem `eval`, usando `SET nx/ex` e `INCR`;
- fallback local somente em ambiente `local`;
- erro controlado `ai_chat_rate_limit_unavailable` em ambientes não locais;
- erro controlado `ai_chat_rate_limit_exceeded` com HTTP 429.

Headers de segurança são validados em `tests/test_security_headers.py`.

## Lacunas para Ollama

Lacunas antes da implementação:

- `AI_PROVIDER=ollama` ainda não é suportado por `build_ai_provider`.
- Não há provider backend para `POST http://127.0.0.1:11434/api/chat`.
- Settings não possuem `OLLAMA_BASE_URL`, `OLLAMA_MODEL` ou `OLLAMA_TIMEOUT_SECONDS`.
- Testes dedicados para payload, timeout, conexão recusada, modelo ausente e parse inválido do Ollama ainda não existem.
- Documentação/runbook B5-A ainda não existiam.

## Plano de alteração mínima

1. Validar Ollama local e detectar modelo disponível sem baixar modelos.
2. Adicionar settings seguros para Ollama com default localhost.
3. Implementar `OllamaProvider` no domínio AI Chat, sem aceitar URL do frontend.
4. Integrar `AI_PROVIDER=ollama` em `build_ai_provider` e `get_ai_provider_health`.
5. Adicionar testes dedicados offline com transporte fake.
6. Preservar rate limit B2 e contrato frontend existente.
7. Atualizar `.env.example` apenas com placeholders localhost/modelo, sem segredo.
8. Atualizar docs e runbook.

## Validação Ollama local antes de codar

Ollama local foi validado sem baixar modelos:

- `command -v ollama`: `/usr/local/bin/ollama`
- `ollama --version`: `0.30.7`
- `/api/tags`: respondeu JSON com modelos locais.
- Modelo escolhido pela ordem de preferência B5-A: `qwen2.5-coder:7b`.
- Endpoint local: `http://127.0.0.1:11434/api/chat`.
- Teste direto com mensagem `Responda apenas OK.` respondeu JSON com `message.content = "OK."`.

Modelos disponíveis relevantes no momento da auditoria:

- `qwen2.5-coder:7b`
- `qwen2.5-coder:3b-hermes64k`
- `qwen2.5-coder:3b-hermes48k`
- `qwen2.5-coder:3b`
- `qwen2.5-coder:1.5b-hermes64k`
- `qwen2.5-coder:1.5b`
- `qwen2.5-coder:0.5b-hermes64k-fast`
- `qwen2.5-coder:0.5b-hermes64k`
- `qwen2.5-coder:0.5b`

## Diagnóstico antes de editar

1. Provider atual do AI Chat: `mock`, `gemini` e `openai` em `backend/app/domains/ai_chat/providers.py`.
2. Contrato atual do endpoint backend: rotas REST autenticadas sob `/api/v1/ai-chat`, retornando `AiChatConversationRead` ou `AiChatConversationDetail` com mensagens persistidas. Não há endpoint simples `{message, provider, model}` separado.
3. Contrato esperado pelo frontend: `AiChatPage.tsx` usa `api.aiChatHealth`, `api.aiChatConversations`, `api.aiChatCreateConversation`, `api.aiChatConversation` e `api.aiChatSendMessage`. A resposta esperada para envio é `AiChatConversationDetail`.
4. Inserção mínima do provider Ollama: adicionar `OllamaProvider` no domínio AI Chat e plugar em `build_ai_provider(settings)` quando `AI_PROVIDER=ollama`.
5. Arquivos planejados para alteração: `backend/app/core/config/settings.py`, `backend/app/domains/ai_chat/providers.py`, testes dedicados AI Chat, `.env.example` com placeholders, e docs B5-A/runbook/audit. Frontend não deve ser alterado se o contrato atual permanecer estável.
6. Testes necessários: provider Ollama, rotas/service AI Chat existentes, hardening B2, rate limit, security headers, compileall, ruff e build frontend.
7. Ollama offline: mapear timeout/conexão recusada para `AiProviderRequestError` com código sanitizado (`ollama_timeout` ou `ollama_request_failed`) e o endpoint deve responder erro controlado já existente via HTTP 502.
8. Modelo ausente: mapear HTTP 404/erro equivalente do Ollama para `provider_http_404` ou `ollama_model_unavailable`, sem baixar modelo automaticamente.
9. Stack trace/secrets: provider não loga payload completo, headers sensíveis ou stack trace para o frontend; rota mantém `_provider_error_detail` com códigos sanitizados.
10. Rate limit: não tocar em `backend/app/domains/ai_chat/rate_limit.py` nem no ponto de chamada `_apply_rate_limit` antes de provider.

## Resumo executivo

B5-A implementou o provider Ollama local no backend FastAPI como proxy seguro. O frontend continua chamando somente `/api/v1/ai-chat/*`. O backend seleciona Ollama apenas por configuração de runtime (`AI_CHAT_PROVIDER=ollama` ou alias compatível `AI_PROVIDER=ollama`) e chama `http://127.0.0.1:11434/api/chat` com `stream=false`.

Status técnico desta execução: provider implementado, testes dedicados passam, teste direto do Ollama passa, teste equivalente via rota backend passa, compileall passa, Ruff passa, pytest dedicado passa e frontend build passa. Sem commit e sem stage.

## Escopo B5-A

Incluído:

- Provider Ollama local no domínio AI Chat.
- Settings backend para `OLLAMA_BASE_URL`, `OLLAMA_MODEL` e `OLLAMA_TIMEOUT_SECONDS`.
- Testes dedicados do provider e contrato de rota/service.
- `.env.example` com placeholders localhost/modelo.
- Documentação e runbook B5-A.

Fora do escopo preservado:

- Docker setup.
- Migrations.
- Frontend visual.
- Electron/Desktop Hermes.
- Imports/staging.
- Macros/movements.
- Alteração de runtime/modelos Ollama.
- Download automático de modelos.

## Arquitetura antes

```text
Frontend AI Chat
  -> Backend FastAPI /api/v1/ai-chat
    -> Provider mock/gemini/openai
```

## Arquitetura depois

```text
Frontend AI Chat
  -> Backend FastAPI /api/v1/ai-chat
    -> Provider Ollama local
      -> http://127.0.0.1:11434/api/chat
        -> resposta para backend
          -> resposta para frontend
```

## Provider Ollama

Implementado em `backend/app/domains/ai_chat/providers.py` como `OllamaProvider`.

Características:

- Usa `POST /api/chat`.
- Envia `stream=false`.
- Usa mensagens `role/content`.
- Usa `urllib.request` por meio do helper assíncrono já existente; não adiciona dependência nova.
- Valida que `OLLAMA_BASE_URL` é local (`http` e host `127.0.0.1`, `localhost` ou `::1`).
- Não aceita URL vinda do frontend.
- Não cria endpoint com URL arbitrária.
- Não expõe `OLLAMA_BASE_URL` no health retornado ao frontend.

## Modelo detectado/usado

Modelo detectado e usado: `qwen2.5-coder:7b`.

Motivo: foi o primeiro modelo disponível na ordem de preferência B5-A.

## Segurança

- Frontend continua chamando somente backend.
- Provider não aceita URL pelo request do usuário.
- Health do provider não retorna `OLLAMA_BASE_URL`.
- `OLLAMA_BASE_URL` é validado para loopback.
- Erros do provider são códigos sanitizados.
- Nenhum segredo real foi lido ou impresso.
- `.env` real não foi lido nem alterado.
- `.env.example` contém apenas placeholders/valores localhost sem segredo.

## Rate limit preservado

Sim. `backend/app/domains/ai_chat/rate_limit.py` não foi alterado. As rotas continuam chamando `_apply_rate_limit(current_user.id)` antes de enviar mensagem ao provider.

## Erros tratados

- Timeout: `ollama_timeout`.
- Conexão recusada/falha operacional: `ollama_request_failed`.
- Modelo ausente/HTTP 404: `ollama_model_unavailable`.
- Resposta sem `message.content`: `ollama_invalid_response` ou `ollama_empty_response`.
- Base URL não-local ou com path: erro de configuração `ollama_base_url_must_be_localhost` / `ollama_base_url_must_not_include_path`.

## Arquivos alterados

Arquivos alterados por esta boundary:

- `backend/app/core/config/settings.py`
- `backend/app/domains/ai_chat/providers.py`
- `tests/test_ai_chat_ollama_provider.py`
- `.env.example`
- `docs/AI_CHAT_OLLAMA_B5A_REPORT.md`
- `docs/AI_CHAT_OLLAMA_LOCAL_RUNBOOK.md`
- `docs/audit/README.md`
- `docs/audit/NEXT_BOUNDARY_DECISION.md`

## Testes executados

- `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests`: PASS.
- `PYTHONPATH=backend timeout 120 .venv/bin/python -m ruff check ...`: PASS.
- `PYTHONPATH=backend timeout 240 .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_ai_chat_rate_limit.py tests/test_security_headers.py tests/test_ai_chat_ollama_provider.py -q -o addopts=''`: PASS, `43 passed, 1 warning`.
- `npm run build` em `frontend/itam-platform`: PASS.

## Teste direto Ollama

`curl http://127.0.0.1:11434/api/chat` com `model=qwen2.5-coder:7b`, `stream=false` e prompt `Responda apenas OK.` retornou JSON com `message.content = "OK."`.

## Teste via backend

Teste equivalente via rota backend Python usando `ai_chat.create_conversation` e `ai_chat.send_message`, com `AI_PROVIDER=ollama`, retornou:

- provider: `ollama`
- model: `qwen2.5-coder:7b`
- roles: `['user', 'assistant']`
- assistant content: `OK via Ollama`

O teste HTTP real do endpoint autenticado ficou coberto por testes automatizados/rota porque as rotas exigem autenticação/RBAC e não foram usadas credenciais reais nesta boundary.

## Frontend build

Build executado com Node `v22.22.3` e npm `10.9.8`:

```text
npm run build: PASS
```

Nenhum arquivo frontend foi alterado nesta boundary.

## Scanner redigido

Scanner em arquivos alterados encontrou apenas:

- nomes de variáveis esperados (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`);
- placeholders em `.env.example`;
- nomes de variáveis/códigos em settings/providers/testes;
- valores localhost permitidos.

Nenhum segredo real foi identificado ou impresso.

## Limitações

- O teste HTTP autenticado real pelo browser/API externa não foi executado porque exigiria sessão/token real; foi substituído por teste automatizado equivalente da rota/service com provider Ollama real.
- A qualidade do modelo depende do modelo local presente no Ollama; nenhum modelo foi baixado ou alterado.
- `OLLAMA_BASE_URL` é deliberadamente restrito a loopback nesta implementação.

## Próximo passo recomendado

B5-B foi executada como boundary separada para `ollama-lan` OpenAI-compatible. Resultado registrado em `docs/AI_CHAT_OLLAMA_LAN_B5B_REPORT.md`: implementação/testes/build passaram, mas validação real do host LAN e smoke UI autenticado ficaram pendentes por bloqueio de conectividade/aprovação e sessão autenticada não efetiva.

Próxima boundary sugerida: `B5-C — AI Chat Ollama LAN authenticated runtime validation`, focada somente em validação runtime real contra `/v1/chat/completions` e smoke UI autenticado, sem novas mudanças funcionais se o código B5-B permanecer igual.
