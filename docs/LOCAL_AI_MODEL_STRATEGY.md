# Local AI Model Strategy

Data da auditoria: 2026-06-11
Escopo: Painel ENS-Quality + Hermes local + Ollama na LAN.

## Resumo executivo

O stack local já está pronto para operar sem fine-tuning agora: backend FastAPI modular, frontend React/Vite, PostgreSQL canônico, Redis, autenticação JWT/RBAC, auditoria, inventário, movimentação e área dedicada de AI Chat.

A mudança de maior impacto é que o Ollama remoto via LAN é o candidato local principal, mas só deve assumir o papel de padrão diário do Hermes depois de um smoke test GO com resultados consistentes; até lá, Codex/OpenAI continua disponível para situações em que o ganho de qualidade justifique o custo e a latência.

A recomendação é padronizar quatro camadas locais:

1. modelo cérebro para raciocínio operacional geral;
2. modelo especialista em código;
3. modelo leve de fallback;
4. modelo de documentação/PT-BR como candidato secundário.

## O que foi auditado

- Raiz do projeto: `/home/estevaoqualityadm/projects/Painel-ENS-Quality`
- Config Hermes local: `~/.hermes/config.yaml`
- Skills Hermes locais: `~/.hermes/skills/`
- Scripts Hermes locais: `~/.hermes/scripts/`
- Stack do produto: FastAPI + React/Vite + PostgreSQL + Redis
- Rota atual de AI Chat no backend: providers `mock`, `gemini` e `openai`
- Endpoint local OpenAI-compatible do Ollama na LAN: `http://192.168.0.103:11434/v1`

## Critério de decisão

Para melhorar o modelo usado localmente, a escolha deve priorizar:

- contexto real de pelo menos 64K;
- qualidade em tool use e instruções longas;
- estabilidade em PT-BR;
- baixo risco de alucinação operacional;
- custo/latência aceitáveis para uso interativo;
- separação clara entre raciocínio geral e geração de código;
- comportamento previsível sem depender de serviços remotos externos.

## Recomendação de modelos

### 1) Cérebro principal / agente geral

Modelo recomendado: `qwen3:4b-64k`

Motivo:

- melhor equilíbrio entre raciocínio, contexto e utilidade geral;
- suficiente para a maior parte das tarefas de Hermes local;
- mais adequado como orquestrador local do que um modelo maior e mais caro;
- é o melhor candidato para tool use, auditoria e coordenação diária.

Uso ideal:

- triagem de intenção;
- roteamento de subtarefas;
- resumo de contexto;
- instruções operacionais;
- geração de macro, checklist e respostas estruturadas.

### 2) Especialista em código

Modelo recomendado: `qwen2.5-coder:7b-64k`

Motivo:

- foco melhor em código do que um modelo geral;
- bom para revisão, refatoração, diffs e escrita de script;
- deve ficar isolado como modelo de produção de código, não como cérebro principal;
- se falhar em tool-calling ou coordenação de tarefas, isso reforça ainda mais sua posição como especialista e não como roteador geral.

Uso ideal:

- patch proposal;
- revisão de código;
- scripts curtos;
- geração de funções e testes;
- análise de erros de implementação.

### 3) Fallback leve

Modelo recomendado: `qwen3:1.7b-64k`

Motivo:

- útil quando a prioridade é latência ou recuperação rápida;
- serve como fallback de baixa complexidade;
- bom para respostas curtas, triagem e compressão.

Uso ideal:

- fallback quando o modelo principal falhar;
- tarefas simples;
- classificação e pré-processamento.

### 4) Português / documentação

Modelo candidato: `llama3.2:3b-64k`

Motivo:

- candidato razoável para linguagem natural em PT-BR;
- útil para documentação, resumo executivo e texto mais fluido;
- vale manter como opção secundária para comparação com `qwen3:4b-64k`.

## O que não usar como padrão diário

### Codex/OpenAI como default automático

Não deve ser o padrão automático porque:

- adiciona dependência externa e custo recorrente;
- aumenta latência e variabilidade;
- reduz a autonomia local;
- é melhor reservado para tarefas complexas ou quando o ganho de qualidade justifica a troca manual.

### `qwen2.5-coder:7b-64k` como cérebro principal

Não deve ser o cérebro principal se o objetivo for agente/coordenação porque:

- o foco dele é código, não orchestration geral;
- modelos coder tendem a ser menos equilibrados em tarefas operacionais amplas;
- se o tool-calling ou a resposta geral ficar instável, ele deve permanecer como especialista.

### `qwen3:8b-64k` como default na RTX 5060 8 GB

Não deve ser o padrão diário nesta máquina porque:

- maior pressão de VRAM;
- maior risco de swap/latência;
- menor previsibilidade para uso interativo;
- a relação custo/benefício tende a ser pior que `qwen3:4b-64k` para uso diário local.

## Decisão prática recomendada

Se a intenção for “melhorar o modelo local usado agora”, a ordem sugerida é:

1. configurar `qwen3:4b-64k` como padrão do roteador;
2. registrar `qwen2.5-coder:7b-64k` como modelo de código;
3. manter `qwen3:1.7b-64k` como fallback;
4. manter `llama3.2:3b-64k` como candidato para documentação/PT-BR;
5. comparar modelos futuros apenas com benchmark controlado.

## Guardrails obrigatórios

- não fazer fine-tuning nesta fase;
- não alterar dados automaticamente sem preview e aprovação;
- não expor segredos em docs, logs ou skills;
- não depender de contexto menor que 64K para tool use;
- manter o backend com DTOs explícitos e histórico/auditoria onde houver persistência;
- preservar legado e fluxos existentes.

## Próximos passos

- criar Modelfiles localmente;
- criar benchmark repetível;
- propor roteador local com decisão por tipo de tarefa;
- validar latência, qualidade e consistência em PT-BR;
- só depois considerar ajuste fino de prompts ou expansão do catálogo.
