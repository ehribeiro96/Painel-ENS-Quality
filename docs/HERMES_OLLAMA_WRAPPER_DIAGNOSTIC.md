# Diagnóstico do provider Ollama LAN no Hermes

Data: 2026-06-12
Projeto: Painel ENS-Quality

## Reversão operacional aplicada em 2026-06-12

Status da rodada: **GO** para restauração segura do Hermes.

A tentativa anterior de trocar `agent.tool_use_enforcement: true` por uma lista de substrings preservou Codex e `qwen2.5-coder`, mas não corrigiu o comportamento do `llama3.2:3b-hermes-64k`. Como a lista também poderia alterar o comportamento global de fallbacks que não estavam incluídos, como Gemini/Bedrock/Claude, a configuração foi revertida para o comportamento seguro original:

```yaml
agent:
  tool_use_enforcement: true
```

Backup criado antes da reversão:

- caminho: `/home/estevaoqualityadm/.hermes/config.yaml.backup-20260612-085852`
- tamanho: `15767` bytes
- mtime preservado: `2026-06-12T08:49:18`

Validações da reversão:

- YAML antes: `YAML_OK_BEFORE`
- YAML depois: `YAML_OK_AFTER`
- `hermes config`: válido, default preservado em `openai-codex` / `gpt-5.5`, `model.context_length: 262144`
- `agent.tool_use_enforcement`: voltou para `true`
- provider custom `ollama-lan` preservado
- fallback providers preservados: `gemini/gemini-2.5-flash` e `bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0`

Smoke tests após reversão:

| Teste | Resultado observado | Classificação |
| --- | --- | --- |
| Codex default (`CODEX_OK`) | `CODEX_OK` | Passou |
| Coder local explícito (`CODER_OK`) | `CODER_OK` | Passou |
| Llama local explícito (`LOCAL_OK`) | `{"name": "LOCAL_OK", "parameters": {}}` | Limitação conhecida; ainda JSON/tool-call-like |

Conclusão atual: Codex permanece o default seguro; `qwen2.5-coder:7b-hermes-64k` permanece recomendado apenas para uso manual explícito; `llama3.2:3b-hermes-64k` continua não recomendado via wrapper Hermes; Qwen3 continua não recomendado. O próximo diagnóstico real deve investigar o prompt final e os schemas/tool schemas enviados pelo Hermes ao modelo local, não repetir a alteração em `tool_use_enforcement`.

## Atualização controlada aplicada em 2026-06-12

Status da rodada: **PARTIAL**.

Foi aplicada uma correção mínima em `~/.hermes/config.yaml`, com backup prévio, para trocar `agent.tool_use_enforcement` de `true` para uma lista explícita de famílias/modelos fortes:

```yaml
agent:
  tool_use_enforcement:
    - gpt
    - codex
    - openai
    - qwen
    - deepseek
    - grok
```

Backup criado:

- caminho: `/home/estevaoqualityadm/.hermes/config.yaml.backup-20260612-084854`
- tamanho: `15712` bytes
- mtime preservado: `2026-06-12T08:11:31`

Validações:

- YAML antes: `YAML_OK_BEFORE`
- YAML depois: `YAML_OK_AFTER`
- `hermes config`: exit 0, default preservado em `openai-codex` / `gpt-5.5`, `model.context_length: 262144`
- provider custom `ollama-lan` preservado
- fallback providers preservados: `gemini/gemini-2.5-flash` e `bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0`

Smoke tests pós-alteração:

| Teste | Comando | Resultado observado | Classificação |
| --- | --- | --- | --- |
| Codex default | `hermes chat -q "Responda somente: CODEX_OK"` | `CODEX_OK` | Passou |
| Llama local explícito | `hermes chat -q "Responda somente: LOCAL_OK" --provider ollama-lan --model llama3.2:3b-hermes-64k` | `{"name": "", "parameters": {"}}` | Falhou para texto puro; ainda JSON/tool-call-like |
| Coder local explícito | `hermes chat -q "Responda somente: CODER_OK" --provider ollama-lan --model qwen2.5-coder:7b-hermes-64k` | `CODER_OK` | Passou |

