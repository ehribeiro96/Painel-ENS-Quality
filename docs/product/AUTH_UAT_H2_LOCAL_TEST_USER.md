# AUTH-UAT-H2 — Local UAT Test User

## Status

`GO_AUTH_USER_CREATED`

Audit run: 2026-06-20T20:21:48-03:00.

## Caminho avaliado

Classificação da FASE 2: `UAT_USER_PATH_APP_SERVICE_SCRIPT_TEMP`.

Caminhos avaliados:

- `scripts/ops/seed-uat-data.ps1`: existe, mas depende de `ADMIN_EMAIL` e `ADMIN_PASSWORD` locais do operador; não foi usado porque esta boundary não podia imprimir, inferir ou ler credencial admin.
- API `/api/v1/users`: existe, mas exige sessão ADMIN/TECHNICIAN; não havia sessão autenticada inicial.
- Helpers de teste: existem para regressão operacional, mas dependem de `ADMIN_PASSWORD` no ambiente e não criam uma sessão UAT independente.
- Script temporário usando serviços/modelos existentes: viável sem alterar código funcional e sem imprimir segredo.

## Caminho usado

Foi usado script temporário fora do repositório:

```text
/tmp/auth_uat_h2_provision_user.py
```

O script:

- carregou configuração pelo mecanismo existente do app;
- usou `AsyncSessionLocal` existente;
- registrou modelos via `app.core.database.base`;
- usou `UserCreate` e `UserService.create()` existentes;
- usou o hash de senha existente indiretamente via service;
- criou usuário sintético local com `source='auth_uat_h2'`;
- não alterou código, schema, migration, Docker, frontend ou backend source;
- não imprimiu senha, hash, cookie, token, Authorization header ou DB URL.

## Usuário sintético

Usuário criado para UAT local:

```text
auth.uat.h2.1781997487@ens.edu.br
```

Função local usada:

```text
ADMIN
```

Justificativa da role: a própria bateria autenticada precisava acessar `/`, `/assets`, `/audit-logs`, `/macros` e `/ai-chat`; `ADMIN` cobre as rotas protegidas sem criar múltiplos usuários.

Não registrar senha.

Resultado de provisionamento:

```text
UAT_USER_ACTION=created
UAT_PASSWORD_PRINTED=NO
UAT_PASSWORD_HASH_PRINTED=NO
DB_URL_PRINTED=NO
```

## Onde a credencial local ficou

Arquivo local temporário:

```text
/tmp/painel_auth_uat_h2_credentials.txt
```

Permissão configurada:

```text
0600
```

Não registrar conteúdo.

O arquivo contém somente credencial sintética local e deve permanecer fora do repositório.

## Como usar com segurança

1. Usar somente no runtime local do Painel.
2. Ler a credencial apenas dentro de script temporário local ou digitar manualmente no navegador headed.
3. Nunca imprimir senha.
4. Nunca imprimir access token, refresh cookie, Authorization header ou storage state.
5. Nunca copiar o arquivo para o repositório.
6. Nunca commitar perfil de navegador autenticado.
7. Se usar Playwright, manter perfis e traces em `/tmp` e revisar risco antes de preservar artefatos.

## Como limpar depois

Opção conservadora recomendada após concluir boundaries autenticadas:

1. Remover o arquivo local de credencial:

```bash
rm -f /tmp/painel_auth_uat_h2_credentials.txt
```

2. Opcionalmente, desativar/remover o usuário sintético local por script temporário ou API existente, em boundary própria de limpeza, sem resetar banco e sem apagar dados reais.

Não executar limpeza destrutiva ampla nesta boundary.

## O que não foi alterado

- Não alterou autenticação de produção.
- Não criou backdoor.
- Não criou endpoint novo.
- Não alterou backend source.
- Não alterou frontend source.
- Não alterou migrations.
- Não alterou Docker/Compose.
- Não alterou `package.json` ou `package-lock.json`.
- Não alterou `.env` ou `.env.*`.
- Não leu `.env` diretamente.
- Não imprimiu senha, cookie, token, Authorization header ou storage state.
- Não commitou credencial, screenshot, trace, storage state ou perfil de navegador.
- Não resetou banco.

## Bloqueios

Nenhum bloqueio para criar usuário sintético local. O caminho seguro foi validado com login HTTP e trace browser autenticado.
