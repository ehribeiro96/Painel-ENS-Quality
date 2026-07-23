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
2. Em uma única sessão Bash, selecionar a tag e o image ID anteriores aprovados, validar a proveniência e vincular exatamente essa imagem à referência que o Compose recriará:

   ```bash
   set -euo pipefail
   : "${TARGET_TAG:?TARGET_TAG is required}"
   : "${ROLLBACK_IMAGE_ID:?ROLLBACK_IMAGE_ID is required from the approved inventory}"
   TARGET_COMMIT="$(TARGET_TAG="${TARGET_TAG}" ./scripts/resolve_release_tag.sh)"
   test -n "${TARGET_COMMIT}"
   export APP_AUTO_MIGRATE=false
   export OCI_REVISION="${TARGET_COMMIT}"
   export OCI_VERSION="${TARGET_TAG}"
   export OCI_SOURCE="https://github.com/ehribeiro96/Painel-ENS-Quality"
   IMAGE_REF="$(docker compose config --format json | python3 -c \
     'import json, sys; print(json.load(sys.stdin)["services"]["app"]["image"])')"
   test -n "${IMAGE_REF}"
   export APP_IMAGE="${IMAGE_REF}"
   IMAGE_ID="$(docker image inspect "${ROLLBACK_IMAGE_ID}" --format '{{.Id}}')"
   test -n "${IMAGE_ID}"
   python3 scripts/assert_oci_labels.py \
     "${IMAGE_ID}" "${TARGET_COMMIT}" "${TARGET_TAG}" "${OCI_SOURCE}"
   docker image tag "${IMAGE_ID}" "${IMAGE_REF}"
   test "$(docker image inspect "${IMAGE_REF}" --format '{{.Id}}')" = "${IMAGE_ID}"
   docker compose up -d --no-build --no-deps --force-recreate app
   CONTAINER_ID="$(docker compose ps -q app)"
   test -n "${CONTAINER_ID}"
   test "$(docker inspect "${CONTAINER_ID}" --format '{{.Image}}')" = "${IMAGE_ID}"
   ```

   O rollback não reconstrói tags históricas com ferramentas potencialmente ausentes naquela versão. Se a imagem aprovada não existir, não tiver labels certificadas ou divergir da tag, interromper e escalar; não fazer rebuild improvisado.
3. Não executar `down`, não remover volumes e não recriar PostgreSQL ou Redis.
4. Confirmar novamente IDs/`StartedAt` de PostgreSQL e Redis.
5. Executar health, readiness e smoke autenticado da versão restaurada.

## Tratamento da migration 0007

A revisão `0007_macro_movement_unique` adiciona um índice único parcial e possui downgrade. A aplicação anterior deve ser avaliada primeiro com o schema avançado, pois manter a migration evita churn no banco.

Antes do upgrade, executar `docs/operations/sql/precheck-0007-macro-movement-unique.sql`. Qualquer linha retornada interrompe o rollout como `STOP_DATA_CONFLICT`; o script é somente leitura e não autoriza correção ou deduplicação automática.

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
- identidade OCI da imagem restaurada correspondente à release aprovada;
- incidente e decisão sobre a migration registrados.
