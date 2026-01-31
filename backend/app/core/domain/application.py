"""Application domain model.

Standards: python_clean.mdc
- Enum for status
- Dataclass with no magic numbers (MatchWeights)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ApplicationStatus(Enum):
    """Application status enumeration."""

    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    FAILED = "failed"
    MANUAL_NEEDED = "manual_needed"
    REJECTED = "rejected"
    INTERVIEW = "interview"


@dataclass(frozen=True)
class MatchWeights:
    """Deterministic scoring weights - no magic numbers."""

    SKILLS: float = 0.40
    EXPERIENCE: float = 0.25
    LOCATION: float = 0.15
    SALARY: float = 0.10
    CULTURE: float = 0.10


@dataclass
class MatchExplanation:
    """Detailed match score breakdown."""

    skills_score: int
    skills_matched: list[str]
    skills_missing: list[str]
    experience_score: int
    experience_gap: str | None
    location_score: int
    location_match: bool
    salary_score: int
    salary_in_range: bool | None
    culture_score: int
    overall_recommendation: str


@dataclass
class Application:
    """Job application domain entity."""

    id: str
    user_id: str
    job_id: str
    resume_id: str
    status: ApplicationStatus = ApplicationStatus.PENDING_REVIEW
    match_score: int = 0
    match_explanation: MatchExplanation | None = None
    cover_letter: str | None = None
    generated_answers: dict[str, str] = field(default_factory=dict)
    qc_approved: bool = False
    qc_feedback: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: datetime | None = None
    error_message: str | None = None
