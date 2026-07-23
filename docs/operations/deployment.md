# Deployment controlado

Procedimento para promover uma versão aprovada do Painel ENS Quality / Apoema sem recriar PostgreSQL ou Redis.

## Pré-condições

- Pull Request aprovada e checks verdes.
- Tag anotada existente no GitHub.
- Janela de mudança e responsável por rollback definidos.
- Backup do PostgreSQL concluído, íntegro e armazenado fora do repositório.
- Precheck da migration sem duplicidades incompatíveis.
- Variáveis obrigatórias definidas no ambiente, sem registrar valores: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `ADMIN_PASSWORD`, `ENVIRONMENT`, `ENABLE_AI_CHAT`, `AI_CHAT_DEFAULT_PROVIDER` e configuração do provider escolhido.
- `APP_AUTO_MIGRATE=false` definido no deployment controlado. O default seguro também é `false` em local, staging e production; habilitar auto-migration exige decisão explícita e não é o fluxo recomendado.

## Procedimento

1. Em uma única sessão Bash, habilitar parada imediata e validar a tag anotada aprovada no `origin` antes de checkout, build, migration ou qualquer outra ação mutante. O helper rejeita tag ausente, local-only, divergente, inexistente ou não anotada e devolve o commit completo peeled:

   ```bash
   set -euo pipefail
   : "${TARGET_TAG:?TARGET_TAG is required}"
   : "${EVIDENCE_ROOT:?EVIDENCE_ROOT is required outside the repository}"
   RELEASE_SOURCE="$(git rev-parse --show-toplevel)"
   REPO_ROOT="${RELEASE_SOURCE}"
   EVIDENCE_ROOT="$(realpath -m "${EVIDENCE_ROOT}")"
   case "${EVIDENCE_ROOT}/" in "${REPO_ROOT}/"*) echo "EVIDENCE_ROOT must be outside the repository" >&2; exit 1;; esac
   ./scripts/release_integrity.sh \
     assert-clean "${RELEASE_SOURCE}" "${EVIDENCE_ROOT}" >/dev/null
   TARGET_COMMIT="$(TARGET_TAG="${TARGET_TAG}" ./scripts/resolve_release_tag.sh)"
   test -n "${TARGET_COMMIT}"
   printf 'TARGET_TAG=%s\nTARGET_COMMIT=%s\n' "${TARGET_TAG}" "${TARGET_COMMIT}"
   git switch --detach "${TARGET_COMMIT}"
   test "$(git rev-parse HEAD)" = "${TARGET_COMMIT}"
   ./scripts/release_integrity.sh \
     assert-clean "${RELEASE_SOURCE}" "${EVIDENCE_ROOT}" >/dev/null
   ```

   O helper valida `EVIDENCE_ROOT` antes de criar qualquer artefato, grava a saída de `git status` em arquivo externo com modo `0600` e testa separadamente o exit code e o tamanho do arquivo. Falha do Git nunca é convertida em worktree limpa. O gate anterior ao `git switch` evita mudar o estado do operador quando já existe drift; a repetição posterior é defesa adicional.

2. Registrar versão atual, containers e health.
3. Criar e verificar o backup do PostgreSQL pelo procedimento operacional aprovado. Não imprimir conexão, credenciais nem conteúdo do dump.
4. Criar o diretório externo já validado e executar o precheck somente leitura da migration 0007 com usuário PostgreSQL read-only:

   ```bash
   mkdir -p "${EVIDENCE_ROOT}"
   psql "$DATABASE_URL_READ_ONLY" --set ON_ERROR_STOP=1 \
     --file docs/operations/sql/precheck-0007-macro-movement-unique.sql \
     > "${EVIDENCE_ROOT}/precheck-0007-macro-movement-unique.txt"
   ```

   Zero linhas significa `READY_TO_MIGRATE`. Uma ou mais linhas significa `STOP_DATA_CONFLICT`: não aplicar a migration, não deduplicar automaticamente e encaminhar decisão manual auditada. A migration só pode seguir após precheck vazio e backup verificado. O arquivo de evidência fica fora do repositório e não invalida o gate de worktree limpa.

5. Validar o grafo Alembic e aplicar a migration como etapa operacional explícita, com o ambiente virtual do projeto:

   ```bash
   cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
   ./.venv/bin/alembic heads
   cd backend
   ../.venv/bin/python -m alembic upgrade head
   cd ..
   ```

