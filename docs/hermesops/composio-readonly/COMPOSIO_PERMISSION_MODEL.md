# Modelo de permissões do Composio

## Classificações

- `read_only`
- `draft_only`
- `write_requires_approval`
- `destructive_blocked`
- `external_publish_blocked`
- `admin_blocked`

## Regras centrais

- Leitura antes de escrita.
- Aprovação humana para qualquer ação de escrita futura.
- Bloqueio permanente de ações destrutivas nesta fase.
- `external_actions_default: blocked` mesmo com credencial presente.
- `configured` não equivale a `enabled`.

## Regras de credencial

- A `COMPOSIO_API_KEY` fica fora do Git em `~/.config/hermesops/secrets/composio.env`.
- O valor nunca deve aparecer em terminal, logs, relatórios ou memória.
- O comando de verificação local apenas confirma presença/ausência e permissões.
- Permissão recomendada para o arquivo: `600`.

## Consequências operacionais

- TEST: apenas inspeção local, dry-run e documentação.
- HML: somente após aprovação explícita e com testes `read-only` / `draft-only`.
- PROD: fora de escopo.
