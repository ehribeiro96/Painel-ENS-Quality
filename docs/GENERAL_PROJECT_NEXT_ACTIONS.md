# Próximas ações recomendadas — Painel ENS-Quality

Data: 2026-06-12 09:13:51 -03
Origem: auditoria geral não destrutiva
Status: usar como checklist antes da próxima edição funcional
Índice operacional consolidado: [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
Decisão de próxima boundary: [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md)

## Próximas 10 ações recomendadas

1. Fazer triage formal do worktree antes de qualquer edição nova.
   - Separar tracked/untracked por: backend real, frontend real, testes, docs, artefatos, sensíveis e incertos.
   - Não commitar nada nesta etapa sem revisão humana.

2. Isolar possíveis segredos/credenciais untracked.
   - `tools/composio_client.py` contém indício redigido de `COMPOSIO_API_KEY`/`api_key`.
   - `.vscode/settings.json` contém indício redigido de `CodeGPT.apiKey`.
   - Não imprimir valores; remover ou substituir por env/credential store em rodada específica.

3. Confirmar política para `.env.bak_20260603_132713`.
   - O arquivo existe e não foi lido.
   - Deve permanecer fora do Git e idealmente fora da raiz do repo se contiver segredo real.

4. Consolidar documentação de Hermes/Ollama/AI local.
   - Fonte de verdade atual: Codex default, contexto 262144, `tool_use_enforcement: true`.
   - `qwen2.5-coder:7b-hermes-64k` só manual.
   - `llama3.2:3b-hermes-64k` e Qwen3 não recomendados como default.

5. Corrigir/limitar descoberta de testes antes de rodar pytest sem escopo.
   - Comando seguro atual: `PYTHONPATH=backend .venv/bin/python -m pytest tests -q -o addopts=''`.
   - Evitar `pytest` na raiz sem escopo enquanto `_validation/`, `exports/` e `imports/` interferem.

6. Fazer baseline visual do frontend antes de mexer em UX/UI.
   - `styles.css` teve remoção grande.
   - Validar dashboard, assets, imports, macros, audit logs, settings e AI Chat.

7. Antes de editar imports/Lansweeper, consolidar refatoração já presente.
   - Novos módulos untracked de classification/normalization/parsing existem.
   - Rodar suíte dedicada de imports antes e depois.

8. Antes de editar fluxo Ativo -> Movimentação -> Macro, criar checklist E2E.
   - Ativo move salva movimento.
   - Macro só gera após movimento salvo.
   - Histórico mostra movimento.
   - Copiar macro marca `MacroGeneration.copied`.

9. Ativar/validar Docker WSL integration se a próxima fase envolver deploy/runtime.
   - `docker compose config --services` falhou porque Docker não está disponível nesta distro WSL.

10. Só mexer em migrations após DB local seguro confirmado.
    - Rodar apenas `alembic heads` como leitura geral.
    - `alembic current/check/upgrade` só com confirmação de DB local e backup.

## O que não fazer agora

- Não commitar o worktree atual como está.
- Não apagar untracked em massa.
- Não mover/editar `.env`, `.env.bak`, dumps, bancos ou evidências reais sem autorização explícita.
- Não editar importação Lansweeper antes de triage e suíte dedicada.
- Não editar `MoveAssetDialog` ou macro/movimentação sem plano E2E.
- Não criar migration agora.
- Não rodar migrations destrutivas.
- Não promover Ollama como default.
- Não promover Qwen3.
- Não usar `llama3.2:3b-hermes-64k` como default.
- Não rodar benchmark Ollama nesta fase.
- Não rodar `pytest` na raiz sem escopo enquanto a árvore contém exports/validation/imports com testes duplicados.
- Não confiar em build frontend como substituto de smoke visual.

## Primeiro prompt recomendado para a próxima rodada

```text
Você está em GPT_CODEX no projeto Painel ENS-Quality.

Objetivo: fazer uma triagem controlada do worktree antes de qualquer edição funcional.

Regras:
1. Não alterar código.
2. Não apagar arquivos.
3. Não fazer commit.
4. Não ler `.env`, `.env.bak`, dumps, bancos, tokens ou credenciais.
5. Não expor secrets.
6. Mostrar `git status --short --branch` antes e depois.
7. Classificar tracked e untracked em: backend real, frontend real, testes, docs, artefatos, sensíveis/não versionáveis, incertos.
8. Gerar/atualizar `docs/WORKTREE_TRIAGE_REPORT.md` com commit boundaries recomendados e itens que exigem revisão humana.
9. Rodar somente validações seguras: `compileall`, `ruff`, `pytest tests -q -o addopts=''`, `npm run build`, `alembic heads`.
10. Se encontrar possível segredo, registrar apenas caminho/linha aproximada/contexto redigido.

Comece por `git status --short --branch`.
```

## Validações-base recomendadas para qualquer próxima edição

Backend geral:

```bash
PYTHONPATH=backend .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts
PYTHONPATH=backend .venv/bin/python -m ruff check backend tests scripts
PYTHONPATH=backend .venv/bin/python -m pytest tests -q -o addopts=''
```

Frontend:

```bash
cd frontend/itam-platform && npm run build
```

Migrations leitura:

```bash
cd backend && ../.venv/bin/python -m alembic heads
```

Imports/Lansweeper:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_import_* tests/test_imports_regression.py tests/test_import_pipeline_units.py -q -o addopts=''
```

Macros/movimentação/assets:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_assets_regression.py tests/test_macros_module.py tests/test_macros_audit_operational.py -q -o addopts=''
```

AI Chat:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_ai_chat_rate_limit.py -q -o addopts=''
```

## Ordem recomendada para começar a editar

1. Higiene/triage do worktree.
2. Saneamento de possíveis secrets untracked.
3. Estabilização de teste/build/discovery.
4. AI Chat/rate limit se for concluir mudanças já iniciadas.
5. Imports/Lansweeper em fase própria.
6. Fluxo Ativo -> Movimentação -> Macro em fase própria.
7. Frontend/UX após baseline visual.
8. Banco/migrations somente após DB local confirmado.
9. IA/Hermes/Ollama somente como consolidação documental/experimental, sem default local.
