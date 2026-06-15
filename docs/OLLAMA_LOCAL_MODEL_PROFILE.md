# Perfil local Ollama — modelo base, contexto e variantes Hermes

Data da rodada: 2026-06-11
Endpoint usado: `http://192.168.0.103:11434`

## Estado aplicado nesta rodada

O Hermes foi ajustado para usar provisoriamente o provider local `ollama-lan` como padrão diário, com:

- default local provisório: `llama3.2:3b-hermes-64k`
- coder local: `qwen2.5-coder:7b-hermes-64k`
- Qwen3 fora do default
- Codex disponível sob demanda
- `model.context_length` do GPT_CODEX preservado em `262144`

## Backup

Backup criado antes da mudança:

- `/home/estevaoqualityadm/.hermes/config.yaml.backup-20260611-205105`

## Healthcheck do endpoint

### `/v1/models`
- HTTP: 200
- modelos confirmados:
  - `llama3.2:3b-hermes-64k`
  - `qwen2.5-coder:7b-hermes-64k`
  - `qwen3:4b-hermes-nothink-64k`
  - e demais variantes base da LAN

### Smoke tests diretos contra a API OpenAI-compatible do Ollama

- `llama3.2:3b-hermes-64k` → respondeu `OK_LOCAL`
- `qwen2.5-coder:7b-hermes-64k` → respondeu `OK_CODER`

## Configuração efetiva no Hermes

```yaml
model:
  default: llama3.2:3b-hermes-64k
  provider: ollama-lan
  base_url: http://192.168.0.103:11434/v1
  context_length: 262144
  ollama_num_ctx: 65536

custom_providers:
  - name: ollama-lan
    base_url: http://192.168.0.103:11434/v1
    api_mode: chat_completions
    model: llama3.2:3b-hermes-64k
```

## Resultado dos testes com Hermes

### Default local

Com `hermes chat -q "Responda somente: LOCAL_OK"`:

- houve tentativa com erro `LOCAL_ERROR` em uma das execuções;
- outra execução com provider/model explícitos retornou conteúdo em formato de tool-call/JSON em vez de texto puro.

Interpretação: o endpoint está funcionando, mas a smoke test exata via wrapper Hermes ainda não está estável o suficiente para chamar de GO pleno.

### Troca manual para Codex

Com `hermes chat -q "Responda somente: CODEX_OK" --provider openai-codex --model gpt-5.4-mini`:

- resultado: `CODEX_OK`

### Troca manual para coder local

Com `hermes chat -q "Responda somente: CODER_OK" --provider ollama-lan --model qwen2.5-coder:7b-hermes-64k`:

- resultado: `CODER_OK`

## Motivo para Qwen3 não ser default

`qwen3:4b-hermes-nothink-64k` continua fora do default porque não demonstrou consistência suficiente nesta rodada e o fluxo oficial pede evitar sua promoção até estabilização.

## Recomendação operacional

- Use `llama3.2:3b-hermes-64k` como default local provisório apenas enquanto o wrapper Hermes estiver estável com ele.
- Use `qwen2.5-coder:7b-hermes-64k` para código, refatoração e testes rápidos.
- Use `openai-codex` somente quando quiser nuvem explicitamente.
- Não usar `qwen3:4b-hermes-nothink-64k` como default.

## Riscos

- HTTP na LAN continua dependente de rede local confiável.
- Diferença entre o endpoint bruto e o wrapper Hermes pode gerar falsos negativos no smoke test.
- O default do Hermes pode precisar de ajuste adicional no schema/flags se o objetivo for texto puro e não tool-call/JSON.

## Rollback

Se precisar reverter:

```bash
cp /home/estevaoqualityadm/.hermes/config.yaml.backup-20260611-205105 /home/estevaoqualityadm/.hermes/config.yaml
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path('/home/estevaoqualityadm/.hermes/config.yaml')
with path.open('r', encoding='utf-8') as f:
    yaml.safe_load(f)
print('rollback_yaml_ok')
PY
hermes config
```

## Próximo passo

Se a meta for fechar com GO, o próximo passo é investigar o motivo do comportamento inconsistente do `hermes chat` com o default local, apesar do endpoint e do coder local responderem corretamente.
