# Hermes GPT_CODEX / openai-codex — recomendação de contexto

Data/hora desta validação: 2026-06-11T19:43:50-03:00

## Escopo

Validação controlada do contexto efetivo usado pelo Hermes para o provider `GPT_CODEX` / `openai-codex`, sem alterar Ollama, sem alterar modelos locais, sem remover providers existentes e sem expor secrets.

## Estado anterior conhecido

Baseline informado na solicitação:

- Contexto anterior conhecido: `65536`
- Provider esperado: `openai-codex` / `GPT_CODEX`
- Modelo esperado: `gpt-5.4-mini`

Estado observado no início desta rodada via `hermes config`:

- `model.default`: `gpt-5.4-mini`
- `model.provider`: `openai-codex`
- `model.base_url`: `https://chatgpt.com/backend-api/codex`
- `model.context_length`: `262144`
- `model.ollama_num_ctx`: `65536`
- `agent.max_turns`: `150`
- Fallback providers preservados: `gemini/gemini-2.5-flash` e `bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0`

Conclusão do estado inicial: o contexto não estava mais preso em `65536`; o config ativo já refletia `262144` para `model.context_length`.

## Campo YAML usado

- Campo efetivo para GPT_CODEX / `openai-codex`: `model.context_length`
- Campo Ollama preservado e não usado como controle principal nesta rodada: `model.ollama_num_ctx`
- Campos procurados e não presentes no bloco `model` ativo: `max_context_tokens`, `max_input_tokens`, `model_context_length`, `reasoning_effort`

Evidência local:

- `hermes config` exibe o bloco `Model` com `context_length`.
- A skill/procedimento local do Hermes para Codex context tuning também aponta `model.context_length` como knob efetivo para `openai-codex`.
- O código local do Hermes contém referências a `context_length` em `agent/context_engine.py`, `agent/conversation_loop.py` e `hermes_cli/config.py`.

## Valor testado e aceito

- Ordem solicitada: `131072`, `196608`, `262144`.
- Como o estado inicial desta rodada já estava em `262144`, não houve downgrade para `131072` ou `196608`.
- Valor confirmado/reaplicado: `262144`.
- Valor aceito por `hermes config`: `262144`.
- Contexto novo efetivo: `262144`.

Comando usado para confirmar/aplicar de forma idempotente:

```bash
hermes config set model.context_length 262144
```

Resultado relevante:

```text
✓ Set model.context_length = 262144 in /home/estevaoqualityadm/.hermes/config.yaml
```

## Backup obrigatório

- Caminho: `/home/estevaoqualityadm/.hermes/config.yaml.backup-20260611-194313`
- Tamanho: `15689 bytes`
- Timestamp do nome: `2026-06-11 19:43:13 -03:00`
- `stat` observado: `ctime=2026-06-11 19:43:13.942882790 -0300`

## Validações executadas

### Estado inicial

```bash
git status --short --branch
hermes config path
hermes config
```

Resultado relevante:

```text
## main...origin/main [ahead 1]
Config: /home/estevaoqualityadm/.hermes/config.yaml
Model: {'default': 'gpt-5.4-mini', 'provider': 'openai-codex', 'base_url': 'https://chatgpt.com/backend-api/codex', 'context_length': 262144, 'ollama_num_ctx': 65536}
Max turns: 150
```

### Descoberta de schema/campos

```bash
hermes config --help || true
hermes --help || true
grep -R "context_length\|max_context_tokens\|max_input_tokens\|ollama_num_ctx\|max_turns" ~/.hermes 2>/dev/null || true
grep -R "context_length\|max_context_tokens\|max_input_tokens\|ollama_num_ctx\|max_turns" . 2>/dev/null | head -n 100 || true
```

Resultado relevante:

- `hermes config set KEY VAL` é suportado.
- `model.context_length` aparece no config ativo e em backups/configs locais.
- `ollama_num_ctx` existe, mas foi preservado em `65536` e não tratado como controle principal do GPT_CODEX.

### YAML antes/depois

```bash
python3 - <<'PY'
from pathlib import Path
try:
    import yaml
except Exception as exc:
    raise SystemExit(f"PyYAML indisponível: {exc}")

path = Path.home() / ".hermes" / "config.yaml"
with path.open("r", encoding="utf-8") as f:
    yaml.safe_load(f)
print("YAML_OK")
PY
```

Resultado:

```text
YAML_OK
```

### Hermes config após aplicação

```bash
hermes config
```

Resultado relevante:

```text
Model: {'default': 'gpt-5.4-mini', 'provider': 'openai-codex', 'base_url': 'https://chatgpt.com/backend-api/codex', 'context_length': 262144, 'ollama_num_ctx': 65536}
Max turns: 150
```

Validação:

- Provider permaneceu `openai-codex` / GPT_CODEX.
- Modelo permaneceu `gpt-5.4-mini`.
- Contexto efetivo ficou acima de `65536`: `262144`.
- `ollama_num_ctx` permaneceu `65536`.
- Fallback providers não foram removidos.
- `hermes config` não quebrou.

### Teste curto funcional

```bash
hermes --provider openai-codex -m gpt-5.4-mini -z 'Responda somente: CONTEXTO_GPT_OK'
```

Resultado:

```text
CONTEXTO_GPT_OK
```

## Rollback

Não houve rollback nesta rodada.

Se for necessário voltar ao backup criado nesta validação:

```bash
cp /home/estevaoqualityadm/.hermes/config.yaml.backup-20260611-194313 /home/estevaoqualityadm/.hermes/config.yaml
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path.home() / ".hermes" / "config.yaml"
with path.open("r", encoding="utf-8") as f:
    yaml.safe_load(f)
print("YAML_OK")
PY
hermes config
```

Observação: esse backup foi criado quando o config já estava com `model.context_length: 262144`; portanto, ele restaura o estado validado desta rodada, não o baseline histórico de `65536`.

## Riscos

- Maior uso de contexto em sessões longas.
- Maior latência quando o histórico cresce.
- Possível maior custo/uso da autenticação GPT/Codex em interações extensas.
- Contexto grande não substitui checkpoints, resumos periódicos e divisão de tarefas em blocos menores.
- Se o provider real impuser limite menor em uma chamada futura, o Hermes pode precisar comprimir/reduzir contexto apesar do valor configurado.

## Resultado

Status recomendado: `GO`.

Critérios atendidos:

- Backup criado: sim.
- YAML válido antes/depois: sim.
- `hermes config` válido: sim.
- Provider preservado: sim, `openai-codex`.
- Modelo preservado: sim, `gpt-5.4-mini`.
- Contexto efetivo acima de `65536`: sim, `262144`.
- Teste curto funcional: sim, `CONTEXTO_GPT_OK`.
- Ollama não foi alterado nem promovido a default.
- Providers/fallbacks existentes não foram removidos.
