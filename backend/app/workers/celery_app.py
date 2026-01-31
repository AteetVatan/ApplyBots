"""Celery application configuration.

Standards: python_clean.mdc
- Configuration from settings
- Windows compatibility (solo pool)
"""

import sys

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ApplyBots",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.job_ingestion",
        "app.workers.application_submitter",
    ],
)

# Windows compatibility: use solo pool to avoid multiprocessing issues
# On Linux/macOS, prefork pool is used by default (better performance)
worker_pool = "solo" if sys.platform == "win32" else "prefork"

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    task_soft_time_limit=540,  # 9 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_pool=worker_pool,  # solo on Windows, prefork on Unix
    broker_connection_retry_on_startup=True,  # Retry broker connection on startup (Celery 6.0+)
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "ingest-jobs-hourly": {
        "task": "app.workers.job_ingestion.ingest_jobs_scheduled",
        "schedule": 3600.0,  # Every hour
    },
    "reset-daily-usage": {
        "task": "app.workers.job_ingestion.reset_daily_usage",
        "schedule": 86400.0,  # Every 24 hours
    },
}
