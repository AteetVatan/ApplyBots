"""Prometheus metrics middleware.

Standards: python_clean.mdc
- Counter and histogram metrics
- Request/response instrumentation
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

import structlog

logger = structlog.get_logger(__name__)

# Try to import prometheus_client, fail gracefully if not installed
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

    PROMETHEUS_AVAILABLE = True

    # Request metrics
    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total number of HTTP requests",
        ["method", "endpoint", "status"],
    )

    REQUEST_LATENCY = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )

    # Application-specific metrics
    APPLICATIONS_SUBMITTED = Counter(
        "applications_submitted_total",
        "Total number of applications submitted",
        ["status"],
    )

    LLM_TOKENS_USED = Counter(
        "llm_tokens_total",
        "Total LLM tokens consumed",
        ["model", "type"],  # type: prompt, completion
    )

    JOBS_INGESTED = Counter(
        "jobs_ingested_total",
        "Total number of jobs ingested",
        ["source"],
    )

    RESUME_UPLOADS = Counter(
        "resume_uploads_total",
        "Total number of resume uploads",
        ["status"],
    )

    ACTIVE_USERS = Counter(
        "active_users_total",
        "Total unique active users",
    )

except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client_not_installed")


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request and collect metrics."""
        if not PROMETHEUS_AVAILABLE:
            return await call_next(request)

        # Get endpoint path template (for consistent labels)
        path = self._get_path_template(request)
        method = request.method

        # Start timing
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        status = str(response.status_code)

        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status=status,
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=path,
        ).observe(duration)

        return response

    def _get_path_template(self, request: Request) -> str:
        """Get path template for consistent metric labels.

        Replaces path parameters with placeholders.
        """
        # Get the route's path template if available
        if hasattr(request, "scope") and "path" in request.scope:
            path = request.scope["path"]

            # Replace common ID patterns with placeholders
            import re
            # UUID pattern
            path = re.sub(
                r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                "/{id}",
                path,
            )
            # Numeric ID pattern
            path = re.sub(r"/\d+", "/{id}", path)

            return path

        return request.url.path


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response.

    Returns:
        Response with Prometheus metrics
    """
    if not PROMETHEUS_AVAILABLE:
        return Response(
            content="Prometheus client not installed",
            status_code=503,
        )

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# Helper functions for recording application metrics

def record_application_submitted(*, status: str) -> None:
    """Record an application submission."""
    if PROMETHEUS_AVAILABLE:
        APPLICATIONS_SUBMITTED.labels(status=status).inc()


def record_llm_tokens(*, model: str, prompt_tokens: int, completion_tokens: int) -> None:
    """Record LLM token usage."""
    if PROMETHEUS_AVAILABLE:
        LLM_TOKENS_USED.labels(model=model, type="prompt").inc(prompt_tokens)
        LLM_TOKENS_USED.labels(model=model, type="completion").inc(completion_tokens)


def record_job_ingested(*, source: str) -> None:
    """Record a job ingestion."""
    if PROMETHEUS_AVAILABLE:
        JOBS_INGESTED.labels(source=source).inc()


def record_resume_upload(*, status: str) -> None:
    """Record a resume upload."""
    if PROMETHEUS_AVAILABLE:
        RESUME_UPLOADS.labels(status=status).inc()
