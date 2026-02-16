"""FastAPI application entrypoint.

Standards: python_clean.mdc
- Async context managers for cleanup
- Structured logging setup
"""

from contextlib import asynccontextmanager
from logging import DEBUG, INFO
from typing import Any, AsyncGenerator, Callable

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.v1.router import api_router
from app.config import get_settings

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        INFO if not settings.debug else DEBUG
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class OptionsMiddleware:
    """ASGI middleware to handle OPTIONS requests at the lowest level.
    
    This runs before FastAPI route matching, ensuring OPTIONS requests
    are handled before any dependency evaluation can occur.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Intercept OPTIONS requests at ASGI level."""
        try:
            if scope["type"] == "http" and scope["method"] == "OPTIONS":
                # Get origin from headers (headers are list of (bytes, bytes) tuples)
                origin = ""
                for header_name, header_value in scope.get("headers", []):
                    if header_name.lower() == b"origin":
                        origin = header_value.decode("utf-8", errors="ignore")
                        break
                
                logger.info(
                    "options_request_intercepted_asgi",
                    path=scope.get("path", ""),
                    origin=origin,
                )
                
                # Determine allowed origin
                allowed_origin = None
                if settings.app_env == "development":
                    allowed_origin = origin or "http://localhost:3000"
                elif origin:
                    cors_origins = getattr(settings, "cors_origins", [])
                    if origin in cors_origins:
                        allowed_origin = origin
                
                # Create response
                response_headers = []
                if allowed_origin:
                    response_headers = [
                        (b"access-control-allow-origin", allowed_origin.encode()),
                        (b"access-control-allow-credentials", b"true"),
                        (b"access-control-allow-methods", b"GET, POST, PUT, PATCH, DELETE, OPTIONS"),
                        (b"access-control-allow-headers", b"*"),
                        (b"access-control-max-age", b"3600"),
                    ]
                    logger.info("options_response_created_asgi", origin=allowed_origin, status=200)
                else:
                    logger.warning("options_request_no_origin_asgi", origin=origin, app_env=settings.app_env)
                
                # Send response directly
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": response_headers,
                })
                await send({
                    "type": "http.response.body",
                    "body": b"",
                })
                return
            
            # For non-OPTIONS requests, pass through
            await self.app(scope, receive, send)
        except Exception as e:
            logger.error("options_middleware_error", error=str(e), exc_info=True)
            # If there's an error, still try to pass through
            await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown."""
    logger.info("application_startup", app_name=settings.app_name, env=settings.app_env)

    # Check extraction dependencies at startup
    try:
        from app.infra.services.resume_service import ResumeService

        service = ResumeService(
            storage=None,  # type: ignore[arg-type]
            resume_repository=None,  # type: ignore[arg-type]
        )
        deps = service._check_extraction_dependencies()

        missing_deps = []
        if not deps.get("pypdfium2"):
            missing_deps.append("pypdfium2")
        if not deps.get("ocrmypdf"):
            missing_deps.append("ocrmypdf (requires: pip install ocrmypdf + tesseract + ghostscript)")

        if missing_deps:
            logger.warning(
                "extraction_dependencies_missing",
                missing=missing_deps,
                available=deps,
                message="Some extraction dependencies are missing. OCR fallbacks may not work.",
            )
        else:
            logger.info("extraction_dependencies_available", all_deps_available=True, deps=deps)
    except Exception as e:
        logger.warning("extraction_dependency_check_failed", error=str(e))

    yield
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.app_name,
    description="Agentic AI-powered automated job application platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware - handles CORS headers for all non-OPTIONS requests
# Added FIRST so it runs AFTER OptionsMiddleware (LIFO order)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# OPTIONS middleware - added LAST so it runs FIRST (outermost)
# Intercepts all OPTIONS preflight requests at ASGI level before route matching
app.add_middleware(OptionsMiddleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error"
            if not settings.debug
            else f"Internal server error: {str(exc)}"
        },
    )


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint with extraction dependencies."""
    from app.infra.services.resume_service import ResumeService

    # Check extraction dependencies
    # Create a minimal service instance just for dependency checking
    # (storage and repo not needed for dependency checks)
    service = ResumeService(
        storage=None,  # type: ignore[arg-type]
        resume_repository=None,  # type: ignore[arg-type]
    )
    deps = service._check_extraction_dependencies()

    return {
        "status": "healthy",
        "version": "0.1.0",
        "extraction": {
            "poppler": deps.get("poppler", False),
            "tesseract": deps.get("tesseract", False),
            "pdf2image": deps.get("pdf2image", False),
        },
    }
