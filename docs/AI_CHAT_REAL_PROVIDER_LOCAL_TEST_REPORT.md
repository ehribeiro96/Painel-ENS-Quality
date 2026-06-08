# AI Chat Real Provider Local Test Report

Data: 2026-06-05
Projeto: Painel ENS-Quality
Escopo: teste local controlado do IA Chat com provider OpenAI real.

## Resumo executivo

Status final: NO-GO para uso controlado interno nesta execução.

Motivo: o backend foi iniciado em modo `ENABLE_AI_CHAT=true` e `AI_PROVIDER=openai`, mas o health autenticado do IA Chat retornou `configuration_error` com `openai_api_key_missing`. Conforme regra da validação, a execução foi interrompida antes de enviar qualquer mensagem ao provider.

Nenhum Apply foi executado. Nenhum `docker compose down -v` foi executado. Nenhum dado real de colaborador, patrimônio, Lansweeper, AD ou histórico de movimentação foi usado. Nenhuma tool/RAG/action foi habilitada.

Após a falha de configuração local, a stack foi restaurada para a configuração padrão sem override de IA no container.

## Configuração usada sem segredo

Pré-check executado em:

```text
/home/estevaoqualityadm/projects/Painel-ENS-Quality
```

Stack UAT inicial:

```text
itam_uat-app-1: up/healthy
itam_uat-postgres-1: up/healthy
itam_uat-redis-1: up/healthy
```

Health geral inicial:

```text
/health: ok
/health/ready: ok
migration: up_to_date, current_revision=0006_ai_chat, head_revision=0006_ai_chat
```

Arquivos `.env*` foram listados apenas por nome. Conteúdo não foi impresso.

Variáveis pretendidas para o teste:

```text
ENABLE_AI_CHAT=true
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=<não impresso>
AI_TIMEOUT_SECONDS=30
AI_MAX_INPUT_CHARS=12000
AI_MAX_OUTPUT_TOKENS=1000
AI_CHAT_RATE_LIMIT_PER_MINUTE=20
```

Resultado efetivo do health: `OPENAI_API_KEY` não estava disponível para o app, logo o provider real não pôde ser exercitado.

## Provider

Provider configurado na tentativa controlada:

```text
openai
```

Provider efetivamente validado por health:

```text
provider=openai
configured=false
status=configuration_error
detail=openai_api_key_missing
```

## Model

Modelo configurado na tentativa controlada:

```text
gpt-4o-mini
```

O modelo não foi exercitado porque a execução parou no health com chave ausente.

## Health result

Arquivo de evidência:

```text
uat_evidence/ai_chat_real_provider/ai_chat_health.json
```

Resultado sanitizado:

```json
{
  "http_status": 200,
  "provider": "openai",
  "configured": false,
  "status": "configuration_error",
  "model": null,
  "detail": "openai_api_key_missing"
}
```

Health sem autenticação também foi validado:

```text
GET /api/v1/ai-chat/health sem token -> 401
```

Evidência:

```text
uat_evidence/ai_chat_real_provider/ai_chat_health_unauth.json
```

## Teste de conversa

Não executado.

Motivo: o health autenticado retornou `configuration_error/openai_api_key_missing`. A instrução da fase 4 determinava interromper nesse caso e registrar falha de configuração local, sem tentar imprimir chave.

Mensagem segura planejada, mas não enviada:

```text
Explique em uma frase o que é inventário de ativos de TI.
```

Não houve chamada real à OpenAI nesta execução.

## Teste de rate limit

Não executado.

Motivo: a validação foi interrompida antes da fase de envio de mensagens porque o provider OpenAI não estava configurado com chave no app.

O rate limit continua coberto por testes automatizados da etapa de hardening anterior, mas não foi exercitado nesta execução real-provider.

## Teste com feature flag off

A stack foi restaurada para a configuração padrão após a falha de configuração local:

```text
docker compose -p itam_uat up -d
```

Resultado:

```text
/health: ok
app/postgres/redis em execução
sem variáveis ENABLE_AI_CHAT, AI_PROVIDER ou OPENAI_API_KEY presentes no container restaurado
```

Evidência:

