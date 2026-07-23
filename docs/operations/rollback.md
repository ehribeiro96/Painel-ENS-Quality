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
2. Em uma única sessão Bash, selecionar a tag e o image ID anteriores aprovados, derivar a fonte histórica da revisão OCI e vincular exatamente essa imagem ao Compose da mesma revisão:

   ```bash
   set -euo pipefail
   : "${TARGET_TAG:?TARGET_TAG is required}"
   : "${ROLLBACK_IMAGE_ID:?ROLLBACK_IMAGE_ID is required from the approved inventory}"
   : "${EVIDENCE_ROOT:?EVIDENCE_ROOT is required outside the repository}"
   : "${CHANGE_ID:?CHANGE_ID is required}"
   RELEASE_SOURCE="$(git rev-parse --show-toplevel)"
   EVIDENCE_ROOT="$(realpath -m "${EVIDENCE_ROOT}")"
   case "${EVIDENCE_ROOT}/" in "${RELEASE_SOURCE}/"*) echo "EVIDENCE_ROOT must be outside the repository" >&2; exit 1;; esac
   mkdir -p "${EVIDENCE_ROOT}"

   ROLLBACK_REVISION="$(
     docker image inspect \
       --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' \
       "${ROLLBACK_IMAGE_ID}"
   )"
   "${RELEASE_SOURCE}/scripts/release_integrity.sh" \
     validate-revision "${RELEASE_SOURCE}" "${ROLLBACK_REVISION}" >/dev/null

   TARGET_COMMIT="$(TARGET_TAG="${TARGET_TAG}" ./scripts/resolve_release_tag.sh)"
   test -n "${TARGET_COMMIT}"
   test "${TARGET_COMMIT}" = "${ROLLBACK_REVISION}"

   ROLLBACK_SOURCE="$(
     mktemp -d "${EVIDENCE_ROOT}/rollback-source.XXXXXX"
   )"
   git worktree add \
     --detach \
     "${ROLLBACK_SOURCE}" \
     "${ROLLBACK_REVISION}"
   test "$(
     git -C "${ROLLBACK_SOURCE}" rev-parse HEAD
   )" = "${ROLLBACK_REVISION}"
   "${RELEASE_SOURCE}/scripts/release_integrity.sh" \
     validate-rollback-source \
     "${ROLLBACK_SOURCE}" \
     "${EVIDENCE_ROOT}" \
     "${ROLLBACK_REVISION}" >/dev/null

   ROLLBACK_OVERRIDE="$(
     mktemp "${EVIDENCE_ROOT}/rollback-override.XXXXXX.yml"
   )"
   chmod 600 "${ROLLBACK_OVERRIDE}"
   cat >"${ROLLBACK_OVERRIDE}" <<'YAML'
   services:
     app:
       image: ${APP_IMAGE:?APP_IMAGE is required}
       environment:
         APP_AUTO_MIGRATE: "false"
   YAML
   "${RELEASE_SOURCE}/scripts/release_integrity.sh" \
     validate-rollback-override "${ROLLBACK_OVERRIDE}"

   export APP_AUTO_MIGRATE=false
   export OCI_REVISION="${ROLLBACK_REVISION}"
   export OCI_VERSION="${TARGET_TAG}"
   export OCI_SOURCE="https://github.com/ehribeiro96/Painel-ENS-Quality"
   [[ "${CHANGE_ID}" =~ ^[A-Za-z0-9_.-]+$ ]]
   ROLLBACK_IMAGE_REF="painel-ens-quality-app:rollback-${CHANGE_ID}"
   IMAGE_ID="$(docker image inspect "${ROLLBACK_IMAGE_ID}" --format '{{.Id}}')"
   test -n "${IMAGE_ID}"
   python3 scripts/assert_oci_labels.py \
     "${IMAGE_ID}" "${ROLLBACK_REVISION}" "${TARGET_TAG}" "${OCI_SOURCE}"
   docker image tag "${ROLLBACK_IMAGE_ID}" "${ROLLBACK_IMAGE_REF}"
   "${RELEASE_SOURCE}/scripts/release_integrity.sh" \
     assert-image-reference "${ROLLBACK_IMAGE_REF}" "${ROLLBACK_IMAGE_ID}"

   APP_IMAGE="${ROLLBACK_IMAGE_REF}" \
   APP_AUTO_MIGRATE=false \
   docker compose \
     --project-directory "${ROLLBACK_SOURCE}" \
     -f "${ROLLBACK_SOURCE}/docker-compose.yml" \
     -f "${ROLLBACK_OVERRIDE}" \
     up \
     -d \
     --no-deps \
     --no-build \
     --force-recreate \
     app

   ROLLED_BACK_CONTAINER_ID="$(
     APP_IMAGE="${ROLLBACK_IMAGE_REF}" \
     APP_AUTO_MIGRATE=false \
     docker compose \
       --project-directory "${ROLLBACK_SOURCE}" \
       -f "${ROLLBACK_SOURCE}/docker-compose.yml" \
       -f "${ROLLBACK_OVERRIDE}" \
       ps -q app
   )"
   test -n "${ROLLED_BACK_CONTAINER_ID}"
   "${RELEASE_SOURCE}/scripts/release_integrity.sh" \
     assert-container-image \
     "${ROLLED_BACK_CONTAINER_ID}" \
     "${ROLLBACK_IMAGE_ID}"
   ```

   O rollback usa obrigatoriamente `docker-compose.yml` do worktree detached em `ROLLBACK_REVISION`; o checkout atual nunca fornece a configuração histórica. O override externo é mínimo, afeta somente `app`, não contém `build`, volumes, PostgreSQL, Redis ou secrets e força `APP_AUTO_MIGRATE=false`. Se a imagem aprovada não existir, não tiver revision OCI certificada, divergir da tag, não possuir commit/Compose histórico ou produzir container com outro image ID, interromper e escalar; não fazer rebuild improvisado.
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
