#!/usr/bin/env bash
set -euo pipefail

error() {
  printf 'ERROR: %s\n' "$*" >&2
}

validate_evidence_root() {
  local release_source="${1:?release source is required}"
  local evidence_root="${2:?evidence root is required}"
  local release_root
  local resolved_evidence

  if ! release_root="$(
    git -C "${release_source}" rev-parse --show-toplevel
  )"; then
    error "unable to resolve release source"
    return 1
  fi

  if ! release_root="$(realpath -m "${release_root}")"; then
    error "unable to normalize release source"
    return 1
  fi

  if ! resolved_evidence="$(realpath -m "${evidence_root}")"; then
    error "unable to normalize EVIDENCE_ROOT"
    return 1
  fi

  case "${resolved_evidence}/" in
    "${release_root}/"*)
      error "EVIDENCE_ROOT must be outside the repository"
      return 1
      ;;
  esac

  printf '%s\n' "${resolved_evidence}"
}

assert_clean_release_source() {
  local release_source="${1:?release source is required}"
  local evidence_root="${2:?evidence root is required}"
  local status_file

  if ! evidence_root="$(
    validate_evidence_root "${release_source}" "${evidence_root}"
  )"; then
    return 1
  fi

  if ! mkdir -p "${evidence_root}"; then
    error "unable to create EVIDENCE_ROOT"
    return 1
  fi

  if ! status_file="$(mktemp "${evidence_root}/git-status.XXXXXX")"; then
    error "unable to create git status evidence"
    return 1
  fi

  if ! chmod 600 "${status_file}"; then
    error "unable to protect git status evidence"
    return 1
  fi

  if ! git -C "${release_source}" \
    status \
    --porcelain=v1 \
    --untracked-files=all \
    >"${status_file}"; then
    error "git status failed for release source"
    return 1
  fi

  if [[ -s "${status_file}" ]]; then
    error "release source is not clean"
    cat "${status_file}" >&2
    return 1
  fi

  printf '%s\n' "${status_file}"
}

verify_build_context() {
  local release_source="${1:?release source is required}"
  local build_context_tar="${2:?build context tar is required}"
  local target_commit="${3:?target commit is required}"
  local archived_commit

  if [[ ! -r "${build_context_tar}" || ! -s "${build_context_tar}" ]]; then
    error "build context tar is empty or unreadable"
    return 1
  fi

  if ! archived_commit="$(
    git -C "${release_source}" get-tar-commit-id <"${build_context_tar}"
  )"; then
    error "unable to read build context commit"
    return 1
  fi

  if [[ "${archived_commit}" != "${target_commit}" ]]; then
    error "build context commit mismatch"
    return 1
  fi

  if ! tar -tf "${build_context_tar}" "backend/Dockerfile" >/dev/null 2>&1; then
    error "build context does not contain backend/Dockerfile"
    return 1
  fi

  printf '%s\n' "${archived_commit}"
}

create_build_context() {
  local release_source="${1:?release source is required}"
  local evidence_root="${2:?evidence root is required}"
  local target_commit="${3:?target commit is required}"
  local build_context_tar

  if ! evidence_root="$(
    validate_evidence_root "${release_source}" "${evidence_root}"
  )"; then
    return 1
  fi

  if ! mkdir -p "${evidence_root}"; then
    error "unable to create EVIDENCE_ROOT"
    return 1
  fi

  if ! git -C "${release_source}" cat-file -e "${target_commit}^{commit}"; then
    error "target commit is not available"
    return 1
  fi

  if ! build_context_tar="$(
    mktemp "${evidence_root}/build-context.${target_commit}.XXXXXX.tar"
  )"; then
    error "unable to create build context archive"
    return 1
  fi

  if ! chmod 600 "${build_context_tar}"; then
    error "unable to protect build context archive"
    return 1
  fi

  if ! git -C "${release_source}" archive \
    --format=tar \
    --output="${build_context_tar}" \
    "${target_commit}"; then
    error "unable to archive target commit"
    return 1
  fi

  if ! verify_build_context \
    "${release_source}" \
    "${build_context_tar}" \
    "${target_commit}" \
    >/dev/null; then
    return 1
  fi

  if ! sha256sum "${build_context_tar}" >"${build_context_tar}.sha256"; then
    error "unable to hash build context archive"
    return 1
  fi

  if ! chmod 600 "${build_context_tar}.sha256"; then
    error "unable to protect build context hash"
    return 1
  fi
  printf '%s\n' "${build_context_tar}"
}