```text
uat_evidence/ai_chat_real_provider/restored_default_stack.txt
```

Validação completa de menu oculto e endpoints `404 ai_chat_disabled` não foi executada nesta rodada porque a execução já havia sido interrompida por falha de configuração local do provider real.

Observação de release: o Dockerfile atual executa `npm run build` no stage `frontend-builder`. Para que `ENABLE_AI_CHAT=true` afete o bundle Vite dentro do container, o build precisa receber essa variável no stage de build, por exemplo via `ARG/ENV` ou build args no Compose. Nesta execução, isso não foi corrigido porque a missão foi interrompida pela ausência de chave real no app.

## Evidência de que API key não foi logada

Logs do app foram capturados temporariamente e escaneados sem imprimir conteúdo.

Arquivo de scan:

```text
uat_evidence/ai_chat_real_provider/app_logs_secret_scan.json
```

Resultado:

```json
{
  "contains_OPENAI_API_KEY_literal": false,
  "contains_openai_key_prefix": false,
  "contains_bearer_token": false,
  "contains_password_word": true,
  "contains_safe_prompt": false,
  "line_count": 27
}
```

Como a varredura encontrou a palavra `password` nos logs, o arquivo bruto de log foi apagado imediatamente por segurança:

```text
uat_evidence/ai_chat_real_provider/app_logs_tail_sanitized.txt: removido
```

A varredura não encontrou literal `OPENAI_API_KEY`, prefixo de chave OpenAI, bearer token nem prompt seguro.

## Evidência de que prompt completo não foi para audit_logs/metadados

Não aplicável nesta execução porque nenhuma mensagem foi enviada ao IA Chat real. A validação foi interrompida no health devido a `openai_api_key_missing`.

## Validações executadas

Executadas:

```text
pwd

docker compose -p itam_uat ps

curl -sS http://127.0.0.1:8080/health || true
curl -sS http://127.0.0.1:8080/health/ready || true

git status --short 2>/dev/null || true
find . -maxdepth 2 -name ".env" -o -name ".env.local" -o -name ".env.*"

ENABLE_AI_CHAT=true AI_PROVIDER=openai ... docker compose -p itam_uat -f docker-compose.yml -f /tmp/painel-ai-chat-local-override.yml up --build -d

POST /api/v1/auth/login
GET /api/v1/ai-chat/health com token
GET /api/v1/ai-chat/health sem token

docker compose -p itam_uat logs app --no-color --tail=300 > evidência temporária
scan de segredo nos logs

docker compose -p itam_uat up -d
```

Não executadas por interrupção obrigatória:

```text
mensagem real para OpenAI
rate limit real por usuário
feature flag off completa com páginas/módulos
unittest discover completo
ruff completo
builds frontend true/false
docker compose config final
```

## Riscos restantes

1. Provider real ainda não validado com chave real nesta execução.
2. Menu Vite em container pode não respeitar `ENABLE_AI_CHAT=true` via `docker compose up --build` enquanto o Dockerfile não passar a variável para o stage `frontend-builder`.
3. Logs brutos contêm a palavra `password`; mesmo sem chave OpenAI detectada, a evidência bruta foi apagada e recomenda-se revisar a origem dessa linha antes de liberar coleta de logs como evidência permanente.
4. Rate limit real por usuário não foi exercitado nesta rodada.
5. Validação de ausência de prompt completo em audit/metadados não foi executada nesta rodada porque nenhuma mensagem foi enviada.

## Reexecução solicitada após seleção "4"

Após a seleção `4`, foi feita nova checagem segura antes de reexecutar o roteiro completo.

Evidência:

```text
uat_evidence/ai_chat_real_provider/rerun_precheck_after_user_4.txt
```

Resultado:

```text
OPENAI_API_KEY_AVAILABLE_IN_AGENT_SESSION: no
stack: app/postgres/redis healthy
/health: ok
/health/ready: ok
```

Como a chave ainda não está disponível na sessão do agente, a reexecução completa foi bloqueada antes de qualquer rebuild com provider real. Nenhum segredo foi impresso e nenhuma chamada à OpenAI foi feita.

