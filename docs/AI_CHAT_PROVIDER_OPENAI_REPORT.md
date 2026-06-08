# IA Chat - Provider OpenAI

## Resumo

O IA Chat agora suporta dois providers:

- `AI_PROVIDER=mock` como padrão seguro.
- `AI_PROVIDER=openai` para geração textual real via OpenAI Chat Completions API.

O módulo continua limitado a respostas textuais. A IA não executa ações no sistema, não altera ativos, usuários, importações, assinaturas, movimentações ou macros, e recebe o mesmo prompt de sistema que explicita essas restrições.

## Configuração

Variáveis relevantes:

```env
AI_PROVIDER=mock
AI_MODEL=
OPENAI_API_KEY=
AI_TIMEOUT_SECONDS=30
AI_MAX_INPUT_CHARS=12000
AI_MAX_OUTPUT_TOKENS=1000
```

Para OpenAI:

```env
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=<definir localmente>
```

A chave é lida somente por variável de ambiente. Ela não deve ser commitada, logada ou exibida em respostas de healthcheck.

## Healthcheck

Endpoint:

```http
GET /api/v1/ai-chat/health
```

Resposta mock:

```json
{
  "provider": "mock",
  "configured": true,
  "status": "ok"
}
```

Resposta OpenAI sem chave:

```json
{
  "provider": "openai",
  "configured": false,
  "status": "configuration_error",
  "detail": "openai_api_key_missing"
}
```

Resposta OpenAI configurado:

```json
{
  "provider": "openai",
  "configured": true,
  "status": "ok",
  "model": "gpt-4o-mini"
}
```

## Segurança

- `mock` permanece o padrão.
- `OPENAI_API_KEY` é a única variável de segredo usada pelo provider OpenAI.
- Nenhuma chave é hardcoded.
- Nenhuma chave é retornada no healthcheck.
- Erros HTTP da OpenAI não incluem headers, body de requisição, prompts ou chave.
- O prompt de sistema continua restringindo a IA a texto e exige aprovação humana para qualquer ação operacional.
- O backend persiste apenas mensagens e metadados do provider/model; não executa ações solicitadas pela IA.

## Testes

Cobertura adicionada/atualizada:

- mock continua como padrão.
- `AI_PROVIDER=openai` constrói `OpenAIProvider`.
- OpenAI sem `OPENAI_API_KEY` retorna erro claro de configuração.
- chamada OpenAI é testada com HTTP mockado, sem rede externa.
- healthcheck reporta `provider`, `configured`, `status` e não expõe segredo.
- erro de configuração em envio retorna HTTP 503 amigável.

Comando usado:

```bash
PYTHONPATH=backend .venv/bin/python -m unittest tests.test_ai_chat_mvp tests.test_ai_chat_api -v
```
