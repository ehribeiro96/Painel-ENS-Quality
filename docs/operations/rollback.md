# Rollback controlado

Rollback do Painel ENS Quality / Apoema após rollout interrompido. O objetivo é restaurar a aplicação sem destruir ou reinicializar PostgreSQL e Redis.

## Interromper o rollout quando

- o backup não puder ser verificado;
- o precheck ou a migration falhar;
- PostgreSQL ou Redis reiniciar inesperadamente;
- readiness não estabilizar;
- hashes host/container divergirem;
- smoke de autenticação, RBAC, Hermes, auditoria, Macros ou Imports falhar;
- houver suspeita de corrupção ou perda de dados.

## Rollback da aplicação

1. Bloquear novas mudanças e registrar versão, health e containers.
2. Selecionar a tag ou imagem anterior aprovada.
3. Reconstruir/recriar somente o serviço `app`; não executar `down`, não remover volumes e não recriar PostgreSQL ou Redis.
4. Confirmar novamente IDs/`StartedAt` de PostgreSQL e Redis.
5. Executar health, readiness e smoke autenticado da versão restaurada.

## Tratamento da migration 0007

A revisão `0007_macro_movement_unique` adiciona um índice único parcial e possui downgrade. A aplicação anterior deve ser avaliada primeiro com o schema avançado, pois manter a migration evita churn no banco.

Executar downgrade somente se:

- a versão anterior for incompatível com o índice;
- o impacto de remover a proteção de idempotência tiver sido revisado;
- o backup anterior estiver íntegro;
- houver autorização operacional explícita.

Comando documentado, não automático:

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/backend
../.venv/bin/python -m alembic downgrade 0006_ai_chat
```

O downgrade remove o índice; não corrige nem elimina dados. Depois dele, bloquear concorrência de geração de macro até a restauração do candidato ou outra mitigação aprovada.

## Restauração do backup

Restaurar o dump anterior somente em incidente de dados confirmado. Antes da restauração:

- interromper escrita da aplicação;
- preservar o banco afetado para análise;
- validar origem, tamanho e checksum do backup;
- obter autorização explícita;
- usar o runbook operacional do PostgreSQL.

Nunca apagar volume, executar SQL destrutivo ad hoc ou reinicializar Redis/PostgreSQL como atalho.

## Encerramento

O rollback termina apenas com:

- app anterior healthy;
- readiness verde;
- PostgreSQL e Redis preservados;
- smoke autenticado aprovado;
- incidente e decisão sobre a migration registrados.
