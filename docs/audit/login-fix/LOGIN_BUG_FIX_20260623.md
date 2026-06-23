# Login Bug Fix — 2026-06-23

## 1. Status
GO

## 2. Problema encontrado
O login ficava preso no estado de loading quando o backend nao respondia, e o formulario nao chegava a aparecer de forma confiavel. Isso tambem mascarava erro de backend indisponivel como se fosse apenas espera normal.

## 3. Causa raiz
O `AuthProvider` aguardava a validacao inicial de sessao sem timeout. Quando `/api/v1/auth/refresh` ficava pendurado, `loading` nao era liberado e a tela de login permanecia travada.

## 4. Correção aplicada
- Adicionei timeout/abort no refresh inicial da sessao no `AuthProvider`.
- Adicionei timeout/abort no submit do login.
- Diferenciei mensagens de erro de credencial invalida, backend indisponivel e permissao.
- Mantive o layout visual do login com hero e card, mas agora o formulario aparece mesmo sem backend.

## 5. Comportamento novo
- `/login` carrega e libera o formulario apos a janela de timeout do refresh.
- Submit sem backend nao trava a tela e mostra erro em PT-BR.
- Erros 401/403/422/429/5xx sao apresentados com mensagens especificas.
- Rotas protegidas continuam protegidas pelo `ProtectedRoute` existente.

## 6. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`
- `git diff --check`

## 7. Limitações
- O backend local nao estava disponivel neste runtime, entao o fluxo de login bem-sucedido nao foi validado com credenciais reais.
- A validacao funcional foi confirmada pelo contrato estatico, build do frontend e smoke de carregamento da rota.
- O endpoint local em `127.0.0.1:8080` ficou sem resposta durante a auditoria; a UI de login passou a liberar o formulario e mostrar erro explicito em vez de travar.

## 8. Próximos passos
Executar um smoke autenticado com backend disponivel para confirmar o redirecionamento apos login valido e a persistencia da sessao.