Conclusão: a mudança não quebrou Codex nem o coder local, preservou o contexto `262144` e manteve providers/fallbacks. Porém, `llama3.2:3b-hermes-64k` continuou retornando JSON/tool-call-like via wrapper Hermes. Portanto, a correção configuracional reduziu o escopo do guidance global, mas não resolveu completamente o comportamento do llama. Não usar `llama3.2:3b-hermes-64k` como default.

Rollback, se necessário:

```bash
cp /home/estevaoqualityadm/.hermes/config.yaml.backup-20260612-084854 /home/estevaoqualityadm/.hermes/config.yaml
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path.home() / '.hermes' / 'config.yaml'
with path.open('r', encoding='utf-8') as f:
    yaml.safe_load(f)
print('ROLLBACK_YAML_OK')
PY
hermes config
```

## Escopo

Investigar o comportamento instável do modelo local `llama3.2:3b-hermes-64k` quando usado via wrapper Hermes/provider `ollama-lan`, sem repetir o teste `curl` bloqueado anteriormente e sem alterar `~/.hermes/config.yaml`.

## Estado atual preservado

O default real do Hermes permanece seguro em Codex:

- provider: `openai-codex`
- model: `gpt-5.5`
- base_url: `https://chatgpt.com/backend-api/codex`
- `model.context_length`: `262144`
- `model.ollama_num_ctx`: `65536`

Configurações relevantes observadas:

- `agent.tool_use_enforcement`: `true`
- `agent.reasoning_effort`: `medium`
- `display.show_reasoning`: `false`
- `display.streaming`: `true`
- `streaming.enabled`: `false`

Provider custom relevante:

```yaml
custom_providers:
  - name: ollama-lan
    base_url: http://192.168.0.103:11434/v1
    api_key: [REDACTED]
    model: llama3.2:3b-hermes-64k
    api_mode: chat_completions
```

Não havia `extra_body` no provider `ollama-lan`.

## Testes executados via Hermes chat

### Default Codex

Comando:

```bash
hermes chat -q "Responda somente: CODEX_BASE_OK"
```

Resultado resumido:

```text
CODEX_BASE_OK
```

Classificação:

- Passou.
- Texto puro.
- Sem JSON/tool-call-like.
- Sem erro.

### Llama explícito via ollama-lan

Comando:

```bash
hermes chat -q "Responda somente: LOCAL_OK" --provider ollama-lan --model llama3.2:3b-hermes-64k
```

Resultado resumido:

```json
{"name": "LOCAL_OK", "parameters": {}}
```

Classificação:

- Falhou para o critério de texto puro.
- Contém `LOCAL_OK`, mas em formato JSON/tool-call-like.
- Sem erro de transporte.
- A sessão Hermes registrou `0 tool calls`; o problema é a saída textual simulando tool call, não uma chamada real de ferramenta despachada pelo Hermes.

### Coder explícito via ollama-lan

Comando:

```bash
hermes chat -q "Responda somente: CODER_OK" --provider ollama-lan --model qwen2.5-coder:7b-hermes-64k
```

Resultado resumido:

```text
CODER_OK
```

Classificação:

- Passou.
- Texto puro.
- Sem JSON/tool-call-like.
- Sem erro.

## Verificação de flags CLI

Comandos consultados:

```bash
hermes chat --help || true
hermes --help || true
hermes config --help || true
```

Resultado:

- Existe `--provider` para override por chamada.
- Existe `--model` para override por chamada.
- Existe `-t, --toolsets` para selecionar toolsets por chamada.
- Não foi encontrada flag documentada como `--no-tools`, `--disable-tools`, `--tool-use`, `--tool_use_enforcement`, `--reasoning` ou equivalente para desativar tool-use/tool-use enforcement em uma chamada isolada de `hermes chat`.

