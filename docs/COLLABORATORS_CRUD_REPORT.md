# Collaborators CRUD Report

Data: 2026-06-03

## Problema

A tela `Colaboradores` listava registros, mas o botao `+ Novo` nao executava criacao/edicao/desativacao. No backend havia create/update/list/get, mas faltava endpoint de delete seguro.

## Causa raiz

- Lacuna de integracao frontend para formulario operacional.
- `UserService.soft_delete` ja existia, mas nao estava exposto por rota.
- `UserUpdate` permitia `role`, criando risco de edicao administrativa fora de fluxo explicito.

## Solucao aplicada

- Criada rota `DELETE /api/v1/users/{id}` com soft delete e auditoria.
- Bloqueada autoexclusao do usuario logado.
- Removida edicao de `role` do schema `UserUpdate`.
- `UserCreate` continua permitindo role apenas com protecao: tecnico nao pode criar role acima de viewer.
- Criacao manual passa a preencher `source=manual`.
- Atualizacao nao troca `source` legado para manual por acidente e nao sobrescreve campos com string vazia.
- Tela `Colaboradores` agora permite:
  - criar colaborador;
  - editar dados cadastrais;
  - desativar com confirmacao;
  - visualizar fonte e status;
  - exibir erros de validacao.

## Testes

- Adicionado teste de contrato para garantir que `UserUpdate` nao expoe `role`.
- Adicionado teste operacional para soft delete de colaborador.

## Riscos restantes

- O formulario nao edita senha, role ou flags administrativas; isso deve continuar em fluxo administrativo separado.
- `source_metadata` aparece como campo interno de backend e nao foi exposto integralmente na UI.

## Proximos passos

- Validar criacao/edicao/desativacao com perfil ADMIN em UAT.
