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
    WELLFOUND = "wellfound"
    ADZUNA = "adzuna"
    JOOBLE = "jooble"
    THEMUSE = "themuse"
    MANUAL = "manual"
    OTHER = "other"


@dataclass
class JobRequirements:
    """Structured job requirements."""

    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    experience_years_min: int | None = None
    experience_years_max: int | None = None
    education_level: str | None = None
    certifications: list[str] = field(default_factory=list)


class RemoteType(Enum):
    """Remote work type classification."""

    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"
    REMOTE_US = "remote_us"
    REMOTE_GLOBAL = "remote_global"


@dataclass
class RemoteIntelligence:
    """Detailed remote work analysis."""

    remote_type: RemoteType
    timezone_requirements: list[str] | None = None
    office_locations: list[str] = field(default_factory=list)
    remote_score: int = 0  # 0-100 based on job text analysis
    travel_required: bool | None = None


@dataclass
class ApplicationTiming:
    """Optimal application timing intelligence."""

    optimal_window_start: datetime
    optimal_window_end: datetime
    urgency_score: int  # 0-100
    days_since_posted: int
    estimated_applicants: int
    recommendation: str  # "Apply now", "Good time", "May be late"


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
    remote_type: RemoteType = RemoteType.ONSITE
    remote_score: int = 0
    timezone_requirements: list[str] | None = None
    requirements: JobRequirements = field(default_factory=JobRequirements)
    embedding: list[float] | None = None
    posted_at: datetime | None = None
    ingested_at: datetime = field(default_factory=datetime.utcnow)
