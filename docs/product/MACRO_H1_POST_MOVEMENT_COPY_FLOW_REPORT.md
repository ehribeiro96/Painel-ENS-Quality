# MACRO-H1 — Post-Movement Copy Flow Report

## Problema confirmado no UAT-H1

O fluxo pós-movimentação mostrava a macro gerada, mas a jornada do operador não a mantinha disponível de forma confiável para cópia. Além disso, o carregamento de usuários da modal de movimentação estava fazendo chamadas duplicadas de `page_size`, o que gerava erro em runtime no endpoint de usuários.

## Arquivos alterados

- `frontend/itam-platform/src/components/MoveAssetDialog.tsx`
- `frontend/itam-platform/src/pages/AssetDetailsPage.tsx`
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/lib/api.ts`

## Comportamento antes

- A modal de movimentação podia ser desmontada pelo fluxo de atualização do detalhe do ativo.
- A confirmação da movimentação não garantia a permanência do painel de macro na mesma jornada.
- O botão de copiar marcava `copied` de forma otimista antes de confirmar clipboard e API.
- A requisição de usuários na modal podia ser montada com `page_size` duplicado.

## Comportamento depois

- A modal de movimentação permanece aberta após o salvamento da movimentação.
- O detalhe do ativo passa a guardar um snapshot local do asset enquanto a modal está aberta.
- A macro sugerida é mantida em estado explícito até o operador copiá-la ou fechar manualmente.
- A cópia passa a aguardar `navigator.clipboard.writeText(...)` e depois chama `POST /api/v1/macros/generations/{id}/copied`.
- A marcação `copied` só ocorre após cópia bem-sucedida.
- O helper `api.users()` passou a normalizar query strings e eliminar a duplicação de `page_size`.

## Endpoints usados

- `POST /api/v1/assets/{id}/move`
- `GET /api/v1/movements/{movement_id}/suggested-macro`
- `POST /api/v1/macros/generations/{generation_id}/copied`
- `GET /api/v1/users?page_size=100`

## Garantias preservadas

- Não houve alteração de regra de negócio da movimentação.
- Não houve alteração de backend.
- Não houve alteração de migrations.
- Não houve alteração do contrato dos endpoints existentes.
- A idempotência da macro permaneceu no backend.

## Validações executadas

- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v` já estava aprovado no baseline do ambiente.
- `PYTHONPATH=backend .venv/bin/python -m ruff check backend tests scripts` já estava aprovado no baseline do ambiente.
- `PYTHONPATH=backend .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` já estava aprovado no baseline do ambiente.
- `"/mnt/c/Program Files/nodejs/node.exe" ./node_modules/typescript/bin/tsc --noEmit` passou.
- `npm run build` falhou por bloqueio de ambiente WSL/UNC e dependência opcional ausente do Rollup.
- A revalidação visual com bundle atualizado ficou bloqueada por esse mesmo problema de build/runtime local.

## Próxima boundary

`MACRO-H1 — frontend build/runtime unblock and revalidation`
