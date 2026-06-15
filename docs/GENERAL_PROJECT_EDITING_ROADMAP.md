# Roadmap seguro de edição do Painel ENS-Quality

Data: 2026-06-12 09:13:51 -03
Base: auditoria geral não destrutiva do projeto
Status: plano recomendado, sem execução de alterações funcionais

## Princípios obrigatórios

1. Não misturar feature, refatoração, visual, segurança e documentação no mesmo pacote.
2. Não editar importação Lansweeper/staging sem plano dedicado e testes específicos.
3. Não editar fluxo Ativo -> Movimentação -> Macro -> Histórico -> Copiar macro sem testes de regressão.
4. Não editar migrations sem backup, plano de rollback e ambiente local confirmado.
5. Não mexer em `.env`, secrets, dumps, bancos ou evidências reais.
6. Não promover Ollama como default.
7. Não promover Qwen3.
8. Manter Hermes default em Codex.
9. Antes de qualquer edição: revalidar `git status --short --branch`.
10. Depois de cada fase: rodar gates mínimos e registrar falhas sem mascarar.

## Ordem recomendada de intervenção

1. S0 — Congelamento e higiene.
2. S1 — Estabilização de testes/build e saneamento de descoberta.
3. S2 — Backend por domínio, começando por áreas pequenas e cobertas.
4. S3 — Frontend/UX, com foco em recuperar confiança visual após alteração grande de CSS.
5. S4 — Banco/migrations, apenas depois de DB local seguro e plano de rollback.
6. S5 — IA/Hermes/Ollama, mantendo local como manual/experimental.

---

## S0 — Congelamento e higiene

### Objetivo

Criar uma base segura para editar sem misturar mudanças pré-existentes, auditoria, experimentos de IA e alterações funcionais.

### Arquivos/diretórios prováveis

- `docs/WORKTREE_TRIAGE_REPORT.md`
- `docs/GENERAL_PROJECT_AUDIT_REPORT.md`
- `docs/GENERAL_PROJECT_RISK_REGISTER.md`
- `docs/GENERAL_PROJECT_NEXT_ACTIONS.md`
- `_audit_findings/`
- `.gitignore` somente se houver autorização explícita

### Ações recomendadas

1. Classificar mudanças rastreadas por tema:
   - AI Chat backend/tests.
   - Import service/refatoração Lansweeper.
   - Frontend visual/AppShell/pages.
   - CSS global.
2. Classificar untracked:
   - fonte/teste útil;
   - documentação útil;
   - artefato temporário;
   - risco sensível/não versionável.
3. Tratar como bloqueadores antes de commit:
   - `tools/composio_client.py` com possível API key hardcoded;
   - `.vscode/settings.json` com possível `CodeGPT.apiKey`;
   - `.env.bak_20260603_132713` presente no diretório;
   - `_validation/`, `exports/`, `imports/` interferindo em descoberta de testes quando pytest é executado sem escopo.
4. Definir commit boundaries, mas não commitar sem autorização.

### Riscos

- Perder contexto de alterações úteis se descartar untracked sem revisão.
- Commit acidental de segredo ou artefato pesado.
- Test discovery contaminado por cópias em `_validation/`, `exports/`, `imports/`.

### Critérios de aceite

- Relatório de triage atualizado.
- Lista explícita do que será commitado, ignorado, arquivado ou removido com aprovação humana.
- Nenhum segredo real impresso ou versionado.
- Próxima edição aponta para um único domínio.

### Comandos de validação

```bash
git status --short --branch
git diff --name-status
git diff --cached --name-status
git ls-files --others --exclude-standard | head -200
PYTHONPATH=backend .venv/bin/python -m pytest tests --collect-only -q -o addopts=''
```

### Rollback

- Não há rollback automático porque S0 deve ser majoritariamente documentação/triage.
- Se algum arquivo de relatório for indesejado: remover apenas após autorização.
- Se `.gitignore` for alterado em futura rodada: `git restore .gitignore` antes de commit.

---

## S1 — Estabilização

### Objetivo

Garantir que o projeto continue com gates básicos verdes antes de qualquer alteração funcional nova.

### Arquivos prováveis

- `pyproject.toml` se for necessário ajustar exclusões de pytest/ruff, somente com aprovação.
- `tests/` para correções pontuais de teste, se necessário.
- `frontend/itam-platform/package.json` somente se scripts forem adicionados com aprovação.
- Docs de validação.

### Riscos

