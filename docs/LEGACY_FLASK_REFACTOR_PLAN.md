# Legacy Flask Refactor Plan

## Objetivo

Preservar o comportamento atual de `/assinaturas/` e `/admin/`, reduzindo risco
gradualmente sem reescrever o legado em uma unica etapa.

## Escopo futuro

- Separar configuracao sensivel em modulo dedicado.
- Separar auth/session/CSRF.
- Separar renderer de assinatura.
- Separar templates/static e validacoes de assets.
- Isolar SMTP.
- Isolar Microsoft Graph/OAuth.
- Isolar banco SQLite `data/ens.db`.
- Criar smoke tests especificos para `/assinaturas/` e `/admin/`.

## Correcoes ja aplicadas

- Removidos defaults sensiveis de senha admin, secret key e SMTP.
- Produção falha se variaveis obrigatorias do legado estiverem ausentes.
- SMTP com `ENS_SMTP_MODE=ON` exige usuario e senha via ambiente.

## Fora de escopo nesta rodada

- Reescrever Flask.
- Migrar SQLite legado.
- Alterar templates de assinatura.
- Integrar Microsoft Graph.
- Remover `/assinaturas/` ou `/admin/`.
