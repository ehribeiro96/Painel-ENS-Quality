# Next Boundary Decision

Boundary atual concluída: `USERS-API-H1 — fix local users serialization failure`.

## Estado consolidado

- `FRONTEND-AUTH-FREEZE-H2`: `GO_FREEZE_FIXED`; commit `0e70dd1 fix(frontend): handle dashboard status response shape`.
- `USERS-API-H1`: `GO_USERS_API_FIXED`; `/api/v1/users?page_size=100` retorna 200 após corrigir serialização de e-mail legado em `UserRead`.

## Decisão objetiva

O achado secundário de `/api/v1/users` foi corrigido sem reabrir H2 e sem alterar autenticação, Docker/Compose, migrations, package files ou dados locais.

Causa raiz corrigida:

```text
UserRead herdava email: EmailStr de UserBase. Registros locais legados com domínio especial/reservado, como example.test, falhavam durante serialização de resposta e causavam 500 em GET /api/v1/users?page_size=100.
```

Correção aplicada:

```text
UserRead.email agora é string de saída com max_length=254.
UserCreate/UserUpdate continuam usando EmailStr para entrada.
```

Evidência resumida:

```text
POST /api/v1/auth/login 200
GET /api/v1/users?page_size=100 200
python -m unittest discover -s tests -> OK (skipped=8)
```

## Próxima boundary recomendada

1. `HISTORY-H1 — improve asset history readability and audit traceability`
   - Condição: freeze autenticado e `/api/v1/users` resolvidos.
   - Objetivo: retomar melhoria de histórico/rastreabilidade de ativos.
   - Escopo sugerido: leitura conservadora do histórico atual, UX/API somente se necessário, sem alterar movimentação append-only sem teste específico.

## Boundaries seguintes condicionais

2. `DASHBOARD-CONTRACT-H1 — align dashboard API/frontend typing`
   - Condição: se for decidido padronizar contrato em vez de manter compatibilidade defensiva no frontend.
   - Objetivo: alinhar `frontend/itam-platform/src/lib/api.ts`, tipos compartilhados e documentação do contrato dashboard.

## O que não fazer agora

- Não reabrir `FRONTEND-AUTH-FREEZE-H2`.
- Não alterar o usuário UAT H2.
- Não imprimir credenciais, tokens, cookies ou storage state.
- Não apagar dados locais nem resetar banco.
- Não alterar `.env`, `.env.*`, Docker/Compose, migrations, package files, assets, CI ou IA/Ollama.
- Não misturar melhorias de histórico com mudanças de auth ou serialização de usuários.

## Decisão final

Próxima boundary recomendada: `HISTORY-H1 — improve asset history readability and audit traceability`.
