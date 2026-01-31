"""Resume domain model.

Standards: python_clean.mdc
- Dataclass for domain models
- Typed fields for parsed data
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkExperience:
    """Parsed work experience entry."""

    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = field(default_factory=list)


@dataclass
class Education:
    """Parsed education entry."""

    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_date: str | None = None
    gpa: float | None = None


@dataclass
class ParsedResume:
    """Structured data extracted from resume."""

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = field(default_factory=list)
    work_experience: list[WorkExperience] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    total_years_experience: float | None = None


@dataclass
class Resume:
    """Resume domain entity."""

    id: str
    user_id: str
    filename: str
    s3_key: str
    raw_text: str | None = None
    parsed_data: ParsedResume | None = None
    embedding: list[float] | None = None
    is_primary: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
