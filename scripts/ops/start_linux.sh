#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Candidatos de diretorio do projeto integrado (tem run.py e backend/app/main.py)
CANDIDATES=(
  "$BASE_DIR/../.."
  "$BASE_DIR/../../Portal-Assinatura-V2"
)

PROJ_DIR=""
for c in "${CANDIDATES[@]}"; do
  if [[ -f "$c/run.py" && -f "$c/backend/app/main.py" ]]; then
    PROJ_DIR="$c"
    break
  fi
done

if [[ -z "$PROJ_DIR" ]]; then
  echo "Nao consegui localizar run.py + backend/app/main.py acima de $BASE_DIR" >&2
  exit 1
fi

cd "$PROJ_DIR"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r requirements-legacy.txt

# Carrega .env (.env ou .env.local no projeto ou um nivel acima)
ENV_CANDIDATES=(
  "$PROJ_DIR/.env"
  "$PROJ_DIR/.env.local"
  "$(dirname "$PROJ_DIR")/.env"
)
for env_file in "${ENV_CANDIDATES[@]}"; do
  if [[ -f "$env_file" ]]; then
    set -a
    # shellcheck disable=SC1090
    . "$env_file"
    set +a
    break
  fi
done

python run.py
