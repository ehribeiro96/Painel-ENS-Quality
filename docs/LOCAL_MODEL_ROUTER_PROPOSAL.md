# Local Model Router Proposal

Data da auditoria: 2026-06-11
Escopo: Hermes local + Ollama + Painel ENS-Quality.

## Objetivo

Definir um roteador local simples, previsível e seguro para escolher o melhor modelo Ollama por tipo de tarefa, sem quebrar o fluxo atual do Painel nem substituir o backend existente de AI Chat.

## Situação atual

O backend do Painel já trabalha com providers configuráveis (`mock`, `gemini`, `openai`). Isso é suficiente para o AI Chat do produto, mas não resolve a orquestração do Hermes local com modelos Ollama na LAN.

A solução proposta é criar uma camada de roteamento fora do backend de produto, para uso do Hermes/CLI e de automações locais.

## Premissas

- Ollama expõe endpoint OpenAI-compatible na rede local.
- O contexto real deve ser >= 64K para as rotas de tool use.
- Não há fine-tuning nesta fase.
- O roteador precisa ser determinístico e fácil de auditar.
- O fallback deve ser explícito.

## Proposta de roteamento

### Tiers

| Tier | Modelo | Papel |
|---|---|---|
| T0 | `qwen3:4b-64k` | cérebro principal / agente geral |
| T1 | `qwen2.5-coder:7b-64k` | código, revisão, testes, scripts |
| T2 | `qwen3:1.7b-64k` | fallback leve |

### Regras de decisão

1. Se a tarefa envolve arquitetura, síntese, coordenação ou múltiplas restrições, usar `qwen3:4b-64k`.
2. Se a tarefa é focada em código, testes, lint, patch ou refatoração, usar `qwen2.5-coder:7b-64k`.
3. Se a tarefa é curta, de baixa complexidade ou precisa de latência menor, usar `qwen3:1.7b-64k`.
4. Se o modelo preferencial falhar, cair para o próximo tier com a mesma instrução resumida.

## Sinais de roteamento sugeridos

- Palavras-chave de código: `diff`, `patch`, `refactor`, `test`, `compile`, `bug`, `stack trace`.
- Palavras-chave de operação: `audit`, `summary`, `report`, `compare`, `plan`, `route`.
- Palavras-chave de baixa complexidade: `resumir`, `classificar`, `extrair`, `triagem`.
- Contexto longo ou tarefa multi-etapas: sempre priorizar o cérebro principal.

## Política de prompt

Cada modelo deve receber uma instrução curta e consistente.

### Prompt base do cérebro principal

- responder com precisão;
- não inventar fatos;
- pedir evidência quando faltar contexto;
- priorizar segurança, rastreabilidade e objetividade;
- evitar ações destrutivas.

### Prompt base do coder

- produzir diffs pequenos;
- preferir correção mínima e verificável;
- não alterar contratos sem necessidade;
- responder direto;
- manter foco em código e testes.

### Prompt base do fallback

- responder rápido;
- manter linguagem simples;
- limitar escopo;
- não assumir tarefas complexas.

## Integração recomendada

O roteador local pode viver em um arquivo de configuração separado do produto, por exemplo:

- `ai-lab/router/router.yaml`
- `ai-lab/router/policies/*.yaml`
- `ai-lab/router/README.md`

Isso evita acoplar a lógica experimental ao backend do Painel.

## Regras de segurança

- Não usar o roteador para auto-apply em dados do Painel.
- Não mover credenciais para prompts.
- Não registrar outputs completos com segredos.
- Não mandar tarefas de produção para um modelo sem validação.
- Manter um modo `dry-run` para auditoria.

## Critérios de sucesso

- Escolha previsível do modelo por tipo de tarefa.
- Fallback automático sem perda de contexto crítico.
- Benchmarks melhores ou iguais em qualidade, com menor latência operacional.
- Operação local sem dependência da nuvem para tarefas diárias.

## Próxima implementação sugerida

1. criar benchmark com casos reais do Painel;
2. medir o trio principal;
3. consolidar regras de roteamento;
4. documentar defaults;
5. só então expor o roteamento para automações do Hermes.
