#!/usr/bin/env bash
# Run the local validation suite used before accepting Hermes-generated changes.

set -euo pipefail

# Keep the default project root fixed, while allowing local override for tests.
PROJECT_ROOT="${HERMES_PROJECT_ROOT:-$HOME/projects/Painel-ENS-Quality}"

cd "$PROJECT_ROOT"

# Validate backend Python syntax without printing source files.
python -m compileall -q backend/app backend/alembic tests

# Run the project unittest suite.
python -m unittest discover -s tests

# Build the existing React/Vite frontend without adding dependencies.
cd frontend/itam-platform
npm run build
