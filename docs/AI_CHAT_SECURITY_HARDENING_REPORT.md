# AI Chat Security Hardening Report

Data: 2026-06-05
Projeto: Painel ENS-Quality
Escopo: hardening operacional do IA Chat antes de liberar para usuário final.

## Decisão executiva

Status: GO para teste local controlado com chave real.

Condição de GO:

- Usar apenas ambiente local/UAT controlado.
- Definir explicitamente ENABLE_AI_CHAT=true para backend e frontend build/runtime.
- Definir AI_PROVIDER=openai apenas no ambiente controlado.
- Definir OPENAI_API_KEY somente por variável de ambiente ou secret manager.
- Não reutilizar prompts reais com PII sem validação humana prévia.
- Monitorar respostas, timeouts, erros 502/503 e rate limit antes de qualquer ampliação.

## Mudanças implementadas

### 1. Feature flag padrão

Foi adicionada a flag operacional:

```env
ENABLE_AI_CHAT=false
```

Default no backend: false.

Comportamento:

- Quando false, os endpoints operacionais do IA Chat retornam `404 ai_chat_disabled`.
- O menu lateral do frontend esconde `IA Chat` por padrão.
- Para exibir o menu em build Vite, o frontend lê `ENABLE_AI_CHAT=true`.
- O `vite.config.ts` foi configurado com `envPrefix: ["VITE_", "ENABLE_"]` para permitir essa flag sem expor segredos.

### 2. Proteção por auth/RBAC

Todos os endpoints `/api/v1/ai-chat/*`, incluindo healthcheck, passam por dependência RBAC com os papéis já existentes:

- ADMIN
- TECHNICIAN
- MANAGER
- VIEWER

A proteção segue o modelo existente do projeto e não adiciona permissões para endpoints mutáveis fora do domínio de chat.

### 3. Aviso visual obrigatório

A página do IA Chat agora exibe:

> A IA não executa ações no sistema. Use apenas para apoio textual.

Esse aviso reforça que o chat é copiloto textual e não executa ações operacionais.

### 4. Metadados seguros

As mensagens registram metadados operacionais seguros no campo `metadata` já existente:

- `provider`
- `model`
- `input_chars`
- `output_chars`
- `status`
- `error_type`, quando houver erro sanitizado

Não são registrados nesses metadados:

- API key
- headers de autorização
- payload bruto da OpenAI
- prompt completo
- conteúdo completo de mensagens em audit_logs

Observação: o conteúdo da conversa continua salvo em `ai_chat_messages.content`, pois esse é o histórico funcional do próprio chat. A restrição aplicada foi não duplicar prompt completo em `audit_logs` ou metadados.

### 5. Segredos

`OPENAI_API_KEY` continua consumida exclusivamente via configuração de ambiente.

O healthcheck não retorna segredo. Para OpenAI sem chave, retorna apenas:

```json
{
  "enabled": true,
  "provider": "openai",
  "configured": false,
  "status": "configuration_error",
  "detail": "openai_api_key_missing"
}
```

### 6. Limites operacionais

Foram mantidos/confirmados os limites configuráveis:

```env
AI_MAX_INPUT_CHARS=12000
AI_MAX_OUTPUT_TOKENS=1000
AI_TIMEOUT_SECONDS=30
```

Foi adicionado também:

```env
AI_CHAT_RATE_LIMIT_PER_MINUTE=20
```

### 7. Rate limit simples por usuário

Foi implementado rate limit em memória por usuário autenticado para envio de mensagens/criação de conversa com mensagem inicial.

Comportamento:

- Janela: 60 segundos.
- Default: 20 mensagens/minuto/usuário.
- Excesso retorna `429 ai_chat_rate_limit_exceeded`.

Limitação conhecida:

- Por ser in-memory, o contador é por processo/container. Para produção multi-réplica, migrar o contador para Redis antes de liberar uso amplo.

### 8. Escopo de ação da IA

Nenhuma tool foi adicionada.

Nenhuma permissão foi adicionada para alterar:

- ativos;
- usuários;
- importações;
- assinaturas;
- macros;
- movimentações.

O system prompt continua bloqueando ações operacionais e orientando resposta apenas textual.

## Arquivos principais alterados

Backend:

- `backend/app/core/config/settings.py`
- `backend/app/api/v1/routes/ai_chat.py`
- `backend/app/domains/ai_chat/service.py`
- `backend/app/domains/ai_chat/repository.py`

Frontend:

- `frontend/itam-platform/src/lib/features.ts`
- `frontend/itam-platform/src/vite-env.d.ts`
- `frontend/itam-platform/vite.config.ts`
- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/pages/AiChatPage.tsx`
- `frontend/itam-platform/src/lib/api.ts`
- `frontend/itam-platform/src/lib/types.ts`

Testes:

- `tests/test_ai_chat_hardening.py`
- `tests/test_ai_chat_api.py`

Config exemplo:

- `.env.example`

## Validações executadas

### Testes backend/unitários

Comando:

```bash
PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v
```

Resultado:

```text
Ran 70 tests in 0.389s
OK (skipped=8)
```

Coberturas específicas incluídas:

- mock continua funcionando;
- OpenAI sem chave retorna `configuration_error`;
- OpenAI com HTTP mockado retorna resposta;
- endpoints protegidos por RBAC;
- feature flag bloqueia o chat quando false;
- menu usa feature flag e fica oculto por padrão;
- aviso visual obrigatório existe;
- metadados seguros são registrados;
- API key e prompt completo não aparecem nos metadados;
- erro de provider registra `error_type` sanitizado;
- rate limit por usuário retorna 429.

### Ruff

Comando:

```bash
.venv/bin/python -m ruff check backend tests
```

Resultado:

```text
All checks passed!
```

### Build frontend

Comandos:

```bash
cd frontend/itam-platform
npm run build
ENABLE_AI_CHAT=true npm run build
ENABLE_AI_CHAT=false npm run build
```

Resultado final com `ENABLE_AI_CHAT=false`:

```text
✓ built in 1.69s
```

A validação com `ENABLE_AI_CHAT=true` também compilou com sucesso, confirmando que a flag é aceita pelo build Vite.

### Docker Compose

Comando:

```bash
docker compose config >/tmp/painel-compose-config.out && echo OK
```

Resultado:

```text
OK
```

## Configuração recomendada para teste local controlado

```env
ENABLE_AI_CHAT=true
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=<definir apenas no ambiente local/controlado>
AI_TIMEOUT_SECONDS=30
AI_MAX_INPUT_CHARS=12000
AI_MAX_OUTPUT_TOKENS=1000
AI_CHAT_RATE_LIMIT_PER_MINUTE=20
```

Para o frontend build com Vite:

```env
ENABLE_AI_CHAT=true
```

## Riscos residuais

1. Rate limit em memória não é suficiente para ambiente horizontal/multi-container.
2. Histórico funcional do chat salva conteúdo em `ai_chat_messages.content`; usuários devem ser orientados a não enviar PII/segredos.
3. A chamada externa à OpenAI deve ser usada inicialmente apenas em ambiente controlado.
4. Logs de infraestrutura/reverse proxy devem ser revisados para garantir que bodies HTTP não sejam capturados fora da aplicação.

## Recomendação final

GO para teste local controlado com chave real.

Não liberar para uso amplo antes de:

- validar comportamento com uma chave real em ambiente local/UAT;
- revisar logs do container/reverse proxy;
- confirmar que `ENABLE_AI_CHAT=false` permanece como default em ambientes não autorizados;
- considerar Redis para rate limit em produção multi-réplica.
