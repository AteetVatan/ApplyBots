"""Job domain model.

Standards: python_clean.mdc
- Enum for job source
- Dataclass for domain models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class JobSource(Enum):
    """Job listing source."""

    REMOTIVE = "remotive"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    MANUAL = "manual"


@dataclass
class JobRequirements:
    """Structured job requirements."""

    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    experience_years_min: int | None = None
    experience_years_max: int | None = None
    education_level: str | None = None
    certifications: list[str] = field(default_factory=list)


@dataclass
class Job:
    """Job listing domain entity."""

    id: str
    external_id: str
    title: str
    company: str
    location: str | None = None
    description: str = ""
    url: str = ""
    source: JobSource = JobSource.MANUAL
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "USD"
    remote: bool = False
    requirements: JobRequirements = field(default_factory=JobRequirements)
    embedding: list[float] | None = None
    posted_at: datetime | None = None
    ingested_at: datetime = field(default_factory=datetime.utcnow)