- Ajustar discovery de testes de forma ampla e esconder cobertura real.
- Confundir falha ambiental Docker com bug de produto.
- Corrigir teste sem corrigir causa.

### Critérios de aceite

- `compileall` OK.
- `ruff` OK.
- `pytest tests` OK.
- `npm run build` OK.
- `alembic heads` OK.
- Docker documentado como indisponível se WSL integration continuar ausente.

### Comandos de validação

```bash
PYTHONPATH=backend .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts
PYTHONPATH=backend .venv/bin/python -m ruff check backend tests scripts
PYTHONPATH=backend .venv/bin/python -m pytest tests -q -o addopts=''
cd frontend/itam-platform && npm run build
cd backend && ../.venv/bin/python -m alembic heads
```

### Rollback

- Para correções de teste/config: `git restore <arquivo>` antes de commit.
- Não alterar DB nem Docker nesta fase.

---

## S2 — Backend

### Objetivo

Evoluir backend com menor risco, preservando auth/RBAC, auditoria, DTOs, transações e fluxos críticos.

### Ordem recomendada

1. AI Chat/rate limit, porque já há mudanças e testes novos.
2. Imports refactor, somente depois de consolidar arquivos untracked e testes de importação.
3. Assets/movements/macros, somente com teste end-to-end dedicado.
4. Search/dashboard/audit, se necessário e com baixo acoplamento.

### Arquivos prováveis

- `backend/app/api/v1/routes/ai_chat.py`
- `backend/app/domains/ai_chat/*`
- `backend/app/domains/imports/service.py`
- `backend/app/domains/imports/classification/*`
- `backend/app/domains/imports/normalization/*`
- `backend/app/domains/imports/parsing/*`
- `backend/app/domains/assets/service.py`
- `backend/app/domains/macros/service.py`
- `backend/app/api/v1/routes/assets.py`
- `backend/app/api/v1/routes/macros.py`
- testes correlatos em `tests/`

### Riscos

- Importação Lansweeper é altamente sensível: normalização errada pode trocar IP por hostname, perder identidade ou sobrescrever ativo indevidamente.
- Macro/movimentação precisa respeitar: macro oficial só depois da movimentação salva.
- AI Chat não pode executar ações operacionais nem vazar prompt/key em metadados/logs.
- Alterações em middleware/rate limit podem afetar todas as APIs.

### Critérios de aceite

- DTO explícito em toda rota alterada.
- RBAC preservado.
- Auditoria/histórico preservados em mutações.
- Testes específicos do domínio passando.
- Testes globais passando ao final.

### Comandos de validação

Para AI Chat:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_ai_chat_rate_limit.py -q -o addopts=''
```

Para imports:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_import_* tests/test_imports_regression.py tests/test_import_pipeline_units.py -q -o addopts=''
```

Para assets/movements/macros:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_assets_regression.py tests/test_macros_module.py tests/test_macros_audit_operational.py -q -o addopts=''
```

Gate final:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests -q -o addopts=''
PYTHONPATH=backend .venv/bin/python -m ruff check backend tests scripts
```

### Rollback

- Reverter patch por arquivo com `git restore <arquivo>` para tracked.
- Remover/arquivar untracked somente com autorização.
- Não rodar migrations para rollback de backend puro.

---

## S3 — Frontend

### Objetivo

Estabilizar UX/UI e integração com API sem alterar contratos backend.

### Ordem recomendada

1. Validar impacto da redução de `styles.css`.
2. Verificar `AppShell`, navegação, auth refresh e role guards.
3. Testar Assets/MoveAssetDialog/Macros manualmente ou com smoke visual.
4. Refatorar páginas grandes em componentes menores somente depois de baseline visual.

### Arquivos prováveis

- `frontend/itam-platform/src/styles.css`
- `frontend/itam-platform/src/components/AppShell.tsx`
- `frontend/itam-platform/src/components/StateBlocks.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/pages/ImportsPage.tsx`
- `frontend/itam-platform/src/pages/AuditLogsPage.tsx`
- `frontend/itam-platform/src/pages/SettingsPage.tsx`
- `frontend/itam-platform/src/lib/api.ts`

### Riscos

- Grande remoção de CSS pode quebrar classes não óbvias.
- Componentes grandes concentram estado e mutações.
- Frontend pode ocultar problemas de autorização que precisam estar no backend.

### Critérios de aceite

- `npm run build` OK.
- Rotas principais carregam.
- Estados loading/error/empty visíveis.
- Actions sensíveis desabilitadas por role no frontend e bloqueadas no backend.
- Sem regressão visual óbvia em dashboard/assets/imports/macros/AI Chat.

