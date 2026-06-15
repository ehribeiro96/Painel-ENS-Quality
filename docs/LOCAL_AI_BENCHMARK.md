# Local AI Benchmark

Data da auditoria: 2026-06-11
Data/hora do smoke test: 2026-06-11T20:13:44Z → 2026-06-11T20:14:12Z
Escopo: validação curta e controlada de modelos Ollama na LAN para uso com Hermes.

## Objetivo

Validar rapidamente se o endpoint local está saudável e se os modelos candidatos respondem a um prompt mínimo antes de qualquer troca de default no Hermes.

## Endpoint usado

- `http://192.168.0.103:11434/v1`
- rota de saúde: `GET /v1/models`
- rota de teste: `POST /v1/chat/completions`

## Modelos testados no smoke test

- `qwen3:1.7b-64k`
- `qwen3:4b-64k`
- `qwen2.5-coder:7b-64k`
- `llama3.2:3b-64k`

Prompt fixo:

- `Responda somente: ok`

Parâmetros usados:

- `stream=false`
- `max_tokens=32`
- timeout por chamada: `60s`

## Resultado do healthcheck mínimo

- `GET /v1/models` → HTTP `200`, resposta recebida com sucesso
- `POST /v1/chat/completions` com `qwen3:1.7b-64k` → HTTP `200`, mas sem conteúdo final em `choices[0].message.content` (`empty_response` no smoke test)

Conclusão do healthcheck: o endpoint responde, mas o comportamento do modelo menor não foi suficiente para considerar a rodada como GO.

## Resultado do smoke test

Arquivo gerado:

- `ai-lab/ollama-benchmark/results/smoke_test_models_20260611T201344Z.jsonl`

| Modelo | ok/fail | duration_ms | status_code | output_chars | Observação |
|---|---:|---:|---:|---:|---|
| `qwen3:1.7b-64k` | fail | 418 | 200 | 0 | `empty_response` |
| `qwen3:4b-64k` | fail | 24580 | 200 | 0 | `empty_response` |
| `qwen2.5-coder:7b-64k` | ok | 3423 | 200 | 2 | respondeu `ok` |
| `llama3.2:3b-64k` | ok | 6559 | 200 | 2 | respondeu `Ok` |

Resumo objetivo:

- sucessos: 2
- falhas: 2
- endpoint: saudável
- smoke test: parcial, não suficiente para trocar o default do Hermes para Ollama sem validação adicional

## Recomendação de modelos

- principal local: `qwen3:4b-64k`
- coder local: `qwen2.5-coder:7b-64k`
- fallback: `qwen3:1.7b-64k`
- PT-BR / documentação: `llama3.2:3b-64k`

## Observação operacional

- benchmark completo só deve ser rodado em `GPT_CODEX` ou em execução separada e controlada
- smoke test é pré-requisito para trocar o default do Hermes para Ollama
- o smoke test atual não atende critério de GO porque `qwen3:1.7b-64k` não produziu conteúdo final e `qwen3:4b-64k` também veio vazio nesta rodada

## Referência do script

- `ai-lab/ollama-benchmark/smoke_test_models.py`

## Investigação de `empty_response` em Qwen3

Após o smoke test inicial, foi feita uma investigação curta e controlada para separar problema de rede de problema de geração.

### Arquivos brutos gerados

- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_1_7b_openai_default.json`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_1_7b_openai_think_false.json`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_4b_openai_default.json`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_4b_openai_think_false.json`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_1_7b_native_chat_think_false.json`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/qwen3_4b_native_chat_think_false.json`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/analysis_summary.md`
- `ai-lab/ollama-benchmark/results/qwen3-empty-response-debug/thinkfalse_recheck.json`

### Diferença observada entre APIs

- A API OpenAI-compatible em `POST /v1/chat/completions` é a superfície válida para o Ollama neste laboratório.
- A tentativa em `POST /api/chat` retornou erro/HTML de resposta inválida no recorte capturado, então não deve ser tratada como caminho principal neste ambiente.
- Os JSONs brutos mostram que Qwen3 pode retornar `message.content` e também campos de `reasoning`.

### Resultado prático da investigação

- `qwen3:1.7b-64k` continua instável: em rechecagem com `think=false`, retornou apenas reasoning e `finish_reason=length`, sem conteúdo final.
- `qwen3:4b-64k` mostrou conteúdo final em rechecagem com `think=false`, mas também apresentou sessões em que a resposta veio apenas com reasoning/thinking.
- `think=false` não deve ser tratado como correção universal; ele altera o comportamento em alguns casos, mas não resolve a inconsistência de forma garantida.

### Conclusão objetiva

- Se Qwen3 continuar retornando apenas reasoning/thinking, não usar como default do Hermes.
- Manter `llama3.2:3b-64k` como candidato temporário geral/PT-BR se a estabilidade for consistente.
- Manter `qwen2.5-coder:7b-64k` como opção coder.
- Manter `qwen3:4b-64k` como candidato pendente até a geração final ficar estável em smoke test repetível.