validate_certified_revision() {
  local repository="${1:?repository is required}"
  local revision="${2:-}"

  if [[ ! "${revision}" =~ ^[0-9a-f]{40}$ ]] &&
     [[ ! "${revision}" =~ ^[0-9a-f]{64}$ ]]; then
    error "rollback image has no certified source revision"
    return 1
  fi

  if ! git -C "${repository}" cat-file -e "${revision}^{commit}"; then
    error "rollback revision is not an available commit"
    return 1
  fi

  printf '%s\n' "${revision}"
}

validate_rollback_source() {
  local rollback_source="${1:?rollback source is required}"
  local evidence_root="${2:?evidence root is required}"
  local rollback_revision="${3:?rollback revision is required}"
  local actual_revision

  if ! validate_certified_revision \
    "${rollback_source}" \
    "${rollback_revision}" \
    >/dev/null; then
    return 1
  fi

  if ! actual_revision="$(
    git -C "${rollback_source}" rev-parse HEAD
  )"; then
    error "unable to resolve rollback source revision"
    return 1
  fi
  if [[ "${actual_revision}" != "${rollback_revision}" ]]; then
    error "rollback source revision mismatch"
    return 1
  fi

  if ! assert_clean_release_source \
    "${rollback_source}" \
    "${evidence_root}" \
    >/dev/null; then
    return 1
  fi

  if [[ ! -f "${rollback_source}/docker-compose.yml" ]]; then
    error "historical Compose file is missing"
    return 1
  fi

  printf '%s\n' "${rollback_source}/docker-compose.yml"
}

validate_rollback_override() {
  local override_path="${1:?rollback override is required}"

  python3 - "${override_path}" <<'PY'
from pathlib import Path
import sys
import yaml

path = Path(sys.argv[1])
document = yaml.safe_load(path.read_text(encoding="utf-8"))
expected = {
    "services": {
        "app": {
            "image": "${APP_IMAGE:?APP_IMAGE is required}",
            "environment": {"APP_AUTO_MIGRATE": "false"},
        }
    }
}
if document != expected:
    raise SystemExit("ERROR: rollback override is not minimal and fail-closed")
PY
}

assert_image_reference() {
  local image_reference="${1:?image reference is required}"
  local expected_image_id="${2:?expected image ID is required}"
  local actual_image_id

  if ! actual_image_id="$(
    docker image inspect "${image_reference}" --format '{{.Id}}'
  )"; then
    error "unable to inspect rollback image reference"
    return 1
  fi

  if [[ "${actual_image_id}" != "${expected_image_id}" ]]; then
    error "rollback image reference mismatch"
    return 1
  fi
}

assert_container_image() {
  local container_id="${1:?container ID is required}"
  local expected_image_id="${2:?expected image ID is required}"
  local actual_image_id

  if ! actual_image_id="$(
    docker inspect "${container_id}" --format '{{.Image}}'
  )"; then
    error "unable to inspect rolled back container"
    return 1
  fi

  if [[ "${actual_image_id}" != "${expected_image_id}" ]]; then
    error "rolled back container image mismatch"
    return 1
  fi
}

usage() {
  cat >&2 <<'EOF'
usage:
  release_integrity.sh assert-clean RELEASE_SOURCE EVIDENCE_ROOT
  release_integrity.sh create-build-context RELEASE_SOURCE EVIDENCE_ROOT TARGET_COMMIT
  release_integrity.sh verify-build-context RELEASE_SOURCE BUILD_CONTEXT_TAR TARGET_COMMIT
  release_integrity.sh validate-revision REPOSITORY REVISION
  release_integrity.sh validate-rollback-source ROLLBACK_SOURCE EVIDENCE_ROOT REVISION
  release_integrity.sh validate-rollback-override OVERRIDE_PATH
  release_integrity.sh assert-image-reference IMAGE_REFERENCE EXPECTED_IMAGE_ID
  release_integrity.sh assert-container-image CONTAINER_ID EXPECTED_IMAGE_ID
EOF
  return 2
}

main() {
  local command="${1:-}"
  if [[ -z "${command}" ]]; then
    usage
  fi
  shift

  case "${command}" in
    assert-clean) assert_clean_release_source "$@" ;;
    create-build-context) create_build_context "$@" ;;
    verify-build-context) verify_build_context "$@" ;;
    validate-revision) validate_certified_revision "$@" ;;
    validate-rollback-source) validate_rollback_source "$@" ;;
    validate-rollback-override) validate_rollback_override "$@" ;;
    assert-image-reference) assert_image_reference "$@" ;;
    assert-container-image) assert_container_image "$@" ;;
    *) usage ;;
  esac
}

main "$@"
