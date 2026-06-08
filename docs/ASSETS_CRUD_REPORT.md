# Assets CRUD Report

Data: 2026-06-03

## Problema

Ativos tinham backend CRUD e soft delete, mas a tela operacional priorizava consulta/movimentacao e nao oferecia formulario de criar/editar/desativar.

## Causa raiz

- Lacuna de frontend: nao havia formulario cadastral.
- `DELETE /assets/{id}` ja fazia soft delete no backend, preservando historico.
- Criacao manual aceitava payload sem identidade suficiente.

## Solucao aplicada

- Adicionada validacao de schema: ativo manual precisa ter `hostname`, `patrimony` ou `serial`.
- Tela `Ativos` recebeu formulario compacto para:
  - criar ativo;
  - editar dados cadastrais;
  - desativar com confirmacao;
  - preservar a movimentacao como fonte da verdade para troca operacional.
- Acoes por linha agora incluem editar e desativar para perfis autorizados.
- Mensagem de exclusao deixa claro que ha desativacao segura, nao remocao definitiva.

## Testes

- Testes operacionais existentes cobrem create/update/delete soft de ativos.
- Build TypeScript validou os novos formularios.

## Riscos restantes

- O modelo atual de `assets` ainda nao tem `source`, `source_metadata` ou `source_external_key` persistidos como coluna. A chave externa do Lansweeper fica no payload/report de importacao nesta rodada.
- Edicao direta de status/localizacao foi mantida como cadastral, mas a UI orienta usar `Movimentar` para mudancas operacionais.

## Proximos passos

- Avaliar migration conservadora futura para rastreabilidade persistente de origem em `assets`.
