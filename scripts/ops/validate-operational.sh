#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="itam_validation"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export OPERATIONAL_BASE_URL="${OPERATIONAL_BASE_URL:-http://127.0.0.1:8080}"
export ADMIN_EMAIL="${ADMIN_EMAIL:-estevao.quality@ens.edu.br}"
export ADMIN_NAME="${ADMIN_NAME:-Estevão Ribeiro}"

CLEANUP=0
if [[ "${1:-}" == "--cleanup" ]]; then
  CLEANUP=1
fi

if [[ -z "${ADMIN_PASSWORD:-}" ]]; then
  echo "ADMIN_PASSWORD must be defined locally before running operational validation. Do not commit it." >&2
  exit 1
fi

cleanup() {
  if [[ "$CLEANUP" == "1" ]]; then
    docker compose -p "$PROJECT_NAME" down -v --remove-orphans
  fi
}
trap cleanup EXIT

cd "$ROOT"

docker --version
docker compose version
docker compose -p "$PROJECT_NAME" up --build -d

deadline=$((SECONDS + 120))
until curl -fsS "$OPERATIONAL_BASE_URL/health/ready" >/dev/null; do
  if (( SECONDS > deadline )); then
    echo "Application did not become ready at $OPERATIONAL_BASE_URL" >&2
    exit 1
  fi
  sleep 2
done

check_status() {
  local path="$1"
  local expected="$2"
  local status
  status="$(curl -sS -o /dev/null -w '%{http_code}' "$OPERATIONAL_BASE_URL$path")"
  if [[ "|$expected|" != *"|$status|"* ]]; then
    echo "Unexpected status for $path. Expected $expected got $status" >&2
    exit 1
  fi
  echo "$path -> $status"
}

check_status "/health" "200"
check_status "/" "200"
check_status "/assinaturas/" "200"
check_status "/admin/" "200|302"
check_status "/api/v1/assets" "401"

PYTHON="python"
if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
fi

"$PYTHON" -m compileall -q backend/app backend/alembic
"$PYTHON" -m unittest discover -s tests

(cd frontend/itam-platform && npm run build)
docker compose -p "$PROJECT_NAME" exec -T app sh -lc "cd /app/backend && alembic current && alembic heads"

echo "Operational validation completed successfully."
