"""Debug utilities for development and troubleshooting.

Standards: python_clean.mdc
- Structured logging
- Type hints for public APIs
- Small, focused functions
- No magic values
"""

import asyncio
import json
import sys
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps
from typing import Any, AsyncGenerator, Awaitable, Callable, TypeVar, cast, overload

import structlog
from pydantic import SecretStr

from app.config import Settings, get_settings

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def print_settings(settings: Settings | None = None, *, hide_secrets: bool = True) -> None:
    """Print application settings in a readable format.
    
    Args:
        settings: Settings instance to print. If None, uses get_settings().
        hide_secrets: If True, masks SecretStr values.
    """
    if settings is None:
        settings = get_settings()
    
    print("\n" + "=" * 80)
    print("APPLICATION SETTINGS")
    print("=" * 80)
    
    for key, value in settings.model_dump().items():
        if isinstance(value, SecretStr):
            if hide_secrets:
                value_str = "***" if value.get_secret_value() else "<empty>"
            else:
                value_str = value.get_secret_value()
        else:
            value_str = str(value)
        
        print(f"  {key:30} = {value_str}")
    
    print("=" * 80 + "\n")


def print_environment() -> None:
    """Print current environment variables (excluding secrets)."""
    import os
    
    print("\n" + "=" * 80)
    print("ENVIRONMENT VARIABLES")
    print("=" * 80)
    
    # Filter out common secret patterns
    secret_patterns = ["key", "secret", "password", "token", "auth"]
    
    for key, value in sorted(os.environ.items()):
        key_lower = key.lower()
        if any(pattern in key_lower for pattern in secret_patterns):
            value = "***"
        print(f"  {key:30} = {value}")
    
    print("=" * 80 + "\n")


async def test_database_connection() -> dict[str, Any]:
    """Test database connection and return status.
    
    Returns:
        Dictionary with connection status and details.
    """
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        AsyncSession,
        async_sessionmaker,
    )
    from sqlalchemy import text
    
    settings = get_settings()
    result: dict[str, Any] = {
        "status": "unknown",
        "url": settings.database_url,
        "error": None,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    try:
        engine = create_async_engine(settings.database_url, echo=False)
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()
        
        result["status"] = "connected"
        await engine.dispose()
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
    
    return result


async def test_redis_connection() -> dict[str, Any]:
    """Test Redis connection and return status.
    
    Returns:
        Dictionary with connection status and details.
    """
    try:
        import redis.asyncio as redis
        
        settings = get_settings()
        result: dict[str, Any] = {
            "status": "unknown",
            "url": settings.redis_url,
            "error": None,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        client = redis.from_url(settings.redis_url)
        await client.ping()
        await client.aclose()
        
        result["status"] = "connected"
        
    except Exception as e:
        result = {
            "status": "failed",
            "url": get_settings().redis_url,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    return result


@overload
def log_function_call(
    log_args: bool = True,
    log_result: bool = True,
    log_duration: bool = True,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Overload for async functions."""
    ...


@overload
def log_function_call(
    log_args: bool = True,
    log_result: bool = True,
    log_duration: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Overload for sync functions."""
    ...


def log_function_call(
    log_args: bool = True,
    log_result: bool = True,
    log_duration: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to log function calls with arguments, results, and duration.
    
    Args:
        log_args: Whether to log function arguments.
        log_result: Whether to log function return value.
        log_duration: Whether to log execution duration.
    
    Returns:
        Decorator function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            func_logger = structlog.get_logger(func.__module__).bind(
                function=func.__name__
            )
            
            start_time = datetime.utcnow()
            
            if log_args:
                func_logger.debug(
                    "function_call_start",
                    args=args,
                    kwargs=kwargs,
                )
            
            try:
                # Cast to async function since we only use this wrapper for coroutine functions
                async_func = cast(Callable[..., Awaitable[Any]], func)
                result = await async_func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                log_data: dict[str, Any] = {"status": "success"}
                if log_duration:
                    log_data["duration_seconds"] = duration
                if log_result:
                    log_data["result"] = str(result)[:200]  # Truncate long results
                
                func_logger.debug("function_call_end", **log_data)
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                func_logger.error(
                    "function_call_error",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_seconds=duration,
                    traceback=traceback.format_exc(),
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            func_logger = structlog.get_logger(func.__module__).bind(
                function=func.__name__
            )
            
            start_time = datetime.utcnow()
            
            if log_args:
                func_logger.debug(
                    "function_call_start",
                    args=args,
                    kwargs=kwargs,
                )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                log_data: dict[str, Any] = {"status": "success"}
                if log_duration:
                    log_data["duration_seconds"] = duration
                if log_result:
                    log_data["result"] = str(result)[:200]  # Truncate long results
                
                func_logger.debug("function_call_end", **log_data)
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                func_logger.error(
                    "function_call_error",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_seconds=duration,
                    traceback=traceback.format_exc(),
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


@asynccontextmanager
async def profile_async(
    operation_name: str,
    *,
    log_result: bool = True,
) -> AsyncGenerator[None, None]:
    """Context manager to profile async operations.
    
    Args:
        operation_name: Name of the operation being profiled.
        log_result: Whether to log the profiling result.
    
    Yields:
        None
    """
    start_time = datetime.utcnow()
    profiler_logger = structlog.get_logger().bind(operation=operation_name)
    
    try:
        profiler_logger.debug("profile_start")
        yield
    finally:
        duration = (datetime.utcnow() - start_time).total_seconds()
        if log_result:
            profiler_logger.info(
                "profile_end",
                duration_seconds=duration,
            )


def print_exception_details(exc: Exception, *, include_traceback: bool = True) -> None:
    """Print detailed exception information.
    
    Args:
        exc: Exception to print details for.
        include_traceback: Whether to include full traceback.
    """
    print("\n" + "=" * 80)
    print("EXCEPTION DETAILS")
    print("=" * 80)
    print(f"Type:    {type(exc).__name__}")
    print(f"Message: {str(exc)}")
    
    if include_traceback:
        print("\nTraceback:")
        print(traceback.format_exc())
    
    print("=" * 80 + "\n")


async def check_all_services() -> dict[str, Any]:
    """Check connectivity to all external services.
    
    Returns:
        Dictionary with status of all services.
    """
    results: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }
    
    # Database
    results["services"]["database"] = await test_database_connection()
    
    # Redis
    results["services"]["redis"] = await test_redis_connection()
    
    return results


def main() -> None:
    """Main entry point to start the development server."""
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        reload=True,
        host="0.0.0.0",
        port=8080,
    )


if __name__ == "__main__":
    main()