## Reexecução solicitada agora com `AI_OPENAI_API_KEY`

Foi feita nova reexecução segura em 2026-06-05T11:37:48-03:00, sem imprimir ou persistir segredo.

Evidências sem segredo:

```text
uat_evidence/ai_chat_real_provider/rerun_real_provider_now_safe_evidence.txt
uat_evidence/ai_chat_real_provider/rerun_real_provider_now_summary.json
```

Validações permitidas de sessão do agente:

```text
OPENAI_API_KEY_AVAILABLE_IN_AGENT_SESSION: no
AI_OPENAI_API_KEY_AVAILABLE_IN_AGENT_SESSION: no
AI_OPENAI_API_KEY_LENGTH_ONLY: 0
AI_OPENAI_API_KEY_BRIDGE_IN_MEMORY_USED: no
```

Pré-condições de runtime confirmadas antes de qualquer chamada externa:

```text
stack app/postgres/redis healthy: true
/health ok: true
/health/ready ok: true
```

Decisão desta reexecução: `NO-GO`.

Motivo: `AI_OPENAI_API_KEY` continua ausente na sessão do agente. Conforme regra explícita, o roteiro real provider foi bloqueado antes de qualquer chamada à OpenAI. Nenhuma key foi impressa, gravada em `.env`, gravada em `docker-compose`, logs ou evidências.

## Decisão final

NO-GO.

Critério bloqueante: `AI_OPENAI_API_KEY` não está disponível na sessão atual do agente. A stack local `app/postgres/redis` está healthy e `/health` + `/health/ready` estão ok, mas a ausência da variável exigida impede continuar o roteiro com provider real.

Não houve evidência de vazamento de API key, mas também não houve chamada real bem-sucedida à OpenAI.

## Mudança de decisão técnica: Gemini / Google AI Studio

Reexecução segura em 2026-06-05T11:59:05-03:00, após decisão de não usar OpenAI como provider real do Painel neste teste.

Provider alvo do Painel:

```text
gemini
```

Contrato pretendido para o roteiro real provider, sem segredo persistido:

```text
AI_PROVIDER=gemini
AI_MODEL=gemini-2.0-flash ou modelo Gemini disponível configurado
AI_GEMINI_API_KEY=<presente apenas no ambiente da sessão/container>
AI_TIMEOUT_SECONDS=30
AI_MAX_INPUT_CHARS=12000
AI_MAX_OUTPUT_TOKENS=1000
```

Pré-check seguro da sessão do agente:

```text
AI_PROVIDER: <unset>
AI_MODEL: <unset>
AI_GEMINI_API_KEY_AVAILABLE_IN_AGENT_SESSION: no
AI_GEMINI_API_KEY_LENGTH_ONLY: 0
```

Pré-condições de runtime:

```text
stack app/postgres/redis healthy: true
/health ok: true
/health/ready ok: true
```

Evidência sem segredo:

```text
uat_evidence/ai_chat_real_provider/gemini_precheck_safe_evidence.txt
```

Decisão desta reexecução: `NO-GO`.

Motivo: `AI_GEMINI_API_KEY` está ausente na sessão atual do agente. Conforme regra explícita, o roteiro real provider Gemini foi bloqueado antes de qualquer rebuild, chamada externa ou envio de prompt.

Inspeção de código antes de patch:

```text
AI_PROVIDER aceita gemini: não; o tipo atual aceita apenas mock/openai.
GeminiProvider existe: não.
GeminiProvider implementado: não; precisa ser criado para suportar Gemini.
Provider mock continua padrão seguro: sim; AI_PROVIDER default é mock.
Testes mock continuam sem internet: sim; testes atuais usam mock e HTTP fake para OpenAI.
Chaves no frontend: não foi identificado contrato de chave de provider no frontend; .env.example contém VITE_API_URL apenas para frontend e não contém VITE_AI_*.
```

Plano proposto antes de qualquer patch de suporte Gemini:

1. Arquivos a alterar:
   - `backend/app/core/config/settings.py`
   - `backend/app/domains/ai_chat/providers.py`
   - `tests/test_ai_chat_mvp.py`
   - `.env.example`
   - `docs/AI_CHAT_REAL_PROVIDER_LOCAL_TEST_REPORT.md` apenas para evidências sem segredo.