### Comandos de validação

```bash
cd frontend/itam-platform && npm run build
```

Se houver ambiente browser disponível em rodada futura:

```bash
cd frontend/itam-platform && npm run dev
```

E smoke visual em browser contra rotas principais.

### Rollback

- `git restore frontend/itam-platform/src/styles.css` se a regressão visual vier do CSS.
- Reverter por página/componente quando o patch for isolado.

---

## S4 — Banco

### Objetivo

Evoluir migrations/constraints/índices com segurança e sem risco a dados reais.

### Pré-condições

- DB local de desenvolvimento confirmado, nunca produção.
- Backup local ou volume descartável.
- `alembic heads` OK.
- `alembic current` somente contra DB local confirmado.

### Arquivos prováveis

- `backend/alembic/versions/*`
- `backend/app/domains/*/models.py`
- `tests/test_migrations_regression.py`

### Riscos

- Constraints em `serial`/`patrimony` podem falhar com dados duplicados reais.
- JSONB de import staging pode crescer e exigir estratégia de retenção/índices.
- Migration destrutiva sem revisão pode perder dados.

### Critérios de aceite

- Migration autônoma e reversível quando possível.
- Sem SQL destrutivo sem plano explícito.
- Testes de migration e modelos passando.
- `alembic upgrade head` somente em ambiente local autorizado.

### Comandos de validação

Leitura segura:

```bash
cd backend && ../.venv/bin/python -m alembic heads
```

Somente com DB local confirmado:

```bash
cd backend && ../.venv/bin/python -m alembic current
cd backend && ../.venv/bin/python -m alembic check
```

Aplicação local, somente com autorização:

```bash
cd backend && ../.venv/bin/python -m alembic upgrade head
```

### Rollback

- Para migration nova ainda não aplicada: remover arquivo migration com autorização.
- Para migration aplicada localmente: usar downgrade específico apenas com plano e backup.
- Nunca executar rollback em produção nesta rotina.

---

## S5 — IA/Hermes/Ollama

### Objetivo

Manter IA operacional e segura sem contaminar o produto com modelos locais instáveis.

### Estado recomendado

- Hermes default: `openai-codex` / `gpt-5.5`.
- `model.context_length: 262144`.
- `agent.tool_use_enforcement: true`.
- Ollama LAN apenas uso explícito.
- Coder local manual: `qwen2.5-coder:7b-hermes-64k`.
- `llama3.2:3b-hermes-64k` não recomendado via wrapper Hermes.
- Qwen3 não recomendado.

### Arquivos prováveis

- `docs/HERMES_*`
- `docs/OLLAMA_*`
- `docs/LOCAL_AI_*`
- `ai-lab/ollama-benchmark/*`
- `ai-lab/ollama-modelfiles/*`
- `backend/app/domains/ai_chat/*`

### Riscos

- Promover Ollama como default quebraria respostas simples e automações.
- Llama local imita tool-call JSON como texto.
- Benchmark/scripts podem conter resultados/artefatos que não devem virar produto.
- Provider real de AI Chat deve continuar sem agency operacional.

### Critérios de aceite

- Codex continua default.
- AI Chat do produto continua mock/offline por padrão seguro quando aplicável.
- Docs locais consolidadas.
- Nenhum segredo em prompts/scripts.
- Sem alteração em `~/.hermes/config.yaml` sem backup e autorização explícita.

### Comandos de validação

```bash
hermes config
hermes chat -q "Responda somente: CODEX_OK"
hermes chat -q "Responda somente: CODER_OK" --provider ollama-lan --model qwen2.5-coder:7b-hermes-64k
```

Não rodar benchmark Ollama sem autorização específica.

### Rollback

- Para docs/prompts: `git restore docs/... ai-lab/...` se rastreados.
- Para config Hermes: restaurar backup timestamped criado na rodada de config.

---

## Primeiro pacote recomendado

Começar por S0/S1, não por feature.

Prompt recomendado para próxima rodada:

```text
Faça uma triagem controlada do worktree do Painel ENS-Quality. Não altere código. Classifique mudanças tracked/untracked em: backend real, frontend real, testes, docs, artefatos, sensíveis/não versionáveis e incertos. Não leia .env nem secrets. Produza docs/WORKTREE_TRIAGE_REPORT.md atualizado e uma proposta de commit boundaries, sem commit e sem apagar arquivos.
```
