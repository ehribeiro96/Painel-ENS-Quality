from __future__ import annotations

import asyncio
import re
import traceback
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, TypeVar

import structlog
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.core.config.settings import _is_weak_jwt_secret, settings
from app.core.database.session import AsyncSessionLocal, engine
from app.core.frontend import frontend_dist_dir, frontend_ready
from app.core.security.passwords import hash_password
from app.domains.users.models import User
from app.shared.enums import Role, UserStatus
from app.shared.models import utc_now
from redis import asyncio as redis
from sqlalchemy import select, text

logger = structlog.get_logger()
T = TypeVar("T")

_SENSITIVE_PATTERNS = (
    re.compile(r"(postgresql(?:\+asyncpg)?|postgres|redis)://[^\s]+", re.IGNORECASE),
    re.compile(r"\b(password|token|secret|authorization|cookie)=([^\s]+)", re.IGNORECASE),
)

BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
ALEMBIC_DIR = BACKEND_DIR / "alembic"

runtime_state: dict[str, Any] = {
    "startup_complete": False,
    "postgres": "unknown",
    "redis": "unknown",
    "migration": {"status": "unknown", "current_revision": None, "head_revision": None},
    "bootstrap_admin": "not_started",
    "current_step": None,
    "last_startup_error": None,
}


def safe_startup_config_snapshot() -> dict[str, Any]:
    frontend_dist = frontend_dist_dir()
    return {
        "environment": settings.environment,
        "app_startup_checks": settings.app_startup_checks,
        "app_auto_migrate": settings.app_auto_migrate,
        "app_startup_step_timeout_seconds": settings.app_startup_step_timeout_seconds,
        "admin_email_set": bool(settings.admin_email),
        "admin_name_set": bool(settings.admin_name),
        "admin_password_set": bool(settings.admin_password),
        "jwt_secret_key_set": bool(settings.jwt_secret_key),
        "database_url_set": bool(settings.database_url),
        "redis_url_set": bool(settings.redis_url),
        "allowed_origins_count": len(settings.allowed_origins),
        "frontend_dist_dir": str(frontend_dist),
        "frontend_index_exists": (frontend_dist / "index.html").is_file(),
        "frontend_assets_exists": (frontend_dist / "_assets").exists(),
    }


def _redact_sensitive_text(value: object) -> str:
    text_value = str(value)
    for pattern in _SENSITIVE_PATTERNS:
        text_value = pattern.sub(
            lambda match: f"{match.group(1)}://<REDACTED_DSN>"
            if "://" in match.group(0)
            else f"{match.group(1)}=<REDACTED>",
            text_value,
        )
    return text_value


def _record_startup_failure(step: str, exc: BaseException) -> None:
    error = {
        "failed_step": step,
        "exception_type": type(exc).__name__,
        "exception_message": _redact_sensitive_text(exc),
        "traceback": _redact_sensitive_text("".join(traceback.format_exception(type(exc), exc, exc.__traceback__))),
    }
    runtime_state["last_startup_error"] = {
        "failed_step": error["failed_step"],
        "exception_type": error["exception_type"],
        "exception_message": error["exception_message"],
    }
    logger.error("startup_failed", **error)


async def _run_startup_step(
    step: str,
    begin_event: str,
    ok_event: str,
    operation: Callable[[], Awaitable[T]],
    *,
    timeout_seconds: float | None = None,
) -> T:
    timeout = timeout_seconds if timeout_seconds is not None else settings.app_startup_step_timeout_seconds
    runtime_state["current_step"] = step
    logger.info("startup_step_begin", step=step, timeout_seconds=timeout)
    logger.info(begin_event)
    try:
        result = await asyncio.wait_for(operation(), timeout=timeout)
    except TimeoutError as exc:
        timeout_error = TimeoutError(f"{step}_timeout_after_{timeout:g}s")
        logger.error("startup_step_timeout", step=step, timeout_seconds=timeout)
        _record_startup_failure(step, timeout_error)
        raise timeout_error from exc
    except Exception as exc:
        logger.error(
            "startup_step_error",
            step=step,
            exception_type=type(exc).__name__,
            exception_message=_redact_sensitive_text(exc),
        )
        _record_startup_failure(step, exc)
        raise
    logger.info("startup_step_ok", step=step)
    logger.info(ok_event)
    return result


def alembic_config() -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(ALEMBIC_DIR))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


async def retry_async(name: str, operation, attempts: int | None = None, delay_seconds: float | None = None) -> Any:
    max_attempts = attempts or settings.dependency_retry_attempts
    delay = delay_seconds if delay_seconds is not None else settings.dependency_retry_delay_seconds
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()
        except Exception as exc:  # noqa: BLE001 - startup diagnostics must preserve the root error
            last_error = exc
            logger.warning(
                "dependency_retry",
                dependency=name,
                attempt=attempt,
                max_attempts=max_attempts,
                error=_redact_sensitive_text(exc),
            )
            if attempt < max_attempts:
                await asyncio.sleep(delay)
    raise RuntimeError(f"{name}_unavailable") from last_error


async def check_postgres() -> dict[str, Any]:
    async with engine.connect() as connection:
        value = await connection.scalar(text("select 1"))
    runtime_state["postgres"] = "ok"
    return {"status": "ok", "result": value}


