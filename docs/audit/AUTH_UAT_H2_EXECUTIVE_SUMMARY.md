# AUTH-UAT-H2 — Executive Summary

## Status

`GO_AUTH_TRACE_REPRODUCED_FREEZE`

## Resultado executivo

A boundary criou um caminho seguro de autenticação local UAT, validou login autenticado e reproduziu o travamento pós-login com evidência redigida.

Usuário sintético local criado:

```text
auth.uat.h2.1781997487@ens.edu.br
```

Senha impressa: não.

Token/cookie/Authorization/storage state impressos: não.

## Caminho de auth encontrado

`UAT_USER_PATH_APP_SERVICE_SCRIPT_TEMP`.

Foi usado script temporário em `/tmp`, com serviços/modelos existentes do app, sem alterar código, migrations, Docker, frontend, backend source, package files ou `.env`.

## Login autenticado

Funcionou.

Validação HTTP:

```text
LOGIN_STATUS=200
ACCESS_TOKEN_PRESENT=true
ACCESS_TOKEN_PRINTED=NO
COOKIE_PRINTED=NO
```

## Trace autenticado

Coletado por script temporário local:

```text
/tmp/frontend_auth_freeze_authenticated_probe.cjs
/tmp/frontend_auth_freeze_authenticated_probe_result.json
```

Nenhum desses arquivos foi colocado no repositório.

## Freeze reproduzido

Sim.

Classificação:

```text
FREEZE_RENDER_EXCEPTION
```

A rota `/` após login ficou sem shell/sidebar/header e gerou page error fatal:

```text
TypeError: Cannot read properties of undefined (reading 'replaceAll')
```

## Causa raiz provável

Contrato incompatível entre dashboard backend e frontend:

- Backend `DashboardService.group_by("status")` retorna itens como `{ name, value }`.
- Frontend `DashboardPage.tsx` espera `{ status, count }` em `/dashboard/assets-by-status`.
- O frontend acessa `item.status`; como o valor é `undefined`, `formatStatus(item.status)` chama `replaceAll` em `undefined`.
- Isso derruba o render do dashboard logo após login.

## Achado secundário

Ao testar `/assets`, a rota renderizou shell, mas `GET /api/v1/users?page_size=100` retornou 500.

Causa provável secundária:

- Existe usuário local prévio com e-mail em domínio reservado `example.test`.
- `UserRead` usa `EmailStr`, que rejeita esse domínio durante serialização.
- Isso quebra `/api/v1/users`, afetando seleção de usuários em movimentação.

## Próxima boundary recomendada

`FRONTEND-AUTH-FREEZE-H2 — fix authenticated freeze root cause`.

Objetivo:

1. Corrigir mismatch de contrato do dashboard com patch mínimo.
2. Revalidar `/` autenticado sem exceção fatal.
3. Registrar `/api/v1/users` como correção secundária ou boundary separada, sem apagar dados reais.

## Segurança

- Nenhuma senha foi impressa.
- Nenhum token foi impresso.
- Nenhum cookie foi impresso.
- Nenhum Authorization header foi impresso.
- Nenhum storage state foi salvo/commitado.
- Nenhum arquivo de credencial foi commitado.
- Nenhum código funcional foi alterado.
