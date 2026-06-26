from app.api.v1.routes import (
    ai_chat,
    artifacts,
    assets,
    audit,
    auth,
    dashboard,
    designer,
    imports,
    macros,
    rag,
    search,
    signatures,
    users,
)
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
api_router.include_router(artifacts.router)
api_router.include_router(dashboard.router)
api_router.include_router(designer.router)
api_router.include_router(imports.router)
api_router.include_router(signatures.router)
api_router.include_router(macros.router)
api_router.include_router(macros.movements_router)
api_router.include_router(ai_chat.router)
api_router.include_router(rag.router)
api_router.include_router(audit.router)
api_router.include_router(search.router)
