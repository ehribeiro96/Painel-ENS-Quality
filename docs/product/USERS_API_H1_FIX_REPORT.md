# USERS-API-H1 — Fix Report

## Status

`GO_USERS_API_FIXED`

Audit run: 2026-06-21T15:54:58-03:00.

## Causa raiz

`GET /api/v1/users?page_size=100` podia retornar 500 durante serialização da resposta quando havia usuário local legado com e-mail em domínio especial/reservado, por exemplo `example.test`.

O banco/modelo `User.email` armazena string operacional, mas o DTO de leitura `UserRead` herdava `email: EmailStr` de `UserBase`. `EmailStr` é adequado para entrada (`UserCreate`, `UserUpdate`, login), mas é restritivo demais para serializar dados legados já persistidos. Ao montar `Page[UserRead]`, Pydantic rejeitava o e-mail legado e a rota falhava.

## Correção aplicada

Patch mínimo em `backend/app/domains/users/schemas.py`:

- `UserCreate` e `UserUpdate` continuam validando e-mail com `EmailStr`.
- `UserRead` passa a sobrescrever `email` como `str` com `max_length=254`.
- O contrato JSON continua retornando uma string em `email`.
- Não houve alteração de auth/RBAC, banco, migration, Docker/Compose ou frontend.

## Teste de regressão

Adicionado em `tests/test_operational_contracts.py`:

```text
test_user_read_allows_legacy_reserved_domain_email
```

O teste reproduz a serialização de um usuário legado com domínio reservado e valida que `UserRead.model_validate(...)` não quebra.

## Validações

Reprodução antes do patch:

```text
USERREAD_INVALID_EMAIL_REPRODUCED
ValidationError
value_error
('email',)
```

Teste específico após patch:

```text
PYTHONPATH=backend .venv/bin/python -m unittest tests.test_operational_contracts.OperationalContractsTest.test_user_read_allows_legacy_reserved_domain_email
OK
```

Validação backend completa:

```text
source .venv/bin/activate
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
Ran 152 tests in 0.324s
OK (skipped=8)
```

Probe autenticado redigido:

```text
POST /api/v1/auth/login 200
GET /api/v1/users?page_size=100 200
items_count=5
total=5
page_size=100
```

## O que ficou fora do escopo

- Não alterou Dashboard/H2.
- Não alterou autenticação.
- Não alterou usuário UAT H2.
- Não imprimiu senha, token, cookie ou Authorization header.
- Não alterou migrations.
- Não alterou Docker/Compose.
- Não alterou package files.
- Não alterou frontend.
- Não apagou nem regravou dados locais.

## Riscos restantes

- Dados legados com e-mails não entregáveis continuarão sendo exibidos como strings; isso é intencional para leitura operacional e evita 500.
- Entrada de novos usuários continua protegida por `EmailStr`, então a correção não relaxa criação/edição.

## Próxima boundary

`HISTORY-H1 — improve asset history readability and audit traceability`, se `/assets`/movimentação permanecer funcional após o fix de users.
