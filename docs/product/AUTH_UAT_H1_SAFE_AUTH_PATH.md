# AUTH-UAT-H1 — Safe Local UAT Authentication Path

## Status

`AUTH_PATH_DOCUMENTED_SEED_COMMAND`

## Objetivo

Definir um caminho local seguro para autenticação UAT visual sem expor credenciais, sem criar backdoor e sem alterar regra de negócio.

## Caminhos avaliados

- Sessão local já existente.
- Login manual em navegador headed.
- Usuário dev documentado no repositório.
- Comando de seed UAT já documentado.
- Helper/teste existente para sessão segura.

## Caminho seguro recomendado

Usar o fluxo documentado de UAT local existente no repositório:

- `scripts/ops/start-uat.ps1`
- `scripts/ops/prepare-uat-session.ps1`
- `scripts/ops/seed-uat-data.ps1`

Esses scripts exigem variáveis locais definidas pelo operador e não devem imprimir senha, cookie ou token.

## O que não fazer

- Não alterar auth de produção.
- Não criar bypass de login.
- Não hardcodar credencial no código.
- Não commitar storage state, perfil de navegador, cookie ou token.
- Não ler `.env` ou credenciais do ambiente nesta boundary.

## Como autenticar sem expor segredo

1. Definir `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `ADMIN_NAME` somente na sessão local do operador.
2. Executar o script de startup UAT já documentado.
3. Executar o seed UAT já documentado.
4. Abrir o navegador local e usar a sessão autenticada gerada sem exportar storage state.

## Sessão temporária

- Se um perfil temporário for necessário, ele deve ficar fora do repositório e ser descartado ao final da validação.
- Nenhum conteúdo de sessão deve ser impresso.

## Critérios para recheck visual

- `/login` abre normalmente.
- A sessão autenticada local é obtida sem expor segredo.
- `/` e `/assets` abrem autenticados.
- O fluxo de movimentação gera macro e mantém o modal visível para cópia.

## Bloqueios

- Nesta execução, `ADMIN_PASSWORD` local não estava disponível.
- A tentativa de browser com perfil temporário não produziu uma sessão autenticada confiável.

## Próxima ação

Provisionar uma sessão local segura conforme os scripts já documentados e então repetir o recheck visual do `MACRO-H1C`.
