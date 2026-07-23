#!/usr/bin/env bash
set -euo pipefail

: "${TARGET_TAG:?TARGET_TAG is required}"
TAG_REF="refs/tags/${TARGET_TAG}"
git check-ref-format "${TAG_REF}" >/dev/null
ORIGIN_URL="$(git remote get-url origin)"
case "${ORIGIN_URL}" in
  git@github.com:ehribeiro96/Painel-ENS-Quality.git|https://github.com/ehribeiro96/Painel-ENS-Quality|https://github.com/ehribeiro96/Painel-ENS-Quality.git) ;;
  *) printf 'unexpected origin URL\n' >&2; exit 1 ;;
esac
git fetch --prune --tags origin >/dev/null
REMOTE_REFS="$(git ls-remote --exit-code origin "${TAG_REF}" "${TAG_REF}^{}")"
REMOTE_TAG_OBJECT=""
REMOTE_COMMIT=""
while IFS=$'\t' read -r object ref; do
  case "${ref}" in
    "${TAG_REF}") test -z "${REMOTE_TAG_OBJECT}"; REMOTE_TAG_OBJECT="${object}" ;;
    "${TAG_REF}^{}") test -z "${REMOTE_COMMIT}"; REMOTE_COMMIT="${object}" ;;
    *) exit 1 ;;
  esac
done <<< "${REMOTE_REFS}"
test -n "${REMOTE_TAG_OBJECT}"
test -n "${REMOTE_COMMIT}"
git rev-parse --verify "${TAG_REF}" >/dev/null
test "$(git cat-file -t "${TAG_REF}")" = "tag" || {
  printf 'release tag must be annotated: %s\n' "${TARGET_TAG}" >&2
  exit 1
}
test "$(git rev-parse "${TAG_REF}")" = "${REMOTE_TAG_OBJECT}"
TARGET_COMMIT="$(git rev-parse "${TAG_REF}^{}")"
test -n "${TARGET_COMMIT}"
test "${TARGET_COMMIT}" = "${REMOTE_COMMIT}"
git cat-file -e "${TARGET_COMMIT}^{commit}"
printf '%s\n' "${TARGET_COMMIT}"
