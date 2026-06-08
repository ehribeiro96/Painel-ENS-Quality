# HermesOps HML Stop Criteria

Durante um futuro smoke test, parar imediatamente se ocorrer:

## Docker/Compose

- Container reiniciando em loop.
- Falha de inicialização de banco.
- Falha de permissão em volume.
- Porta crítica em conflito.
- Uso inesperado de imagem/serviço não aprovado.
- Volume inesperado criado fora do escopo.

## Segurança

- `.env.hml` aparece em `git status` como rastreável.
- Secret aparece em log.
- `COMPOSIO_API_KEY` aparece em output.
- Chamada Composio executada.
- Connected account criada.
- Endpoint externo chamado sem aprovação.

## Aplicação

- Stack trace crítico persistente.
- Serviço principal não inicializa.
- Migração de banco destrutiva aparece sem aprovação.
- Perda de dados ou risco de sobrescrita.

## Ação ao parar

1. Capturar `docker compose ps`.
2. Capturar logs com `--tail=200 --timestamps`.
3. Não executar `down -v`.
4. Usar rollback aprovado.
5. Registrar relatório.
