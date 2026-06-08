# AGENTS.md - Padrões do Painel ENS-Quality

## Backend

- Manter arquitetura modular existente.
- Routes ficam em backend/app/api/v1/routes.
- Domínios ficam em backend/app/domains.
- Regras de negócio ficam nos services.
- Models SQLAlchemy não devem ser retornados diretamente se houver DTO específico melhor.
- Usar Pydantic para request/response.
- Registrar auditoria em alterações persistentes.
- Não duplicar regra de negócio no frontend.

## Frontend

- Usar React/Vite existente.
- Manter API central em frontend/itam-platform/src/lib/api.ts.
- Tipos em frontend/itam-platform/src/lib/types.ts.
- Componentes pequenos.
- Loading, erro e sucesso explícitos.
- Macro gerada após movimentação deve continuar visível.
- Não fechar modal automaticamente se o técnico ainda precisa copiar macro.

## Macros

- Placeholder padrão: {Campo}.
- Não usar eval, exec ou template engine executável.
- Campo ausente deve permanecer como placeholder quando permitido.
- Campos obrigatórios devem ser validados.
- Macro gerada deve ser persistida em macro_generations.
- Macro copiada deve marcar copied=true e copied_at.

## Movimentações

- AssetMovement é append-only.
- Não permitir update/delete de movimentação.
- Correções devem ser novos eventos compensatórios.
- Movimentação deve capturar estado anterior e novo estado.
- Futuro: adicionar movement_type, ticket_number e kcs_code.

## Segurança

- Não abrir, imprimir ou copiar valores de .env/secrets.
- Não versionar .env, secrets, bancos locais, backups, .venv, node_modules ou evidências.
- Não colocar chave OpenAI no frontend.