async def check_redis() -> dict[str, Any]:
    client = redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
    try:
        pong = await client.ping()
    finally:
        await client.aclose()
    runtime_state["redis"] = "ok"
    return {"status": "ok", "result": bool(pong)}


async def wait_for_dependencies() -> None:
    if not settings.app_startup_checks:
        return
    await _run_startup_step(
        "postgres",
        "database_wait_begin",
        "database_wait_ok",
        lambda: retry_async("postgres", check_postgres),
    )
    await _run_startup_step(
        "redis",
        "redis_wait_begin",
        "redis_wait_ok",
        lambda: retry_async("redis", check_redis),
    )


def get_migration_status_sync() -> dict[str, Any]:
    config = alembic_config()
    head = ScriptDirectory.from_config(config).get_current_head()
    return {"status": "unknown", "current_revision": None, "head_revision": head}


async def get_migration_status() -> dict[str, Any]:
    status = await asyncio.to_thread(get_migration_status_sync)
    try:
        async with engine.connect() as connection:
            current = await connection.scalar(text("select version_num from alembic_version"))
    except Exception as exc:  # noqa: BLE001 - health endpoint reports details as state
        current = None
        status["error"] = str(exc)
    status["current_revision"] = current
    status["status"] = "up_to_date" if current and current == status["head_revision"] else "pending"
    runtime_state["migration"] = status
    return status


def run_migrations_sync() -> None:
    command.upgrade(alembic_config(), "head")


async def run_migrations() -> None:
    if not settings.app_auto_migrate:
        runtime_state["migration"] = await get_migration_status()
        return
    runtime_state["migration"] = {"status": "running", "current_revision": None, "head_revision": None}
    await asyncio.to_thread(run_migrations_sync)
    runtime_state["migration"] = await get_migration_status()


async def bootstrap_admin() -> None:
    if not settings.admin_email or not settings.admin_password:
        runtime_state["bootstrap_admin"] = "skipped_missing_env"
        logger.warning("bootstrap_admin_skipped", reason="ADMIN_EMAIL_or_ADMIN_PASSWORD_missing")
        return

    if len(settings.admin_password) < 10:
        runtime_state["bootstrap_admin"] = "failed_password_policy"
        raise RuntimeError("ADMIN_PASSWORD must have at least 10 characters")

    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.email == settings.admin_email, User.deleted_at.is_(None)))
            if user is None:
                user = User(
                    name=settings.admin_name,
                    email=settings.admin_email,
                    password_hash=hash_password(settings.admin_password),
                    status=UserStatus.ACTIVE,
                    role=Role.ADMIN,
                    created_by=None,
                    updated_by=None,
                )
                session.add(user)
                runtime_state["bootstrap_admin"] = "created"
            else:
                changed = False
                if user.role != Role.ADMIN:
                    user.role = Role.ADMIN
                    changed = True
                if user.status != UserStatus.ACTIVE:
                    user.status = UserStatus.ACTIVE
                    changed = True
                if not user.password_hash:
                    user.password_hash = hash_password(settings.admin_password)
                    changed = True
                if changed:
                    user.updated_at = utc_now()
                    runtime_state["bootstrap_admin"] = "updated"
                else:
                    runtime_state["bootstrap_admin"] = "exists"


async def validate_settings_for_startup() -> None:
    logger.info("settings_validation_snapshot", **safe_startup_config_snapshot())
    if settings.environment != "local" and _is_weak_jwt_secret(settings.jwt_secret_key):
        raise RuntimeError("JWT_SECRET_KEY must be changed outside local")
    if settings.environment == "production" and settings.admin_password == "<DEFINIR_LOCALMENTE_NO_ENV>":
        raise RuntimeError("ADMIN_PASSWORD must be changed in production")


async def check_frontend_runtime() -> None:
    logger.info("frontend_check_state", frontend_dist_dir=str(frontend_dist_dir()), frontend_ready=frontend_ready())
    if settings.app_startup_checks and not frontend_ready():
        raise RuntimeError(f"frontend_dist_not_ready:{frontend_dist_dir()}")


async def check_legacy_runtime() -> None:
    try:
        __import__("src.legacy.flask_app")
    except Exception as exc:
        raise RuntimeError("legacy_signature_import_failed") from exc


async def enterprise_startup() -> None:
    logger.info("startup_begin")
    runtime_state["startup_complete"] = False
    runtime_state["last_startup_error"] = None
    try:
        await _run_startup_step("settings_validation", "settings_validation_begin", "settings_validation_ok", validate_settings_for_startup)
        await wait_for_dependencies()
        await _run_startup_step("migrations", "migrations_begin", "migrations_ok", run_migrations)
        await _run_startup_step("bootstrap_admin", "bootstrap_admin_begin", "bootstrap_admin_ok", bootstrap_admin)
        await _run_startup_step("frontend_check", "frontend_check_begin", "frontend_check_ok", check_frontend_runtime)
        await _run_startup_step("legacy_mount_check", "legacy_mount_check_begin", "legacy_mount_check_ok", check_legacy_runtime)
        runtime_state["startup_complete"] = True
        runtime_state["current_step"] = None
        logger.info("startup_complete")
    except Exception:
        runtime_state["startup_complete"] = False
        raise
