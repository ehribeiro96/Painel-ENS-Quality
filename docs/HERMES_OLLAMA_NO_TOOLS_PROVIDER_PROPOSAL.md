# Proposta controlada: reduzir tool-use enforcement para Ollama LAN sem promover default local

Data: 2026-06-12
Status: proposta testada, não aprovada para permanência; revertida para `agent.tool_use_enforcement: true`

## Reversão aplicada em 2026-06-12

A lista experimental em `agent.tool_use_enforcement` não resolveu o problema principal do `llama3.2:3b-hermes-64k`: o modelo continuou retornando JSON/tool-call-like via wrapper Hermes. Além disso, manter a lista poderia mudar o comportamento de fallbacks não incluídos, especialmente Gemini/Bedrock/Claude.

Decisão operacional aplicada:

```yaml
agent:
  tool_use_enforcement: true
```

Motivo da reversão:

- preservar o comportamento global esperado do Hermes;
- não criar diferença silenciosa nos fallbacks;
- manter Codex como default seguro;
- manter `model.context_length: 262144`;
- manter Ollama apenas como uso explícito;
- não promover `llama3.2:3b-hermes-64k`;
- não promover Qwen3.

Backup antes da reversão:

- `/home/estevaoqualityadm/.hermes/config.yaml.backup-20260612-085852`
- `15767` bytes
- mtime: `2026-06-12T08:49:18`

Validação da reversão:

- `YAML_OK_BEFORE`
- `YAML_OK_AFTER`
- `hermes config` carregou sem erro
- default continuou `openai-codex` / `gpt-5.5`
- `model.context_length` continuou `262144`
- `agent.tool_use_enforcement` voltou para `true`
- fallbacks `gemini` e `bedrock` continuaram presentes
- `ollama-lan` continuou presente

Smoke tests:

- Codex default: `CODEX_OK` — passou.
- Coder local explícito: `CODER_OK` — passou.
- Llama local explícito: `{"name": "LOCAL_OK", "parameters": {}}` — limitação conhecida, ainda não corrigida.

Recomendação pós-reversão: não insistir em `agent.tool_use_enforcement` como correção para o `llama3.2`. O próximo diagnóstico real deve inspecionar o prompt final e os schemas/tool schemas enviados pelo Hermes ao modelo local, ou testar um perfil/provider realmente sem ferramentas.

## Resultado da aplicação controlada em 2026-06-12

A proposta foi testada com alteração mínima em `~/.hermes/config.yaml`, sem promover Ollama como default, sem promover Qwen3, sem remover providers e sem alterar `model.context_length`.

Antes:

```yaml
agent:
  tool_use_enforcement: true
```

Depois:

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

Backup obrigatório criado antes da alteração:

- `/home/estevaoqualityadm/.hermes/config.yaml.backup-20260612-084854`
- `15712` bytes
- mtime: `2026-06-12T08:11:31`

Validações concluídas:

- `YAML_OK_BEFORE`
- `YAML_OK_AFTER`
- `hermes config` carregou sem erro
- default continuou `openai-codex` / `gpt-5.5`
- `model.context_length` continuou `262144`
- `ollama-lan` continuou em `custom_providers`
- fallback providers continuaram presentes

Smoke tests pós-alteração:

- Codex default: `CODEX_OK` — passou.
- Llama local explícito: retornou `{"name": "", "parameters": {"}}` — ainda falhou para texto puro e continuou JSON/tool-call-like.
- Coder local explícito: `CODER_OK` — passou.

Conclusão: manter a alteração é aceitável porque Codex e coder foram preservados e o Hermes config/YAML continuou válido, mas a hipótese de que remover `llama` do `tool_use_enforcement` corrigiria totalmente o `llama3.2` não se confirmou. A classificação operacional é **PARTIAL**, não GO. Não recomendar `llama3.2:3b-hermes-64k` como default.

## Objetivo

Preparar uma correção segura para investigar o comportamento JSON/tool-call-like do `llama3.2:3b-hermes-64k` no Hermes wrapper, sem alterar o default para Ollama e sem quebrar o default Codex.

## Campo exato detectado

O código local do Hermes mostra que `agent.tool_use_enforcement` aceita quatro formas principais:

```yaml
agent:
  tool_use_enforcement: true   # injeta guidance para todos os modelos
```

Também aceita:

```yaml
agent:
  tool_use_enforcement: false  # não injeta guidance
```

E aceita lista de substrings de modelo:

```yaml
agent:
  tool_use_enforcement:
    - gpt
    - codex
    - qwen
    - deepseek
    - grok
```

