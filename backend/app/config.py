"""Application configuration using pydantic-settings.

Standards: python_clean.mdc
- pydantic-settings BaseSettings only; no manual os.getenv
- SecretStr for sensitive values
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env file in current dir, backend dir, or project root
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
_env_file = (
    Path(".env") if Path(".env").exists()
    else _backend_dir / ".env" if (_backend_dir / ".env").exists()
    else _project_root / ".env" if (_project_root / ".env").exists()
    else ".env"
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_env_file),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "ApplyBots"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ApplyBots"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Together AI
    together_api_key: SecretStr = SecretStr("")
    together_api_base: str = "https://api.together.xyz/v1"

    # Stripe
    stripe_secret_key: SecretStr = SecretStr("")
    stripe_webhook_secret: SecretStr = SecretStr("")
    stripe_price_id_premium: str = ""
    stripe_price_id_elite: str = ""

    # S3/MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: SecretStr = SecretStr("")
    s3_secret_key: SecretStr = SecretStr("")
    s3_bucket: str = "applybots"
    s3_region: str = "us-east-1"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Plan Limits
    daily_apply_limit_free: int = 5
    daily_apply_limit_premium: int = 20
    daily_apply_limit_elite: int = 50

    # OAuth - Google
    google_client_id: SecretStr = SecretStr("")
    google_client_secret: SecretStr = SecretStr("")
    google_redirect_uri: str = "http://localhost:3000/api/auth/callback/google"

    # OAuth - GitHub
    github_client_id: SecretStr = SecretStr("")
    github_client_secret: SecretStr = SecretStr("")
    github_redirect_uri: str = "http://localhost:3000/api/auth/callback/github"

    # Email Notifications (SendGrid)
    sendgrid_api_key: SecretStr = SecretStr("")
    sendgrid_from_email: str = "noreply@applybots.com"

    # Job Aggregator APIs
    adzuna_app_id: str = ""
    adzuna_api_key: SecretStr = SecretStr("")
    jooble_api_key: SecretStr = SecretStr("")
    themuse_api_key: SecretStr = SecretStr("")

    # Company Intelligence APIs
    newsapi_key: SecretStr = SecretStr("")

    # Feature Flags
    feature_company_intel: bool = True
    feature_gamification: bool = True
    feature_wellness: bool = True
    feature_advanced_analytics: bool = True

    # Alert Settings
    alert_dream_job_default_threshold: int = 90


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
