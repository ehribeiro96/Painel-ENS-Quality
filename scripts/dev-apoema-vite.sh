#!/usr/bin/env bash
set -euo pipefail

cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform

PORT="${APOEMA_VITE_PORT:-5175}"

PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" \
npm run dev -- --host 127.0.0.1 --port "$PORT" --strictPort
