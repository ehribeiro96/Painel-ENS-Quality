from __future__ import annotations

from typing import Any

from app.core.frontend import frontend_ready
from app.core.startup import check_postgres, check_redis, get_migration_status, runtime_state


async def dependency_health() -> dict[str, Any]:
    postgres: dict[str, Any]
    redis: dict[str, Any]
    try:
        postgres = await check_postgres()
    except Exception as exc:  # noqa: BLE001 - health response should expose failed dependency state
        runtime_state["postgres"] = "error"
        postgres = {"status": "error", "error": str(exc)}

    try:
        redis = await check_redis()
    except Exception as exc:  # noqa: BLE001
        runtime_state["redis"] = "error"
        redis = {"status": "error", "error": str(exc)}

    migration = await get_migration_status()
    frontend = frontend_ready()
    ready = postgres["status"] == "ok" and redis["status"] == "ok" and migration["status"] == "up_to_date" and frontend
    return {
        "status": "ok" if ready else "degraded",
        "postgres": postgres,
        "redis": redis,
        "frontend_ready": frontend,
        "migration": migration,
        "bootstrap_admin": runtime_state.get("bootstrap_admin"),
        "startup_complete": runtime_state.get("startup_complete", False),
    }
