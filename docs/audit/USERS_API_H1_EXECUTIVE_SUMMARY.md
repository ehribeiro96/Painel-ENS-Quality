# USERS-API-H1 — Executive Summary

## Status final

```text
GO_USERS_API_FIXED
```

Audit run: 2026-06-21T15:54:58-03:00.

## Decisão

A falha secundária de `GET /api/v1/users?page_size=100` foi corrigida com patch mínimo no DTO de leitura de usuários.

## Causa raiz

`UserRead` herdava `email: EmailStr` de `UserBase`. Esse tipo é correto para entrada de dados, mas na saída quebrava quando registros locais legados tinham e-mail em domínio especial/reservado (`example.test`).

Resultado antes do patch:

```text
UserRead.model_validate(user legado) -> ValidationError em email
/api/v1/users?page_size=100 -> 500 no trace autenticado anterior
```

## Correção

Arquivo alterado:

```text
backend/app/domains/users/schemas.py
```

Mudança:

```text
UserRead.email: str = Field(max_length=254)
```

Preservado:

```text
UserCreate.email: EmailStr
UserUpdate.email: EmailStr | None
```

## Evidência de validação

Teste de regressão:

```text
PYTHONPATH=backend .venv/bin/python -m unittest tests.test_operational_contracts.OperationalContractsTest.test_user_read_allows_legacy_reserved_domain_email
OK
```

Suite backend:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
Ran 152 tests
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

## Segurança e escopo

- Nenhuma credencial foi impressa.
- Nenhum token/cookie/storage state foi salvo ou commitado.
- Nenhuma migration foi criada.
- Nenhum dado local foi apagado ou alterado.
- Docker/Compose não foi alterado.
- Frontend e fix H2 não foram reabertos.

## Próxima boundary recomendada

```text
HISTORY-H1 — improve asset history readability and audit traceability
```
