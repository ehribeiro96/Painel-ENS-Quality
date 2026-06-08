from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FRONTEND_DIST = PROJECT_ROOT / "frontend" / "itam-platform" / "dist"
RESERVED_PREFIXES = ("api/", "docs", "redoc", "openapi.json", "health")


def frontend_dist_dir() -> Path:
    configured = os.getenv("FRONTEND_DIST") or os.getenv("ENS_FRONTEND_DIST")
    return Path(configured).resolve() if configured else DEFAULT_FRONTEND_DIST


def frontend_ready() -> bool:
    dist_dir = frontend_dist_dir()
    return dist_dir.exists() and (dist_dir / "index.html").is_file()


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _spa_response(full_path: str) -> Response:
    if any(full_path == prefix.rstrip("/") or full_path.startswith(prefix) for prefix in RESERVED_PREFIXES):
        return JSONResponse({"detail": "not_found"}, status_code=404)

    dist_dir = frontend_dist_dir()
    index_file = dist_dir / "index.html"

    if not index_file.is_file():
        return JSONResponse(
            {
                "error": "frontend_not_built",
                "detail": "Execute `npm run build` em frontend/itam-platform ou habilite ENS_BUILD_FRONTEND.",
                "frontend_dist": str(dist_dir),
            },
            status_code=503,
        )

    if full_path:
        requested = (dist_dir / full_path).resolve()
        if _is_relative_to(requested, dist_dir) and requested.is_file():
            return FileResponse(requested)

    return FileResponse(index_file)


def mount_frontend(app: FastAPI) -> None:
    dist_dir = frontend_dist_dir()
    assets_dir = dist_dir / "_assets"

    if assets_dir.exists():
        app.mount("/_assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend_root() -> Response:
        return _spa_response("")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend_path(full_path: str) -> Response:
        return _spa_response(full_path)
