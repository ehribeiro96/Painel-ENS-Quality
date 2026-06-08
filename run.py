#!/usr/bin/env python3
"""
Ponto de entrada unico: builda o frontend quando necessario e sobe FastAPI + SPA.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import uvicorn

from src.config.settings import env_flag, load_env_files

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend" / "itam-platform"
FRONTEND_DIST = FRONTEND_DIR / "dist"


def _configure_pythonpath() -> None:
    paths = [str(BACKEND_DIR), str(PROJECT_ROOT)]
    for path in reversed(paths):
        if path not in sys.path:
            sys.path.insert(0, path)

    current = os.environ.get("PYTHONPATH")
    merged = os.pathsep.join(paths + ([current] if current else []))
    os.environ["PYTHONPATH"] = merged


def _frontend_ready() -> bool:
    return FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").is_file()


def _run_frontend_command(command: list[str]) -> None:
    print(f"[frontend] {' '.join(command)}")
    subprocess.run(command, cwd=FRONTEND_DIR, check=True)


def _ensure_frontend_build() -> None:
    mode = (os.getenv("ENS_BUILD_FRONTEND") or os.getenv("APP_BUILD_FRONTEND") or "auto").strip().lower()
    if mode in ("0", "false", "no", "off", "skip"):
        return
    if mode == "auto" and _frontend_ready():
        return

    npm = shutil.which("npm")
    if not npm:
        print("[frontend] npm nao encontrado; iniciando somente API. Gere o build manualmente em frontend/itam-platform.", file=sys.stderr)
        return

    if not (FRONTEND_DIR / "node_modules").exists():
        _run_frontend_command([npm, "ci"])
    _run_frontend_command([npm, "run", "build"])


def main() -> None:
    load_env_files()
    _configure_pythonpath()
    _ensure_frontend_build()

    host = os.getenv("APP_HOST") or os.getenv("ENS_HOST") or "127.0.0.1"
    port = int(os.getenv("APP_PORT") or os.getenv("ENS_PORT") or "8080")
    reload = env_flag("APP_RELOAD") or env_flag("ENS_RELOAD")

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
