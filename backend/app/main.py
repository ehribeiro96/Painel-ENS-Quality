from __future__ import annotations

import secrets
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager

import structlog
from app.api.v1.router import api_router
from app.core.config.settings import settings
from app.core.database.session import engine
from app.core.frontend import frontend_ready, mount_frontend
from app.core.health import dependency_health
from app.core.legacy import mount_legacy_signature_apps
from app.core.logging.setup import configure_logging
from app.core.observability.metrics import instrument_sqlalchemy, metrics
from app.core.startup import enterprise_startup, runtime_state
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

configure_logging()
logger = structlog.get_logger()

_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)
_STRICT_CSP = (
    "default-src 'self'; base-uri 'self'; object-src 'none'; img-src 'self' data: https:; "
    "style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-ancestors 'self'"
)
_LEGACY_CSP = (
    "default-src 'self'; base-uri 'self'; object-src 'none'; img-src 'self' data: https:; "
    "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'self'"
)
_STRICT_CSP_REPORT_ONLY = (
    "default-src 'self'; base-uri 'self'; object-src 'none'; img-src 'self' data: https:; "
    "style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'self'"
)
_METRICS_TOKEN_HEADER = "x-metrics-token"


@asynccontextmanager
async def lifespan(_: FastAPI):
    instrument_sqlalchemy(engine)
    await enterprise_startup()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

legacy_mounts = mount_legacy_signature_apps(app)


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def _rate_limit_key(request: Request) -> tuple[str, int]:
    ip = _client_ip(request) or "unknown"
    if request.url.path.startswith(f"{settings.api_prefix}/auth"):
        return f"auth:{ip}", settings.auth_rate_limit_per_minute
    return f"api:{ip}", settings.rate_limit_per_minute


def _is_rate_limited(request: Request) -> bool:
    if not request.url.path.startswith(settings.api_prefix):
        return False
    key, limit = _rate_limit_key(request)
    if limit <= 0:
        return False
    now = time.monotonic()
    bucket = _rate_limit_buckets[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= limit:
        return True
    bucket.append(now)
    return False


def _is_legacy_path(path: str) -> bool:
    return path.startswith("/admin") or path.startswith("/assinaturas")


def _apply_security_headers(response, path: str) -> None:
    response.headers.setdefault("x-content-type-options", "nosniff")
    response.headers.setdefault("x-frame-options", "SAMEORIGIN")
    response.headers.setdefault("referrer-policy", "same-origin")
    response.headers.setdefault("permissions-policy", "camera=(), microphone=(), geolocation=()")
    if _is_legacy_path(path):
        response.headers["content-security-policy"] = _LEGACY_CSP
        response.headers["content-security-policy-report-only"] = _STRICT_CSP_REPORT_ONLY
    else:
        response.headers["content-security-policy"] = _STRICT_CSP
        if "content-security-policy-report-only" in response.headers:
            del response.headers["content-security-policy-report-only"]
    if settings.environment == "production":
        response.headers.setdefault("strict-transport-security", "max-age=31536000; includeSubDomains")


def _require_metrics_access(request: Request) -> None:
    if settings.environment == "local":
        return
    configured_token = settings.metrics_token.strip()
    if not configured_token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="metrics_disabled_without_token")
    provided_token = request.headers.get(_METRICS_TOKEN_HEADER, "").strip()
    if not provided_token or not secrets.compare_digest(provided_token, configured_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_metrics_token")


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    correlation_id = request.headers.get("x-correlation-id", request_id)
    started = time.perf_counter()
    ip_address = _client_ip(request)
    request.state.request_id = request_id
    request.state.correlation_id = correlation_id
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        correlation_id=correlation_id,
        path=request.url.path,
        ip=ip_address,
        source=request.headers.get("x-audit-source", "api"),
    )
    try:
        if _is_rate_limited(request):
            metrics.increment("itam_rate_limited_requests_total", {"path": request.url.path})
            response = JSONResponse({"detail": "rate_limit_exceeded"}, status_code=429)
        else:
            response = await call_next(request)
        duration_ms = (time.perf_counter() - started) * 1000
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        metrics.increment(
            "itam_http_requests_total",
            {"method": request.method, "path": route_path, "status": str(response.status_code)},
        )
        metrics.observe("itam_http_request_duration_ms", duration_ms, {"method": request.method, "path": route_path})
        response.headers["x-request-id"] = request_id
        response.headers["x-correlation-id"] = correlation_id
        _apply_security_headers(response, request.url.path)
        logger.info(
            "request_completed",
            method=request.method,
            status_code=response.status_code,
            user_id=getattr(request.state, "user_id", None),
            action=request.method,
            entity=route_path.split("/")[3] if route_path.startswith(settings.api_prefix) and len(route_path.split("/")) > 3 else None,
            duration_ms=round(duration_ms, 2),
            source=request.headers.get("x-audit-source", "api"),
            ip=ip_address,
        )
        return response
    except Exception:
        duration_ms = (time.perf_counter() - started) * 1000
        metrics.increment("itam_http_requests_total", {"method": request.method, "path": request.url.path, "status": "500"})
        logger.exception("request_failed", method=request.method, duration_ms=round(duration_ms, 2), ip=ip_address)
        raise
    finally:
        structlog.contextvars.clear_contextvars()


@app.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "frontend_ready": frontend_ready(),
        "legacy_mounts": legacy_mounts,
        "startup": runtime_state,
    }


@app.get("/health/live")
async def health_live() -> dict[str, object]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/ready")
async def health_ready():
    payload = await dependency_health()
    return JSONResponse(payload, status_code=200 if payload["status"] == "ok" else 503)


@app.get("/health/dependencies")
async def health_dependencies() -> dict[str, object]:
    return await dependency_health()


@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics(request: Request) -> PlainTextResponse:
    _require_metrics_access(request)
    return PlainTextResponse(metrics.render_prometheus(), media_type="text/plain; version=0.0.4")


app.include_router(api_router, prefix=settings.api_prefix)
mount_frontend(app)
