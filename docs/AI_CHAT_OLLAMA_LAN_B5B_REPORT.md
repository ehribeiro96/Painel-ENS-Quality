# AI Chat Ollama LAN B5-B Report

## 1. Resumo executivo

Status desta boundary: `PARTIAL`.

Atualização B5-D: o default do provider `ollama-lan` passou a ser `qwen3:1.7b-64k`; este relatório mantém o histórico da validação B5-B.

Foi implementado no backend FastAPI o provider real `ollama-lan`, separado do provider `ollama` local B5-A. O novo provider usa o endpoint OpenAI-compatible do Ollama LAN e monta chamadas para `/v1/chat/completions`, sem `/api/chat`, sem mock e sem fallback silencioso para mock.

A validação local de código, testes backend e build frontend passou. A validação direta do host LAN real e o smoke UI autenticado não foram concluídos nesta execução: a primeira tentativa de curl para o IP LAN não retornou corpo visível e a segunda tentativa diagnóstica detalhada foi negada pelo fluxo de aprovação do comando; o navegador permaneceu na tela de login após a confirmação manual, então não houve sessão autenticada utilizável para enviar a mensagem na UI.

## 2. Diferença entre B5-A e B5-B LAN

- B5-A: provider `ollama`, backend -> `http://127.0.0.1:11434/api/chat`, formato nativo Ollama, loopback-only.
- B5-B: provider `ollama-lan`, backend -> `http://192.168.0.103:11434/v1/chat/completions`, formato OpenAI-compatible, LAN permitida somente por allowlist explícita.

O provider B5-A foi preservado para compatibilidade local e continua usando `/api/chat`. O provider B5-B não usa `/api/chat`.

## 3. Provider usado

Provider runtime implementado: `ollama-lan`.

Aliases aceitos:

- `AI_CHAT_PROVIDER=ollama-lan`
- `AI_PROVIDER=ollama-lan`

Quando ambos existem, `AI_CHAT_PROVIDER` tem prioridade por `AliasChoices` no `Settings`.

## 4. Base URL usada

Base URL configurada para B5-B:

```text
http://192.168.0.103:11434/v1
```

A URL completa não é exposta no health do AI Chat.

## 5. Endpoint backend -> Ollama

Endpoint final formado pelo backend:

```text
http://192.168.0.103:11434/v1/chat/completions
```

Teste unitário dedicado valida que a URL final é exatamente essa e que não contém `/api/chat`.

## 6. Modelo usado

Modelo configurado/testado em payload fake e runtime temporário:

```text
qwen2.5-coder:7b
```

Nenhum modelo foi baixado automaticamente.

## 7. Como foi garantido que não era mock

- `build_ai_provider(settings)` agora seleciona `OllamaLanProvider` quando o provider normalizado é `ollama-lan`.
- `OllamaLanProvider.provider == "ollama-lan"`.
- Falhas de transporte geram `AiProviderRequestError` (`ollama_lan_request_failed`, `ollama_lan_timeout`, etc.).
- Não há fallback para `MockAiProvider` em falhas do provider LAN.
- Teste `test_ollama_lan_failure_does_not_fallback_to_mock` valida que uma falha de conexão vira erro controlado e não resposta mock.

## 8. Como foi garantido que frontend não chama Ollama direto

- Nenhuma alteração visual/frontend foi feita.
- O frontend continua usando o client existente para `/api/v1/ai-chat/*`.
- Os schemas de request do AI Chat não aceitam `OLLAMA_BASE_URL` como contrato válido.
- Não foi criado endpoint que aceita URL arbitrária.
- O provider só lê `OLLAMA_BASE_URL` do backend/runtime.
- Network check no browser não encontrou chamadas para `192.168.0.103`, `/v1/chat/completions` ou `/api/chat`; porém essa checagem ocorreu sem sessão autenticada efetiva, então não substitui o smoke UI completo.

## 9. Allowlist de host

Novo setting backend:

```text
OLLAMA_ALLOWED_HOSTS=localhost,127.0.0.1,::1,192.168.0.103
```

Regras implementadas:

- `192.168.0.103` só é aceito quando aparece explicitamente na allowlist.
- Wildcard (`*`, `0.0.0.0/0`, `::/0`) é rejeitado.
- IP público é rejeitado mesmo se listado.
- Host não listado é rejeitado.
- Hostname arbitrário não é aceito como host seguro.

## 10. Segurança aplicada

- Backend-only: browser não recebe base URL do Ollama.
- Health não expõe `OLLAMA_BASE_URL`.
- Erros são códigos sanitizados, sem stack trace e sem payload completo.
- `AI_CHAT_PROVIDER=ollama-lan` e `AI_PROVIDER=ollama-lan` não caem para mock.
- `OLLAMA_BASE_URL` com `/v1` não duplica `/v1`.
- `OLLAMA_BASE_URL` sem path, para `ollama-lan`, é normalizado para incluir `/v1` antes de `/chat/completions`.
- Nenhuma secret real foi lida ou impressa.
- `.env` real não foi lido nem alterado.

