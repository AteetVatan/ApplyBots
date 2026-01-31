"""Redis-based rate limiting middleware.

Standards: python_clean.mdc
- Async Redis operations
- Sliding window algorithm
- Decorator pattern
"""

from functools import wraps
from typing import Callable

import structlog
from fastapi import HTTPException, Request, status

logger = structlog.get_logger(__name__)


class RateLimitExceeded(HTTPException):
    """Rate limit exceeded exception."""

    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


class RateLimiter:
    """Redis-based rate limiter using sliding window algorithm."""

    def __init__(
        self,
        *,
        redis_url: str,
        requests_per_minute: int = 60,
    ) -> None:
        """Initialize rate limiter.

        Args:
            redis_url: Redis connection URL
            requests_per_minute: Maximum requests per minute
        """
        self._redis_url = redis_url
        self._limit = requests_per_minute
        self._window = 60  # 1 minute window
        self._redis = None

    async def _get_redis(self):
        """Get or create Redis connection."""
        if self._redis is None:
            import redis.asyncio as redis
            self._redis = redis.from_url(self._redis_url)
        return self._redis

    async def check(
        self,
        *,
        key: str,
        limit: int | None = None,
    ) -> tuple[bool, int, int]:
        """Check if request is within rate limit.

        Args:
            key: Rate limit key (e.g., user_id or IP)
            limit: Override default limit

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        import time

        redis = await self._get_redis()
        limit = limit or self._limit

        now = int(time.time())
        window_start = now - self._window
        rate_key = f"rate_limit:{key}"

        try:
            pipe = redis.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(rate_key, 0, window_start)

            # Count requests in current window
            pipe.zcard(rate_key)

            # Add current request
            pipe.zadd(rate_key, {str(now): now})

            # Set expiry on the key
            pipe.expire(rate_key, self._window * 2)

            results = await pipe.execute()
            current_count = results[1]

            remaining = max(0, limit - current_count - 1)
            reset_time = now + self._window

            allowed = current_count < limit

            if not allowed:
                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    current=current_count,
                    limit=limit,
                )

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error("rate_limit_check_error", key=key, error=str(e))
            # Fail open - allow request if Redis is down
            return True, limit, now + self._window

    async def is_allowed(self, *, key: str) -> bool:
        """Simple check if request is allowed.

        Args:
            key: Rate limit key

        Returns:
            True if request is allowed
        """
        allowed, _, _ = await self.check(key=key)
        return allowed

    async def get_remaining(self, *, key: str) -> int:
        """Get remaining requests for a key.

        Args:
            key: Rate limit key

        Returns:
            Number of remaining requests
        """
        _, remaining, _ = await self.check(key=key)
        return remaining


def rate_limit(
    requests_per_minute: int = 60,
    key_func: Callable[[Request], str] | None = None,
):
    """Rate limiting decorator for FastAPI endpoints.

    Args:
        requests_per_minute: Maximum requests per minute
        key_func: Function to extract rate limit key from request

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the Request object in args/kwargs
            request: Request | None = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")

            if request is None:
                # No request found, skip rate limiting
                return await func(*args, **kwargs)

            # Get rate limit key
            if key_func:
                key = key_func(request)
            else:
                # Default: use IP address
                key = request.client.host if request.client else "unknown"

            # Check with app's rate limiter
            rate_limiter = getattr(request.app.state, "rate_limiter", None)
            if rate_limiter:
                allowed, remaining, reset = await rate_limiter.check(
                    key=key,
                    limit=requests_per_minute,
                )

                # Add rate limit headers to response
                request.state.rate_limit_remaining = remaining
                request.state.rate_limit_reset = reset

                if not allowed:
                    raise RateLimitExceeded(retry_after=reset - int(__import__("time").time()))

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def get_user_key(request: Request) -> str:
    """Extract user ID from request for rate limiting.

    Args:
        request: FastAPI request

    Returns:
        User ID or IP address
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"

    # Fall back to IP
    return f"ip:{request.client.host if request.client else 'unknown'}"
