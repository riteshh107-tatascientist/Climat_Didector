"""
ClimateGuard AI — FastAPI application entrypoint.
Run locally with:  uvicorn app.main:app --reload --app-dir backend
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.models.db import init_db
from app.ml.predictors import preload_all_models
from app.api.routes import climate, system, auth, dashboard, locations, models_info

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("climateguard")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Powered Climate Risk, Sustainability & Resilience Intelligence Platform.\n\n"
        "Authenticate via `/api/v1/auth/login` to receive a bearer token, then pass it as "
        "`Authorization: Bearer <token>` on subsequent requests. Prediction endpoints also "
        "work anonymously (for demo/judge use) — results just won't be tied to an account."
    ),
)

# CORS: origins are environment-driven (see .env.example), never hardcoded.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE on rate limiting: this app is structured so a rate limiter (e.g.
# slowapi/starlette-limiter) can be dropped in as another middleware layer
# here without touching route code — each route is a plain, idempotent-safe
# handler with no shared mutable state except the documented token
# blocklist in app/api/deps.py. Not enabled by default for the local/demo
# deployment target; enable it before any public production deployment.

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(system.router, prefix=settings.API_PREFIX)
app.include_router(climate.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(locations.router, prefix=settings.API_PREFIX)
app.include_router(models_info.router, prefix=settings.API_PREFIX)


# --- Graceful error handling: never leak Python tracebacks to clients ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "detail": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error handling %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "database_unavailable", "detail": "A database error occurred. Please try again."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error handling %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_error", "detail": "Something went wrong. Please try again later."},
    )


@app.on_event("startup")
def on_startup():
    init_db()
    status_map = preload_all_models()
    failed = {k: v for k, v in status_map.items() if not v["loaded"]}
    if failed:
        raise RuntimeError(f"Model(s) failed to load at startup: {failed}")
    logger.info("ClimateGuard AI startup complete. Models loaded: %s", status_map)


@app.get("/")
def root():
    return {
        "message": "ClimateGuard AI API",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
    }
