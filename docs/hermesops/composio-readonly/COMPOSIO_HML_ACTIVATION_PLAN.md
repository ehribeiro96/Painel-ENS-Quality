# Plano de ativação HML do Composio

## Estado atual em TEST

1. Plugin visível no CLI, porém em `configured` + `dry-run` + `test`.
2. Credencial armazenada apenas fora do Git em `~/.config/hermesops/secrets/composio.env`.
3. `api.enabled: false` e ações externas bloqueadas por padrão.
4. Write actions e destructive actions continuam bloqueadas.

## Etapas futuras em HML

1. revisar política de segurança e modelo de permissões;
2. confirmar que a chave continua fora do Git;
3. executar apenas o comando local `hermesops composio secret check --dry-run`;
4. obter aprovação explícita antes de qualquer teste com rede;
5. usar futuramente `hermesops composio api health --read-only --confirm-network` para validar a API key sem executar tool externa;
6. autenticar manualmente somente os toolkits aprovados em HML;
7. validar cenários `read-only` e `draft-only`;
8. revisar audit logs sanitizados;
9. só então considerar write actions com aprovação humana adicional.

## Proibições mantidas até HML

- sem autenticação real em TEST;
- sem chamadas externas automáticas;
- sem auto-apply;
- sem ações destrutivas;
- sem promoção para `enabled` nesta fase.
