# Composio API Health Check Plan

## Objetivo
Adicionar e documentar o comando seguro:

```bash
hermesops composio api health --read-only --confirm-network
```

## Regras
- Exige `--read-only`.
- Exige `--confirm-network`.
- Sem essas flags, o comando aborta.
- A chave fica somente em `~/.config/hermesops/secrets/composio.env`.
- A chave nunca é impressa, copiada, enviada ao renderer ou gravada em relatório.
- O comando faz apenas leitura em `GET /api/v3.1/tools`.
- Nenhuma tool de execução é chamada.
- Nenhuma conta conectada é criada.
- Nenhuma ação externa é executada.

## Comportamento em dry-run

```bash
hermesops composio api health --read-only --confirm-network --dry-run
```

- Mostra o plano.
- Não faz rede.
- Não carrega a chave para execução real.
- Registra apenas o resumo planejado.

## Saída esperada em execução real

```text
Composio API Health Check
Modo: read-only
Rede: confirmada explicitamente
Endpoint: GET /api/v3.1/tools
Chave: presente / ocultada
HTTP: 200
Tools retornadas: <n>
Ações externas executadas: 0
Contas conectadas criadas: 0
Status: OK
```

## Falhas esperadas

```text
Status: FALHA
HTTP: <code ou unavailable>
Erro: <mensagem sanitizada>
Chave: ocultada
```

## Registro sanitizado
- timestamp
- endpoint
- HTTP status
- tools retornadas
- erro sanitizado
- ações externas executadas: 0
- contas conectadas criadas: 0

## Observação
O host base do Composio fica configurável por `COMPOSIO_API_BASE_URL`, com fallback local em `https://connect.composio.dev`.
