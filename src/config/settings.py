from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Sequence

# Diretório raiz do projeto (pasta que contém src/, assets/, frontend/, config/ etc).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Ordem padrão de arquivos .env carregados (o primeiro que existir é lido primeiro).
DEFAULT_ENV_FILES: tuple[Path, ...] = (
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / ".env.local",
    PROJECT_ROOT.parent / ".env",
)


def load_env_files(env_files: Sequence[Path] | Iterable[Path] = DEFAULT_ENV_FILES) -> None:
    """
    Carrega variáveis de ambiente a partir de arquivos .env, sem sobrescrever
    valores já definidos no ambiente.
    """
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        load_dotenv = None

    for env_file in env_files:
        if not env_file or not Path(env_file).exists():
            continue
        if load_dotenv:
            load_dotenv(env_file, override=False)
            continue

        # Fallback simples caso python-dotenv não esteja disponível.
        try:
            content = Path(env_file).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = Path(env_file).read_text(encoding="cp1252")
        for raw in content.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key:
                continue
            os.environ.setdefault(key, value.strip().strip("\"'"))


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def assets_dir() -> Path:
    return PROJECT_ROOT / "assets"


def templates_dir() -> Path:
    return assets_dir() / "templates"


def static_dir() -> Path:
    return assets_dir() / "static"


def data_dir() -> Path:
    return Path(os.getenv("ENS_DATA_DIR") or (PROJECT_ROOT / "data"))


def preview_cache_dir() -> Path:
    return Path(os.getenv("ENS_PREVIEW_CACHE_DIR") or (data_dir() / "previews"))


def backups_dir() -> Path:
    return data_dir() / "backups"


def default_db_path() -> Path:
    return Path(os.getenv("ENS_DB_PATH") or (data_dir() / "ens.db"))


def frontend_dir() -> Path:
    return PROJECT_ROOT / "frontend"


def frontend_app_dir() -> Path:
    return frontend_dir() / "app"


def frontend_dist_dir() -> Path:
    return frontend_dir() / "dist"


def resolve_frontend_dist() -> Path:
    """
    Resolve onde está o build da SPA React.
    Prioridade:
    1) FRONTEND_DIST (variável de ambiente)
    2) frontend/dist (bundle movido para produção)
    3) frontend/app/dist (saída padrão do Vite)
    """
    env_path = os.getenv("FRONTEND_DIST")
    if env_path:
        return Path(env_path)

    for candidate in (frontend_dist_dir(), frontend_app_dir() / "dist"):
        if candidate.exists():
            return candidate

    # Fallback (mesmo que ainda não exista)
    return frontend_app_dir() / "dist"


__all__ = [
    "PROJECT_ROOT",
    "DEFAULT_ENV_FILES",
    "assets_dir",
    "templates_dir",
    "static_dir",
    "data_dir",
    "backups_dir",
    "preview_cache_dir",
    "default_db_path",
    "frontend_dir",
    "frontend_app_dir",
    "frontend_dist_dir",
    "resolve_frontend_dist",
    "load_env_files",
    "env_flag",
]