2. Arquivos a criar: nenhum arquivo de código novo previsto.
3. Dependência necessária: nenhuma dependência nova prevista; usar `urllib.request`, já usado no provider atual.
4. Como testar sem expor segredo:
   - testes unitários com `http_post` fake, verificando endpoint Gemini, payload e metadados sem imprimir headers reais;
   - pré-check imprime somente presença e comprimento da variável, nunca valor;
   - chamada real somente via backend e somente se `AI_GEMINI_API_KEY` existir em ambiente efêmero da sessão/container.
5. Como manter mock como padrão:
   - manter `ai_provider` default `mock`;
   - manter health de mock configurado sem chave;
   - não configurar Gemini em `.env` real nem em `docker-compose.yml`.
6. Como impedir testes com internet/key:
   - não ler `AI_GEMINI_API_KEY` nos testes unitários;
   - injetar `http_post` fake no `GeminiProvider`;
   - validar health de configuração com settings fake contendo chave sentinela não real;
   - não executar rota real provider em testes automatizados.

Confirmação de isolamento: nenhum valor de API key foi impresso, gravado em `.env`, gravado em `docker-compose.yml`, salvo em logs/evidências ou exposto ao frontend. Nenhuma chamada à OpenAI ou Gemini foi feita nesta reexecução.

## Implementação autorizada: Fase 1 Gemini backend mínimo

Implementação executada em 2026-06-05T12:11:28-03:00.

Arquivos alterados:

```text
backend/app/core/config/settings.py
backend/app/domains/ai_chat/providers.py
tests/test_ai_chat_mvp.py
.env.example
```

Evidência sem segredo:

```text
uat_evidence/ai_chat_real_provider/gemini_phase1_backend_support_evidence.txt
```

Resumo técnico:

```text
AI_PROVIDER default permanece mock.
AI_PROVIDER passa a aceitar gemini mantendo compatibilidade openai existente.
settings.ai_gemini_api_key adicionado com default vazio.
GeminiProvider mínimo criado no backend.
GeminiProvider recebe settings e aceita http_post fake/injetável para testes offline.
GeminiProvider usa apenas AI_GEMINI_API_KEY/settings.ai_gemini_api_key.
Endpoint REST generateContent usado via biblioteca padrão, sem SDK externo.
Payload mínimo contents/parts/text implementado.
Streaming não implementado.
Tool calling não implementado.
Testes Gemini usam http_post fake, sem internet e sem chave real.
```

Validações pós-patch:

```text
python -m compileall -q backend/app backend/alembic tests: rc=0
python -m unittest discover -s tests: rc=0, Ran 76 tests, OK, skipped=8
cd frontend/itam-platform && npm run build: rc=0, Vite build concluído
```

Pré-check Gemini pós-patch:

```text
AI_PROVIDER: <unset>
AI_MODEL: <unset>
AI_GEMINI_API_KEY_AVAILABLE_IN_AGENT_SESSION: no
AI_GEMINI_API_KEY_LENGTH_ONLY: 0
stack app/postgres/redis healthy: true
/health: HTTP 200 status=ok
/health/ready: HTTP 200 status=ok
GO_STATUS: NO-GO para chamada real provider, pois a chave está ausente.
```

Confirmação de isolamento: nenhum valor de API key foi impresso, gravado em `.env`, gravado em `docker-compose.yml`, salvo em logs/evidências ou exposto ao frontend. Nenhuma chamada real Gemini foi feita sem key. Nenhuma chamada OpenAI foi feita.

## Próximo passo recomendado

1. Disponibilizar `AI_GEMINI_API_KEY` somente em ambiente efêmero da sessão/container quando o roteiro real provider for reexecutado.
2. Não gravar chave em `.env`, `docker-compose.yml`, frontend, logs ou evidências.
3. Reexecutar pré-check; se a chave estiver presente, iniciar app/container com `AI_PROVIDER=gemini` por mecanismo temporário seguro e chamar o backend do Painel com prompt mínimo.