Pelo código em `~/.hermes/hermes-agent/agent/system_prompt.py`, quando o valor é uma lista, o Hermes injeta o guidance apenas se o nome do modelo contiver uma das substrings.

## Alteração mínima sugerida

Hoje:

```yaml
agent:
  tool_use_enforcement: true
```

Proposta experimental:

```yaml
agent:
  tool_use_enforcement:
    - gpt
    - codex
    - qwen
    - deepseek
    - grok
```

Efeito esperado:

- Codex continua recebendo enforcement porque `gpt-5.5` e `gpt-5.4-mini` batem em `gpt`.
- Modelos Codex que contenham `codex` também continuam cobertos.
- `qwen2.5-coder:7b-hermes-64k` continua coberto por `qwen`.
- `llama3.2:3b-hermes-64k` deixa de receber o guidance de tool-use enforcement, porque não contém nenhuma substring listada.

## Por que não aplicar automaticamente agora

Não aplicar automaticamente nesta rodada porque:

- a regra do usuário foi diagnosticar e propor correção segura, não forçar default local;
- a mudança é global no `agent.tool_use_enforcement`, embora preserve Codex por substring;
- não existe flag CLI documentada para desabilitar tools/tool enforcement em uma única chamada;
- a alteração exige backup e rodada de validação específica.

## `extra_body` do provider

O schema de `custom_providers` suporta `extra_body`, mas isso afeta o payload enviado ao endpoint OpenAI-compatible. Não foi encontrado campo de `extra_body` que desabilite a injeção de guidance de ferramentas no system prompt do Hermes.

Adicionar algo como:

```yaml
extra_body:
  stream: false
  think: false
  max_tokens: 512
```

pode ser útil para parâmetros do endpoint, mas não resolve diretamente a hipótese de prompt/tool-use enforcement, porque o problema observado é o modelo responder com JSON/tool-call-like como texto.

## Procedimento obrigatório se a proposta for testada

### 1. Backup

```bash
backup="$HOME/.hermes/config.yaml.backup-$(date +%Y%m%d-%H%M%S)"
cp "$HOME/.hermes/config.yaml" "$backup"
stat -c '%n %s bytes %y' "$backup"
```

### 2. Editar somente o campo proposto

Trocar:

```yaml
agent:
  tool_use_enforcement: true
```

por:

```yaml
agent:
  tool_use_enforcement:
    - gpt
    - codex
    - qwen
    - deepseek
    - grok
```

Não alterar:

```yaml
model:
  context_length: 262144
```

Não promover Qwen3.

### 3. Validar YAML

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path.home() / '.hermes' / 'config.yaml'
with path.open('r', encoding='utf-8') as f:
    yaml.safe_load(f)
print('YAML_OK')
PY
```

### 4. Validar Hermes config

```bash
hermes config
```

Critério:

- comando retorna exit 0;
- default continua `openai-codex` / `gpt-5.5`;
- `model.context_length` continua `262144`.

### 5. Testar default seguro

```bash
hermes chat -q "Responda somente: CODEX_BASE_OK"
```

Critério:

- saída contém `CODEX_BASE_OK`;
- sem erro.

### 6. Testar llama explícito

```bash
hermes chat -q "Responda somente: LOCAL_OK" --provider ollama-lan --model llama3.2:3b-hermes-64k
```

Critério de sucesso experimental:

- saída textual simples contendo `LOCAL_OK`;
- sem JSON/tool-call-like (`{"name": ...}`);
- sem `LOCAL_ERROR`.

### 7. Testar coder explícito

```bash
hermes chat -q "Responda somente: CODER_OK" --provider ollama-lan --model qwen2.5-coder:7b-hermes-64k
```

Critério:

- saída textual simples contendo `CODER_OK`.

## Rollback

Se `hermes config`, YAML ou smoke test Codex falhar:

```bash
cp "$backup" "$HOME/.hermes/config.yaml"
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path.home() / '.hermes' / 'config.yaml'
with path.open('r', encoding='utf-8') as f:
    yaml.safe_load(f)
print('YAML_OK_AFTER_ROLLBACK')
PY
hermes config
hermes chat -q "Responda somente: CODEX_BASE_OK"
```

## Decisão recomendada

Não aplicar agora.

Classificação operacional atual:

- GO para manter Codex como default.
- PARTIAL para Ollama local: `qwen2.5-coder:7b-hermes-64k` funciona como chamada explícita, mas `llama3.2:3b-hermes-64k` não deve ser default.
- NO-GO para promover `llama3.2:3b-hermes-64k` como default nesta rodada.
