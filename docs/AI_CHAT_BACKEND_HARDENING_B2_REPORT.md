# AI Chat Backend Hardening B2 Report

## 1. Resumo Executivo

A boundary `B2 — AI Chat/backend hardening` foi fechada com sucesso funcional e ressalva operacional.

- O rate limit Redis do AI Chat não usa mais `eval`.
- O renderer SVG do frontend não usa mais `dangerouslySetInnerHTML`.
- Os testes dedicados do recorte B2 passaram.
- O build do frontend foi executado nesta rodada final e falhou por limitação ambiental do shell WSL/Windows UNC, não por regressão funcional do renderer.

## 2. Status Final B2

`GO COM RESSALVAS`

Motivo da ressalva:

- o backend ficou validado;
- a evidência do frontend foi confirmada por teste e por leitura estática;
- o `npm run build` no shell WSL desta sessão falhou por ambiente (`CMD.EXE` em caminho UNC e `tsc` não reconhecido).

## 3. Achados HIGH Fechados

1. Redis rate limit sem `eval`.
2. Renderer SVG sem `dangerouslySetInnerHTML`.

## 4. Evidência Rate Limit Redis Sem `eval`

Arquivo principal:

- [backend/app/domains/ai_chat/rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/ai_chat/rate_limit.py)

Evidência:

- `RedisRateLimitStore.increment()` usa `SET key 1 EX ttl NX` e `INCR key`.
- `AiChatRateLimiter.build_key()` deriva a chave de `user_id` hash + janela temporal.
- Não há script Lua nem `eval` no caminho atual.

## 5. Evidência 429 / 503 / Fallback Local

Arquivo principal:

- [backend/app/domains/ai_chat/rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/ai_chat/rate_limit.py)

Comportamento validado:

- retorna `429 ai_chat_rate_limit_exceeded` quando o limite por janela é ultrapassado;
- retorna `503 ai_chat_rate_limit_unavailable` quando Redis falha fora de `local`;
- mantém fallback em memória quando o ambiente é `local`.

Teste dedicado:

- [tests/test_ai_chat_rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_rate_limit.py)

## 6. Evidência Renderer SVG Sem `dangerouslySetInnerHTML`

Arquivo principal:

- [frontend/itam-platform/src/components/icons/HermesIcons.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/icons/HermesIcons.tsx)

Evidência:

- o renderer usa `DOMParser` + whitelist de tags SVG;
- a serialização de nós passa por `renderSvgNode`;
- `dangerouslySetInnerHTML` não aparece no arquivo.

Teste dedicado:

- [tests/test_hermes_icons_security.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_hermes_icons_security.py)

## 7. Testes Backend Executados

Comandos executados nesta rodada de fechamento:

```bash
PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests
timeout 120 .venv/bin/python -m ruff check backend/app/api/v1/routes/ai_chat.py backend/app/domains/ai_chat tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_security_headers.py tests/test_hermes_icons_security.py
PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_security_headers.py tests/test_hermes_icons_security.py -q -o addopts=''
PYTHONPATH=backend timeout 180 .venv/bin/python -m pytest tests/test_ai_chat_api.py tests/test_ai_chat_hardening.py tests/test_ai_chat_provider_mock.py tests/test_security_headers.py tests/test_hermes_icons_security.py -q -s -o addopts=''
```

Resultado:

- `compileall`: passou.
- `ruff`: passou.
- `pytest`: a primeira execução falhou por um problema de captura no encerramento; o retry com `-s` passou com `30` testes e `1` warning.

## 8. Frontend Build Executado

Comando executado:

```bash
cd frontend/itam-platform && timeout 180 npm run build
```

Resultado:

- Falhou no shell WSL desta sessão.
- Saída relevante:
  - `CMD.EXE` iniciou em caminho UNC.
  - o caminho UNC foi reduzido para a pasta do Windows.
  - `tsc` não foi reconhecido como comando interno ou externo.
- Classificação: limitação ambiental, não regressão do renderer.

## 9. Scanner Redigido

Escopo do scanner nesta rodada:

- [backend/app/domains/ai_chat/rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/ai_chat/rate_limit.py)
- [backend/app/api/v1/routes/ai_chat.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/api/v1/routes/ai_chat.py)
- [backend/app/main.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/main.py)
- [tests/test_ai_chat_rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_rate_limit.py)
- [tests/test_ai_chat_hardening.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_hardening.py)
- [tests/test_ai_chat_provider_mock.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_provider_mock.py)
- [tests/test_security_headers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_security_headers.py)
- [tests/test_hermes_icons_security.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_hermes_icons_security.py)
- [frontend/itam-platform/src/components/icons/HermesIcons.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/icons/HermesIcons.tsx)
- [docs/CRITICAL_FIX_ROUND2_MANIFEST.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_MANIFEST.md)
- [docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md)
- [docs/audit/HIGH_FIX_ROUND3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/HIGH_FIX_ROUND3_REPORT.md)

Classificação resumida:

- `eval` em `rate_limit.py`: resolvido.
- `dangerouslySetInnerHTML` em `HermesIcons.tsx`: resolvido.
- `COMPOSIO_API_KEY`: aparece apenas como nome de variável de ambiente em `docs/audit/NEXT_BOUNDARY_DECISION.md`; classificação `esperado`.
- `secret`, `token`, `password`, `bearer`, `sk-`, `private_key`: aparecem apenas em asserções negativas, nomes de teste ou histórico documental; classificação `esperado` ou `resolvido`.
- Menções a `eval`/`dangerouslySetInnerHTML` em relatórios: esperadas e históricas.

## 10. Arquivos Funcionais Envolvidos

- [backend/app/domains/ai_chat/rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/domains/ai_chat/rate_limit.py)
- [backend/app/api/v1/routes/ai_chat.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/api/v1/routes/ai_chat.py)
- [backend/app/main.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/backend/app/main.py)
- [frontend/itam-platform/src/components/icons/HermesIcons.tsx](/home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform/src/components/icons/HermesIcons.tsx)

## 11. Arquivos de Teste Envolvidos

- [tests/test_ai_chat_rate_limit.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_rate_limit.py)
- [tests/test_ai_chat_hardening.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_hardening.py)
- [tests/test_ai_chat_provider_mock.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_ai_chat_provider_mock.py)
- [tests/test_security_headers.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_security_headers.py)
- [tests/test_hermes_icons_security.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tests/test_hermes_icons_security.py)

## 12. Riscos Remanescentes

- O build do frontend continua dependente do ambiente que executa `npm` dentro do WSL/UNC.
- O renderer SVG aceita apenas tags permitidas pela whitelist atual.
- O worktree geral segue misturado com outras boundaries anteriores.

## 13. Itens Fora de Escopo

- `backend/app/domains/imports/`
- pipeline de import/staging/Lansweeper
- migrations
- Docker/Compose
- remake amplo do frontend
- `.env`, `.env.*`, dumps, bancos, tokens e credenciais

## 14. Próxima Boundary Recomendada

`B3 — Import pipeline/staging`

Motivo:

- `B2` está fechado;
- `B3` é a próxima boundary funcional natural no roadmap já documentado;
- o backend hardening de AI Chat não precisa bloquear a refatoração controlada do importador.
