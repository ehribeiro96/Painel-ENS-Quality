# Registro geral de riscos — Painel ENS-Quality

Data: 2026-06-12 09:13:51 -03
Origem: auditoria geral não destrutiva
Status: usar antes de qualquer nova edição

## Escala

Severidade:

- Alta: pode causar vazamento, perda/corrupção de dados, quebra de fluxo crítico ou bloqueio de release.
- Média: pode causar regressão funcional, retrabalho relevante ou falha operacional limitada.
- Baixa: impacto localizado, principalmente manutenção/higiene.

Probabilidade:

- Alta: evidência presente no worktree ou comportamento já observado.
- Média: depende de próxima edição ou ambiente.
- Baixa: cenário possível, mas sem evidência direta atual.

## Matriz de riscos

| ID | Risco | Área | Severidade | Probabilidade | Evidência | Impacto | Recomendação | Prioridade | Dono sugerido |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Worktree sujo mistura backend, frontend, testes, docs, IA e artefatos | Release/higiene | Alta | Alta | `git status` mostra 14 tracked modificados e muitos untracked | Commit incorreto, regressão difícil de isolar, vazamento de artefatos | Fazer triage antes de editar; separar commit boundaries; não commitar sem revisão | P0 | Dev responsável |
| R02 | Possível API key hardcoded em `tools/composio_client.py` untracked | Segurança | Alta | Alta | Scanner redigido encontrou `COMPOSIO_API_KEY`/`api_key` no arquivo | Vazamento de credencial se versionado/compartilhado | Remover segredo, usar env/credential store, não commitar arquivo como está | P0 | Dev/Sec |
| R03 | Possível `CodeGPT.apiKey` em `.vscode/settings.json` untracked | Segurança | Alta | Média | Scanner redigido encontrou chave em settings local | Vazamento de credencial/config pessoal | Manter fora do Git; adicionar ignore se necessário com aprovação | P0 | Dev/Sec |
| R04 | `.env` e `.env.bak_20260603_132713` existem no diretório | Segurança/higiene | Alta | Média | Presença por nome confirmada; conteúdo não lido | Risco de leitura/commit acidental | Garantir `.gitignore`; nunca ler/imprimir; considerar mover backup sensível para local seguro | P0 | Dev/Sec |
| R05 | Pytest sem escopo coleta `_validation/`, `exports/` e `imports/` | Testes/higiene | Média | Alta | `pytest --collect-only` sem escopo gerou 91 erros de import mismatch | Falso vermelho, perda de confiança nos testes | Usar `pytest tests -o addopts=''`; depois avaliar exclusões no config | P1 | Dev |
| R06 | `frontend/itam-platform/src/styles.css` teve remoção massiva | UX/UI | Alta | Alta | Diff +65/-2768 | Regressão visual em páginas e componentes | Smoke visual antes de novas mudanças; revisar classes órfãs; não misturar com backend | P0 | Frontend |
| R07 | Import pipeline está em refatoração com arquivos untracked | Importação/staging | Alta | Alta | `ImportService` modificado; novos módulos classification/normalization/parsing untracked | Quebra do Lansweeper, classificação errada, overwrite indevido | Congelar e testar imports antes de editar; rodar suíte de importação dedicada | P0 | Backend |
| R08 | `ImportService` concentra muita responsabilidade | Backend/imports | Média | Alta | `backend/app/domains/imports/service.py` tem 733 linhas | Refatorações arriscadas e bugs de fluxo | Extrair gradualmente com testes; manter contrato de staging/apply | P1 | Backend |
| R09 | Fluxo macro/movimentação depende de múltiplos endpoints | Macros/ativos | Alta | Média | Movimento salva em `/assets/{id}/move`; macro sugerida em `/movements/{id}/suggested-macro` | Macro pode não ser gerada/copied se frontend falhar | Teste E2E dedicado antes de alterar; preservar geração só após movimento salvo | P1 | Backend/Frontend |
| R10 | Docker indisponível na distro WSL atual | Build/deploy | Média | Alta | `docker compose config --services` falhou por Docker não encontrado no WSL | Não há validação de compose/runtime nesta auditoria | Ativar integração Docker Desktop/WSL antes de validar deploy | P1 | DevOps |
| R11 | `docker-compose.yml` usa senha local padrão para Postgres | Segurança/devops | Média | Alta | `POSTGRES_PASSWORD: itam` em compose | Se reutilizado fora de dev, risco de credencial fraca | Manter só local; usar env obrigatório em ambientes reais | P2 | DevOps |
| R12 | CORS com credentials e métodos/headers wildcard quando habilitado | Segurança/API | Média | Média | `allow_credentials=True`, methods/headers `*` | Se origins forem amplos, risco cross-origin | Validar `allowed_origins` por ambiente; nunca wildcard com credentials | P1 | Backend/Sec |
| R13 | Rate limit genérico in-memory não escala para multi-worker | Backend/operacional | Média | Média | `main.py` usa buckets em memória | Bypass/limites inconsistentes em produção | Usar Redis para limites globais onde necessário | P2 | Backend |
| R14 | AI Chat local/externo pode ser confundido com agent operacional | IA/segurança | Alta | Média | Prompt do AI Chat proíbe ação; docs reforçam | Usuário pode acreditar que IA executou ação | Manter IA textual; nunca agency sem preview/aprovação | P1 | Backend/Produto |
| R15 | `llama3.2:3b-hermes-64k` retorna JSON/tool-call-like via wrapper Hermes | IA/Hermes | Média | Alta | Testes Hermes recentes retornaram `{"name": ...}` | Respostas inválidas/automação quebrada | Não usar como default; investigar prompt/schemas finais | P1 | Dev IA |
| R16 | Qwen3 teve comportamento inconsistente em docs de benchmark | IA local | Média | Média | Docs e ai-lab indicam investigação de empty/thinking responses | Default local instável | Não promover Qwen3; manter experimental | P2 | Dev IA |
| R17 | Migrations não validadas contra DB online nesta auditoria | Banco | Média | Média | Apenas `alembic heads` foi rodado | Estado real do DB local pode divergir | Rodar `alembic current/check` só com DB local seguro | P1 | Backend/DB |
| R18 | Constraints únicas de asset podem conflitar com import sujo | Banco/imports | Alta | Média | `Asset.serial` e `Asset.patrimony` unique | Falha em apply ou conflito indevido | Normalização/conflito antes de apply; testes com duplicados | P1 | Backend/DB |
| R19 | Grande volume de docs/reports antigos e auditorias | Documentação | Baixa | Alta | Centenas de docs/reports tracked/untracked | Dificulta encontrar fonte de verdade | Consolidar docs e arquivar temporários após revisão | P2 | Produto/Dev |
| R20 | Frontend depende de build, mas não há teste automatizado de UI | Frontend/QA | Média | Alta | `package.json` só tem `dev`, `build`, `preview` | Regressões visuais não detectadas pelo CI | Adicionar smoke visual/manual ou Playwright em fase própria | P2 | Frontend/QA |
| R21 | `assets/`, `_migration_proposals/`, `imports/` e exports contêm muitos artefatos | Higiene/release | Média | Alta | Untracked e diretórios grandes | Commit pesado ou teste contaminado | Classificar/quarentenar antes de commit | P1 | Dev |
| R22 | Alguns endpoints retornam ORM sob response_model | Backend/API | Baixa | Média | Rotas usam `response_model` com retorno ORM | Risco futuro de campos acidentais se schemas mudarem | Manter DTOs explícitos e testes de contrato | P2 | Backend |
| R23 | Legado exige CSP menos estrito | Segurança/legado | Média | Média | `/admin` e `/assinaturas` usam CSP com inline compat | Superfície maior de XSS no legado | Isolar legado e manter report-only estrito; não remover sem plano | P2 | Backend/Sec |
| R24 | AI/Ollama docs e ai-lab podem estar desorganizados | IA/docs | Baixa | Alta | Muitos arquivos `docs/HERMES*`, `OLLAMA*`, `LOCAL_AI*`, `ai-lab` | Decisão futura confusa | Consolidar recomendação atual; arquivar resultados temporários | P2 | Dev IA |

