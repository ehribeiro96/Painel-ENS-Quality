# Painel ENS-Quality

## IA Chat

O módulo IA Chat suporta providers configuráveis para geração textual:

- `AI_PROVIDER=mock` é o padrão seguro e não usa rede externa.
- `AI_PROVIDER=openai` usa a OpenAI Chat Completions API.

Configuração local para OpenAI:

```env
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=<definir localmente>
AI_TIMEOUT_SECONDS=30
AI_MAX_INPUT_CHARS=12000
AI_MAX_OUTPUT_TOKENS=1000
```

Regras de segurança:

- Não hardcodar `OPENAI_API_KEY`.
- Não commitar segredo em `.env`.
- Não logar chave.
- A IA responde apenas texto.
- A IA não executa ações em ativos, usuários, importações, assinaturas, movimentações ou macros.

Healthcheck:

```bash
curl http://127.0.0.1:8080/api/v1/ai-chat/health
```

Relatório técnico: `docs/AI_CHAT_PROVIDER_OPENAI_REPORT.md`.