6. Criar um contexto imutável diretamente do commit certificado, construir a imagem desse tar via stdin e conferir as labels, de forma fail-closed, antes de recriar somente a aplicação:

   ```bash
   export APP_AUTO_MIGRATE=false
   export OCI_REVISION="${TARGET_COMMIT}"
   export OCI_VERSION="${TARGET_TAG}"
   export OCI_SOURCE="https://github.com/ehribeiro96/Painel-ENS-Quality"
   BUILD_CONTEXT_TAR="$(
     ./scripts/release_integrity.sh \
       create-build-context \
       "${RELEASE_SOURCE}" \
       "${EVIDENCE_ROOT}" \
       "${TARGET_COMMIT}"
   )"
   ARCHIVED_COMMIT="$(
     git -C "${RELEASE_SOURCE}" \
       get-tar-commit-id <"${BUILD_CONTEXT_TAR}"
   )"
   test "${ARCHIVED_COMMIT}" = "${TARGET_COMMIT}"
   sha256sum "${BUILD_CONTEXT_TAR}" | tee "${BUILD_CONTEXT_TAR}.sha256"
   IMAGE_REF="$(docker compose config --format json | python3 -c \
     'import json, sys; print(json.load(sys.stdin)["services"]["app"]["image"])')"
   test -n "${IMAGE_REF}"
   export APP_IMAGE="${IMAGE_REF}"
   IID_FILE="$(mktemp "${EVIDENCE_ROOT}/image-id.XXXXXX")"
   docker build --iidfile "${IID_FILE}" --tag "${IMAGE_REF}" \
     --file backend/Dockerfile \
     --build-arg "OCI_REVISION=${TARGET_COMMIT}" \
     --build-arg "OCI_VERSION=${TARGET_TAG}" \
     --build-arg "OCI_SOURCE=${OCI_SOURCE}" \
     - <"${BUILD_CONTEXT_TAR}"
   IMAGE_ID="$(<"${IID_FILE}")"
   test -n "${IMAGE_ID}"
   python3 scripts/assert_oci_labels.py \
     "${IMAGE_ID}" "${TARGET_COMMIT}" "${TARGET_TAG}" "${OCI_SOURCE}"
   test "$(docker image inspect "${IMAGE_REF}" --format '{{.Id}}')" = "${IMAGE_ID}"
   docker compose up -d --no-build --no-deps --force-recreate app
   CONTAINER_ID="$(docker compose ps -q app)"
   test -n "${CONTAINER_ID}"
   test "$(docker inspect "${CONTAINER_ID}" --format '{{.Image}}')" = "${IMAGE_ID}"
   ```

   `git archive` incorpora o commit no pax header; o helper rejeita tar vazio, ilegível, divergente ou sem `backend/Dockerfile`, registra SHA-256 e nunca usa worktree ou arquivo untracked como contexto. A referência vem do modelo Compose resolvido e `--iidfile` registra o ID devolvido pelo build, sem depender do project name nem de containers anteriores. O assertion exige igualdade exata de revision, version e source, rejeita labels ausentes, `dirty` e `unknown`. Os defaults `unknown` continuam úteis apenas para builds não certificados.

7. Confirmar que os IDs e `StartedAt` de PostgreSQL e Redis não mudaram.
8. Confirmar o hash dos arquivos críticos entre host e container.
9. Aguardar o serviço `app` ficar healthy.

## Health checks

```bash
curl --fail --show-error http://localhost:8080/health
curl --fail --show-error http://localhost:8080/health/live
curl --fail --show-error http://localhost:8080/health/ready
```

No WSL/Docker, falha específica de `127.0.0.1:8080` deve ser comparada com localhost/IPv6 e probe interno antes de classificar o app como indisponível.

## Smoke autenticado

- Login, refresh e logout.
- Matriz `ADMIN`/`TECHNICIAN`/`VIEWER`.
- `/login`, `/apoema/dashboard` e proxy `/api/v1`.
- Mensagem Hermes real, sem fallback mock.
- Persistência de auditoria de sucesso e falha de IA.
- Macro ITIL após movimentação salva e cópia pelo histórico.
- Import IA staging-first com sugestão, aprovação e rejeição; confirmar ausência de apply automático.

## Critérios de sucesso

- Alembic no head esperado.
- App healthy e readiness com database, Redis e migrations prontos.
- PostgreSQL e Redis preservados.
- Hash host/container correspondente.
- Labels OCI de revisão, versão e origem correspondentes à release alvo.
- Smoke autenticado sem regressão.

Qualquer falha nesses critérios interrompe o rollout e aciona [rollback](rollback.md).
