# Plano de Backup Lógico Futuro - HermesOps HML

## Status

Plano documental. Nenhum backup lógico foi executado nesta fase.

## PostgreSQL

Estratégia recomendada:

1. Criar diretório seguro fora do Git.
2. Executar `pg_dump` dentro do container atual.
3. Salvar dump em arquivo `.dump` ou `.sql` fora do Git.
4. Gerar SHA256.
5. Validar restore em daemon alvo antes de cutover.

Comando futuro, NÃO EXECUTAR NESTA FASE:

```bash
docker compose -f docker-compose.hml.yml --env-file .env.hml exec -T postgres \
  sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > /caminho/seguro/hermesops_hml_postgres.dump
```

## Qdrant

Estratégia recomendada:

1. Verificar collections.
2. Se houver collections, usar mecanismo oficial de snapshot/export compatível.
3. Salvar snapshots fora do Git.
4. Gerar SHA256.
5. Validar import no daemon alvo.

Comando futuro genérico, validar antes de usar:

```bash
curl -fsS http://127.0.0.1:7333/collections
```

## Redis

Decisão necessária:

- Se Redis for cache: não migrar dados, apenas recriar.
- Se Redis armazenar estado de fila/sessão relevante: usar RDB/AOF conforme política.

## Proibido

- Copiar volume bruto entre Docker Desktop e Docker Engine nativo sem validação.
- Versionar dumps.
- Versionar snapshots.
- Imprimir secrets.
