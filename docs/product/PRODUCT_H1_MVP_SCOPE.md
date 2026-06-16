# MVP Operacional — Painel ENS-Quality

Boundary: `PRODUCT-H1 — roadmap de evolução funcional do Painel ENS-Quality`
Status: planejamento funcional/técnico, sem implementação.

## Objetivo do MVP

Entregar um fluxo operacional diário confiável para a equipe N2 registrar, localizar e movimentar ativos, gerar uma macro ITIL oficial após a movimentação salva, copiar essa macro para o chamado e rastrear todo o ciclo em histórico e auditoria.

O MVP não é “ter todas as telas bonitas”; é conseguir executar o caso real de suporte com dado persistido, validação mínima, evidência auditável e baixa chance de operador colar uma macro errada.

## Usuário principal

- N2 Suporte: executa movimentação, consulta ativo, copia macro e confere histórico.
- Programador/analista: mantém templates, investiga inconsistências e apoia UAT/release.
- Operação ENS-Quality: acompanha qualidade dos dados, auditoria e adoção do processo.

## Fluxos obrigatórios

1. Ativo manual
   - Criar ativo com identidade mínima (`hostname`, patrimônio ou serial).
   - Consultar ativo por lista e detalhe.
   - Ver situação atual: usuário, status, localidade e identificação técnica.

2. Ativo importado
   - Fazer upload de planilha CSV/XLSX pelo pipeline validado.
   - Revisar preview, staging, conflitos e validações.
   - Aplicar somente linhas seguras, com confirmação humana.
   - Preservar dados operacionais críticos quando a política de merge bloquear sobrescrita automática.

3. Movimentação
   - Registrar movimentação somente após revisão explícita de usuário, status e localidade.
   - Exigir justificativa.
   - Persistir `AssetMovement` imutável.
   - Atualizar o estado canônico do ativo no PostgreSQL.

4. Macro pós-movimentação
   - Gerar macro somente depois da movimentação salva.
   - Vincular geração ao `movement_id` via `context_type=asset_movement` e `context_id`.
   - Exibir campos pendentes quando houver.
   - Permitir copiar somente macro persistida com `generation_id`.
   - Marcar macro como copiada e registrar auditoria.

5. Histórico
   - Exibir timeline do ativo a partir de `/assets/{id}/history`.
   - Mostrar antes/depois, justificativa e data/hora.
   - Preservar imutabilidade da movimentação.

6. Auditoria
   - Registrar create/update/delete/move/import/macro/copy/login/logout conforme ação.
   - Permitir consulta por equipe autorizada.
   - Preservar `request_id`, `correlation_id`, ator, fonte, entidade e snapshots quando disponíveis.

7. IA assistiva local
   - AI Chat pode explicar macro, revisar texto, sugerir melhoria e apoiar análise.
   - IA não altera ativo, movimentação, importação, template ou auditoria sem preview e aprovação humana.
   - Browser continua falando com backend same-origin; provider `ollama-lan` permanece interno.

## Fluxos fora do MVP

- Automação autônoma de movimentações pela IA.
- Abertura real automática de chamado ITIL em ferramenta externa.
- Dashboard executivo completo com SLA/KPIs históricos.
- Exportação operacional final em massa.
- Edição avançada de templates por usuário final sem guardrails.
- Limpeza/remoção de legado `/admin` e `/assinaturas`.
- Refatoração visual global do frontend.
- Troca de provider/modelo de IA.
- Alteração de migrations, Docker volumes, CI publish ou import pipeline validado fora de boundary própria.

## Critérios de aceite

- Um operador consegue localizar um ativo, movimentar, ver macro gerada, copiar e conferir histórico em uma única sessão autenticada.
- A macro oficial só aparece após o backend retornar uma movimentação salva.
- O botão “Copiar macro” só marca `copied` quando existe `generation_id` persistido.
- O histórico do ativo reflete a movimentação recém-criada.
- A auditoria contém eventos para movimentação, geração de macro e cópia da macro.
- Importação continua em staging/review antes de aplicar; conflitos bloqueiam apply.
- IA Chat responde como apoio textual sem executar ação operacional.
- Usuários sem permissão não acessam imports/macros/audit/settings conforme RBAC atual.
- Nenhum fluxo MVP exige alteração de `.env`, migrations, Docker volumes ou package-lock.

## Não objetivos

- Não resolver todos os itens de release/infra pendentes nesta fase.
- Não limpar untracked antigos.
- Não publicar commits ou imagens Docker.
- Não substituir a UX atual por redesign amplo.
- Não mudar o legado validado.
- Não transformar IA em agente executor.

## Riscos

- Macro pós-movimentação fica invisível porque o modal fecha após `onMoved()`; a implementação atual chama `setMovementMacro()` e em seguida `onMoved()` fecha o modal em `AssetDetailsPage`.
- Timeline mostra IDs truncados de usuários/responsável, não nomes; isso reduz valor operacional em auditoria humana.
- Auditoria atual lista eventos, mas ainda não tem filtros por entidade, ação, período ou ID do ativo/movimentação.
- Movimentação não expõe uma rota dedicada `/movements/{id}` para detalhe operacional; macro usa rota de sugestão, mas UAT pode precisar evidenciar movimento individual.
- Importação é forte tecnicamente, mas UAT diário precisa separar “ativo manual” de “ativo importado” com evidência clara.
- Dashboard ainda parece agregador inicial, não cockpit operacional.
- IA local depende de disponibilidade do Ollama LAN; indisponibilidade deve virar limitação operacional, não bug do frontend.

## Dependências

- Backend FastAPI modular em `backend/app/api/v1/routes` e `backend/app/domains`.
- Frontend React/Vite em `frontend/itam-platform/src`.
- PostgreSQL como fonte canônica.
- Redis para runtime/rate limit quando aplicável.
- Provider `ollama-lan` e baseline `qwen3:1.7b-64k` preservados.
- Seeds/templates de macro oficiais, especialmente slug `ativos-atualizar-inventario`.
- Testes existentes de assets, macros, imports, AI Chat, auth, legacy e operational contracts.
