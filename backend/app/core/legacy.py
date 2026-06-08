from __future__ import annotations

import structlog
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

logger = structlog.get_logger()


def mount_legacy_signature_apps(app: FastAPI) -> list[str]:
    try:
        from src.legacy.flask_app import criar_aplicativo
    except Exception as exc:
        logger.warning("legacy_signature_import_failed", error=str(exc))
        return []

    mounted: list[str] = []
    try:
        app.mount("/admin", WSGIMiddleware(criar_aplicativo("admin")))
        mounted.append("/admin")
        app.mount("/assinaturas", WSGIMiddleware(criar_aplicativo("publico")))
        mounted.append("/assinaturas")
    except Exception as exc:
        logger.warning("legacy_signature_mount_failed", error=str(exc))
        return mounted

    logger.info("legacy_signature_apps_mounted", paths=mounted)
    return mounted
