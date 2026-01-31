"""Profile domain model.

Standards: python_clean.mdc
- Dataclass for domain models
- Typed fields, no Any
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Preferences:
    """User job search preferences."""

    target_roles: list[str] = field(default_factory=list)
    target_locations: list[str] = field(default_factory=list)
    remote_only: bool = False
    salary_min: int | None = None
    salary_max: int | None = None
    negative_keywords: list[str] = field(default_factory=list)
    experience_years: int | None = None


@dataclass
class Profile:
    """User profile domain entity."""

    id: str
    user_id: str
    full_name: str | None = None
    headline: str | None = None
    location: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    preferences: Preferences = field(default_factory=Preferences)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