## Riscos bloqueadores

Antes de qualquer commit ou edição ampla:

1. R01 — Worktree sujo e misturado.
2. R02 — Possível segredo em `tools/composio_client.py`.
3. R03 — Possível chave em `.vscode/settings.json`.
4. R04 — Presença de `.env.bak_*` no diretório.
5. R06 — CSS com remoção massiva sem smoke visual.
6. R07 — Refatoração de import pipeline incompleta/fragmentada.

## Riscos antes de editar backend

- R01: worktree sujo.
- R07/R08: import pipeline em refatoração e serviço grande.
- R09: fluxo macro/movimentação precisa regressão dedicada.
- R12/R13: CORS/rate limit global.
- R17/R18: DB/migrations/constraints.

## Riscos antes de editar frontend

- R06: CSS global alterado massivamente.
- R20: ausência de teste UI automatizado.
- R09: frontend participa do fluxo movimento -> macro -> copiar.
- R01: alterações frontend já misturadas com backend.

## Riscos antes de mexer em banco

- R17: DB online não validado nesta auditoria.
- R18: constraints únicas em dados de importação sujos.
- R04: não tocar dumps/backups/DB reais sem confirmação.
- Migrations destrutivas proibidas sem plano explícito.

## Riscos antes de integrar IA/local

- R14: IA Chat deve permanecer textual, sem agency.
- R15: llama local não confiável via wrapper Hermes.
- R16: Qwen3 não promovido.
- R24: docs e scripts ai-lab precisam consolidação.
- R02: Composio/API keys não podem ficar hardcoded.

## Mitigação prioritária

1. S0 triage de worktree.
2. Remover ou isolar possíveis secrets untracked.
3. Rodar gates direcionados sempre com escopo (`tests`, não árvore inteira).
4. Separar próximas edições por domínio.
5. Só depois evoluir backend/frontend/banco/IA.
