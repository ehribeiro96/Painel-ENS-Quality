# MACRO-H1 — UAT Fix Validation

## Escopo validado

Correção pequena e conservadora no fluxo pós-movimentação.

## Resultados esperados

- A modal não deve fechar automaticamente após salvar a movimentação.
- A macro sugerida deve permanecer visível para cópia.
- `generation_id` deve ser preservado.
- `copied` deve ser marcado apenas após cópia bem-sucedida.

## Resultado da implementação

- O detalhe do ativo passou a segurar um snapshot local do asset enquanto a modal está aberta.
- A modal de movimentação passou a manter o estado de sucesso e da macro gerada.
- O endpoint de cópia é chamado apenas depois da escrita no clipboard.
- O helper de usuários foi corrigido para não duplicar `page_size`.

## Validação de runtime

O runtime visual atualizado não pôde ser reexecutado no bundle servido localmente porque:

- o build do frontend falhou no ambiente WSL/UNC;
- o Rollup nativo opcional `@rollup/rollup-win32-x64-msvc` não está presente;
- o bundle servido localmente ainda é o anterior à mudança.

## Validação estática

- `tsc --noEmit` passou com o código alterado.
- O diff ficou restrito ao frontend e não tocou em backend, migrations ou package-lock.

## Status

`PARTIAL_RUNTIME_BLOCKED`