Por isso, não foi feito teste inventado com flag inexistente.

## Evidência em código local do Hermes

Arquivos consultados no install local `~/.hermes/hermes-agent`:

- `agent/system_prompt.py`
- `tests/run_agent/test_run_agent.py`
- `agent/agent_init.py`
- `hermes_cli/config.py`

Achados:

1. `agent.tool_use_enforcement` aceita:
   - `true` / `always`: injeta guidance para todos os modelos.
   - `false` / `off`: não injeta.
   - lista de substrings de modelo: injeta apenas quando o nome do modelo contém uma das substrings.
   - `auto`: injeta para famílias codificadas no Hermes.

2. Com o valor atual `true`, o guidance de uso de ferramentas é injetado para o `llama3.2:3b-hermes-64k` também.

3. `custom_providers` suporta `extra_body` e o Hermes mescla esse bloco em `request_overrides.extra_body` quando o provider custom é resolvido para `custom`.

4. Não foi encontrado campo documentado/observado para desabilitar tools somente no provider `ollama-lan` sem mexer no mecanismo global de tool-use enforcement.

## Hipótese principal

A causa provável é a combinação:

- provider `ollama-lan` resolvido via wrapper OpenAI-compatible/custom;
- `agent.tool_use_enforcement: true` global;
- modelo `llama3.2:3b-hermes-64k` sensível a instruções de ferramenta/tool-call;
- prompt simples exigindo texto puro.

O resultado observado sugere que o modelo imita uma chamada de ferramenta em JSON (`name` + `parameters`) em vez de responder texto plano.

## Por que não promover llama como default

Não promover `llama3.2:3b-hermes-64k` como default nesta rodada porque:

- falhou no smoke test mínimo `LOCAL_OK` via Hermes wrapper;
- retornou JSON/tool-call-like mesmo sem ferramenta real executada;
- pode contaminar respostas simples e fluxos de automação que esperam texto puro;
- não há correção isolada por chamada via CLI documentada para desativar tool-use enforcement.

## Por que qwen2.5-coder é mais estável como chamada explícita

O modelo `qwen2.5-coder:7b-hermes-64k` respondeu corretamente ao smoke test via mesmo provider `ollama-lan`:

- mesma família de endpoint/provider custom;
- mesmo wrapper Hermes;
- resposta textual simples (`CODER_OK`);
- sem JSON/tool-call-like.

Isso indica que o problema não é apenas rede/provider, mas a interação específica entre o wrapper/prompt de ferramentas e o modelo `llama3.2:3b-hermes-64k`.

## Recomendação objetiva

Status recomendado: GO operacional mantendo Codex como default.

Recomendação:

1. Manter `openai-codex` / `gpt-5.5` como default seguro.
2. Manter `model.context_length: 262144` intacto.
3. Usar `qwen2.5-coder:7b-hermes-64k` manualmente quando quiser execução local técnica/código:

   ```bash
   hermes chat -q "..." --provider ollama-lan --model qwen2.5-coder:7b-hermes-64k
   ```

4. Não promover `llama3.2:3b-hermes-64k` como default até passar em smoke test de texto puro via Hermes wrapper.
5. Não promover Qwen3 nesta rodada.
6. Se desejar testar correção em rodada controlada, avaliar uma mudança configuracional com backup para trocar `agent.tool_use_enforcement` de `true` para uma lista explícita de famílias/modelos onde a injeção deve permanecer habilitada, excluindo `llama3.2:3b-hermes-64k`.

## Rollback seguro atual

Nenhum rollback foi necessário porque `~/.hermes/config.yaml` não foi alterado nesta rodada.

Se em rodada futura o default for alterado indevidamente, o estado seguro esperado é:

```yaml
model:
  provider: openai-codex
  default: gpt-5.5
  base_url: https://chatgpt.com/backend-api/codex
  context_length: 262144
```
