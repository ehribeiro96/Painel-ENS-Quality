# P1 Apoema Fallback Fix - 2026-06-23

## 1. Bugs corrigidos
- BUG-001 - Apoema `sendAiMessage` mascara falha de API/auth com resposta mock
- BUG-002 - Apoema `getAiProviders` oculta 401 atras do catalogo default

## 2. Comportamento anterior
- Erros HTTP explícitos do backend eram engolidos pelo adapter do Apoema.
- `401`, `403`, `422`, `429` e `5xx` podiam virar fallback/local como se a resposta tivesse sido bem-sucedida.
- O chat podia renderizar mensagem mock ou catálogo local sem avisar que a API tinha retornado erro.

## 3. Comportamento novo
- `401` e `403` agora propagam erro tipado de autenticação/permissão.
- `422`, `429` e `5xx` também propagam erro tipado com mensagem clara.
- Fallback local só acontece quando o backend não responde por falha real de rede.

## 4. Fallback permitido
- Backend offline.
- Falha de rede.
- Falha real de conexão sem resposta HTTP.

## 5. Fallback proibido
- Resposta HTTP explícita `401`.
- Resposta HTTP explícita `403`.
- Resposta HTTP explícita `422`.
- Resposta HTTP explícita `429`.
- Resposta HTTP explícita `5xx`.

## 6. Testes/regressao
- Adicionado teste de contrato estatico em `tests/test_apoema_frontend_error_contract.py`.
- Valida o erro tipado, a separacao entre HTTP e rede e os estados visuais do ChatPage.
- Build do frontend continua parte da validacao obrigatoria.

## 7. Limitacoes
- BUG-003 nao foi corrigido nesta rodada.
- Nao foi adicionado runner frontend novo; a regressao foi coberta por teste estatico no lado Python.
