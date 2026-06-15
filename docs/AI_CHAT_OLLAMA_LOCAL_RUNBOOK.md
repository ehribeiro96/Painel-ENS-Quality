# AI Chat Ollama Local Runbook

## 1. Como verificar Ollama

No WSL, verifique se o binário e o servidor local estão disponíveis:

```bash
command -v ollama
ollama --version
curl --max-time 5 -s http://127.0.0.1:11434/api/tags
```

O endpoint esperado é apenas local:

```text
http://127.0.0.1:11434
```

Não exponha Ollama diretamente para o browser ou para a rede externa.

## 2. Como listar modelos

```bash
ollama list
curl --max-time 5 -s http://127.0.0.1:11434/api/tags
```

Ordem recomendada para B5-A:

1. `qwen2.5-coder:7b-hermes-64k`
2. `qwen2.5-coder:7b-64k`
3. `qwen2.5-coder:7b`
4. `qwen2.5-coder:3b-64k`
5. `qwen2.5-coder:3b`
6. `llama3.2:3b-64k`
7. `llama3.2:3b`
8. `gemma3:latest`

Não baixar modelo automaticamente em boundary de integração. Se não houver modelo, escolha manualmente e rode `ollama pull <modelo>` fora da boundary.

## 3. Como testar `/api/chat` direto

```bash
MODEL="qwen2.5-coder:7b"

curl --max-time 120 -s http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${MODEL}\",
    \"stream\": false,
    \"messages\": [
      {\"role\": \"system\", \"content\": \"Você é um assistente técnico em português.\"},
      {\"role\": \"user\", \"content\": \"Responda apenas OK.\"}
    ]
  }"
```

Resultado esperado: JSON com `message.content` preenchido.

## 4. Como subir backend com `AI_CHAT_PROVIDER=ollama`

Sem alterar `.env`, suba uma instância temporária:

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
PYTHONPATH=backend \
AI_CHAT_PROVIDER=ollama \
OLLAMA_BASE_URL=http://127.0.0.1:11434 \
OLLAMA_MODEL="qwen2.5-coder:7b" \
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Valide health:

```bash
curl -i --max-time 10 http://127.0.0.1:8001/health
```

## 5. Como validar endpoint backend

O frontend deve continuar usando somente o backend:

```text
/api/v1/ai-chat/health
/api/v1/ai-chat/conversations
/api/v1/ai-chat/conversations/{conversation_id}/messages
```

Essas rotas exigem autenticação/RBAC. Para validação automatizada sem credenciais reais, use testes dedicados com sessão fake:

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_ai_chat_ollama_provider.py -q -o addopts=''
```

## 6. Como diagnosticar modelo ausente

Sintomas comuns:

- Ollama responde HTTP 404.
- Backend retorna HTTP 502 com detalhe sanitizado contendo `ollama_model_unavailable`.

Ação:

```bash
ollama list
curl --max-time 5 -s http://127.0.0.1:11434/api/tags
```

Ajuste manualmente o modelo via runtime:

```bash
OLLAMA_MODEL="modelo_existente"
```

Não permita que o frontend escolha o modelo ou URL arbitrária.

## 7. Como diagnosticar timeout

Sintomas:

- Backend retorna erro controlado com `ollama_timeout`.
- Modelo grande demora para carregar ou a GPU/CPU está saturada.

Ações:

```bash
ollama ps
curl --max-time 5 -s http://127.0.0.1:11434/api/tags
```

Aumente apenas no backend/runtime, se necessário:

```bash
OLLAMA_TIMEOUT_SECONDS=180
```

## 8. Como voltar para provider anterior

Para mock offline:

```bash
AI_CHAT_PROVIDER=mock
AI_MODEL=
```

Para Gemini/OpenAI, use apenas variáveis de backend e nunca exponha chave no frontend. Não grave segredo real em docs ou `.env.example`.

## 9. Ollama LAN OpenAI-compatible (`ollama-lan`)

Use este modo somente quando a boundary exigir o Ollama de uma máquina LAN e o host estiver explicitamente aprovado no backend.

Configuração temporária segura, sem alterar `.env` real:

```bash
AI_CHAT_PROVIDER=ollama-lan \
AI_PROVIDER=ollama-lan \
OLLAMA_BASE_URL="http://192.168.0.103:11434/v1" \
OLLAMA_MODEL="qwen3:1.7b-64k" \
OLLAMA_ALLOWED_HOSTS="localhost,127.0.0.1,::1,192.168.0.103" \
OLLAMA_TIMEOUT_SECONDS=120 \
PYTHONPATH=backend \
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Validação direta do endpoint OpenAI-compatible, se a rede LAN estiver aprovada:

```bash
BASE="http://192.168.0.103:11434/v1"
MODEL="qwen3:1.7b-64k"

curl --max-time 10 -s "$BASE/models"

curl --max-time 120 -s "$BASE/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${MODEL}\",\"stream\":false,\"messages\":[{\"role\":\"system\",\"content\":\"Você é um assistente técnico em português.\"},{\"role\":\"user\",\"content\":\"Responda apenas: OK via Ollama LAN.\"}]}"
```

Resultado esperado: JSON com `choices[0].message.content` preenchido. Não use `/api/chat` neste modo.

Baseline atual do `ollama-lan`: `qwen3:1.7b-64k`.

Validação B5-C confirmada:

- `GET /v1/models`: HTTP 200, JSON válido e `qwen3:1.7b-64k` disponível.
- `POST /v1/chat/completions`: HTTP 200 e `choices[0].message.content` retornou `OK via Ollama LAN.`.
- Provider backend `ollama-lan`: `OllamaLanProvider`, sem mock.
- UI autenticada ainda depende de validação separada se a sessão do navegador não permanecer ativa.

## 10. Cuidados de segurança

- Provider `ollama` local deve permanecer em `127.0.0.1` e usa `/api/chat`.
- Provider `ollama-lan` usa endpoint OpenAI-compatible `/v1/chat/completions`.
- `192.168.0.103` só é permitido se estiver em `OLLAMA_ALLOWED_HOSTS`.
- Não usar wildcard em `OLLAMA_ALLOWED_HOSTS`.
- Não permitir IP público.
- Frontend nunca chama `http://127.0.0.1:11434` nem `http://192.168.0.103:11434` diretamente.
- Frontend não envia `OLLAMA_BASE_URL`.
- Backend não aceita URL arbitrária do request.
- `get_ai_provider_health` não expõe `OLLAMA_BASE_URL` ao frontend.
- Provider errors são códigos sanitizados, sem stack trace.
- Rate limit B2 deve continuar antes da chamada ao provider.
- Não baixar modelos automaticamente durante boundary de código.
