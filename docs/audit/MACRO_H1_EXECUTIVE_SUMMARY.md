# MACRO-H1 — Executive Summary

## Status

`PARTIAL_RUNTIME_BLOCKED`

## Resumo

O ajuste do fluxo pós-movimentação foi aplicado no frontend para manter a macro visível e tornar a cópia menos frágil. A correção também removeu a duplicação de `page_size` no cliente de usuários.

## O que foi alterado

- `MoveAssetDialog` agora mantém estado explícito para movimentação, macro e cópia.
- `AssetDetailsPage` usa snapshot local do asset enquanto a modal está aberta.
- `api.users()` passou a normalizar query string e evitar `page_size` duplicado.
- `AssetsPage` e `AssetDetailsPage` passaram a chamar `api.users(..., "?page_size=100")`.

## O que foi preservado

- Backend idempotente de macro.
- Endpoints existentes.
- Regras de negócio da movimentação.
- Migrations.
- Docker/Compose.
- ImportService.

## Limitação encontrada

O frontend não pôde ser revalidado em bundle atualizado porque o ambiente WSL/UNC não conseguiu executar a build do Vite sem o binário opcional do Rollup nativo.

## Próxima boundary recomendada

`MACRO-H1 — frontend build/runtime unblock and revalidation`