## 11. Teste direto `/v1/models`

Resultado desta execução: `PENDENTE / NÃO VALIDADO`.

Comando inicial executado com `curl -s` não retornou corpo visível. A tentativa seguinte com `curl -i -sS` para diagnosticar status/erro foi negada pelo fluxo de aprovação do comando. Por isso, não foi possível confirmar resposta real de `/v1/models` nesta rodada.

## 12. Teste direto `/v1/chat/completions`

Resultado desta execução: `PENDENTE / NÃO VALIDADO`.

O payload OpenAI-compatible foi preparado para `qwen2.5-coder:7b`, mas a validação real contra `http://192.168.0.103:11434/v1/chat/completions` não foi concluída pelos mesmos bloqueios da seção anterior.

## 13. Teste backend com provider real

Resultado desta execução: `PARCIAL`.

- Backend temporário subiu em `127.0.0.1:8001` com `AI_CHAT_PROVIDER=ollama-lan`, `AI_PROVIDER=ollama-lan`, `OLLAMA_BASE_URL=http://192.168.0.103:11434/v1`, modelo `qwen2.5-coder:7b` e allowlist contendo `192.168.0.103`.
- `/health` respondeu HTTP 200.
- `/api/v1/ai-chat/health` sem token respondeu HTTP 401 `missing_token`, conforme esperado para rota protegida.
- A chamada autenticada real que acionaria o provider LAN não foi concluída, porque a sessão manual não ficou ativa no browser.

## 14. Smoke autenticado na UI

Resultado: `PENDENTE`.

O navegador abriu `http://127.0.0.1:8001/login`. Após a confirmação manual de autenticação, navegar para `/ai-chat` ainda mostrou a tela de login. Não foram lidos token/cookie/localStorage e nenhuma credencial foi manipulada pelo agente.

## 15. Screenshots

Diretório reservado para evidências:

```text
docs/audit/screenshots/b5b-ollama-lan/
```

Nenhum screenshot autenticado foi gerado porque o smoke UI não chegou à página `/ai-chat` autenticada.

## 16. Resultado build

Frontend build:

```text
nvm use 22.22.3
npm run build
PASS
```

Saída principal: TypeScript e Vite build passaram; bundle gerado em `frontend/itam-platform/dist`.

## 17. Resultado testes

Backend:

```text
PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests
PASS

PYTHONPATH=backend timeout 120 .venv/bin/python -m ruff check ...
PASS — All checks passed!

PYTHONPATH=backend timeout 240 .venv/bin/python -m pytest ... -q -o addopts=''
PASS — 53 passed, 1 warning
```

Teste dedicado isolado do provider:

```text
PYTHONPATH=backend timeout 120 .venv/bin/python -m pytest tests/test_ai_chat_ollama_provider.py -q -o addopts=''
PASS — 18 passed
```

## 18. Scanner redigido

Scanner redigido executado sobre arquivos alterados desta boundary classificou:

- nomes de variáveis esperados: `OLLAMA_BASE_URL`, `OLLAMA_ALLOWED_HOSTS`, `OLLAMA_MODEL`;
- IP LAN documentado permitido: `192.168.0.103`;
- localhost/loopback permitidos;
- termos `token`, `secret`, `password` aparecem apenas em nomes de variáveis existentes, placeholders ou textos de segurança, sem valores reais impressos;
- nenhum segredo real identificado.

## 19. Limitações

- Não foi possível validar o host LAN real `/v1/models` e `/v1/chat/completions` nesta execução.
- Não foi possível concluir smoke autenticado na UI.
- Health de `/api/v1/ai-chat/health` é protegido por autenticação; sem sessão válida retorna `missing_token`.
- A confirmação de resposta real do modelo LAN permanece pendente.

## 20. Próximo passo recomendado

B5-C foi executada como validação operacional real e registrada em `docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md`.

Resultado B5-C:

- TCP LAN: OK.
- `/v1/models`: OK, com `qwen2.5-coder:7b` disponível.
- `/v1/chat/completions`: OK, com `choices[0].message.content = OK via Ollama LAN.`.
- Provider backend direto: OK, `OllamaLanProvider`, provider `ollama-lan`, sem mock.
- UI autenticada: pendente; sessão do navegador não permaneceu autenticada em `127.0.0.1:8001`.

Próxima boundary recomendada: `B5-D — AI Chat authenticated UI session fix/validation`, focada somente em autenticação/sessão UI e smoke `/ai-chat`, sem nova alteração no provider se o runtime LAN continuar OK.
