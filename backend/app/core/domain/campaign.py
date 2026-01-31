"""Campaign domain model.

Standards: python_clean.mdc
- Dataclass domain entities
- Enums for status
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    """Campaign status options."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RecommendationMode(str, Enum):
    """Job recommendation mode for campaigns."""

    KEYWORD = "keyword"  # First 3 days - keyword/filter matching
    LEARNED = "learned"  # After 3 days - ML-based from applied jobs


class CampaignJobStatus(str, Enum):
    """Campaign-job relationship status."""

    PENDING = "pending"
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"
    SKIPPED = "skipped"


@dataclass
class Campaign:
    """Role-cluster campaign for targeted job applications.

    Represents a copilot with its own resume, search criteria,
    and behavior settings for automated job applications.
    """

    id: str
    user_id: str
    name: str
    resume_id: str  # Resume used for this campaign

    # Search criteria
    target_roles: list[str] = field(default_factory=list)
    target_locations: list[str] = field(default_factory=list)
    target_countries: list[str] = field(default_factory=list)
    target_companies: list[str] = field(default_factory=list)
    remote_only: bool = False
    salary_min: int | None = None
    salary_max: int | None = None
    negative_keywords: list[str] = field(default_factory=list)

    # Behavior settings
    auto_apply: bool = False  # Auto-apply vs save for review
    daily_limit: int = 10  # Max applications per day
    min_match_score: int = 70  # Minimum match score to apply
    send_per_app_email: bool = False  # Send email per application
    cover_letter_template: str | None = None

    # Status
    status: CampaignStatus = CampaignStatus.ACTIVE

    # Statistics
    jobs_found: int = 0
    jobs_applied: int = 0
    interviews: int = 0
    offers: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    activated_at: datetime | None = None  # When campaign was first activated

    # Recommendation mode (switches from keyword to learned after 3 days)
    recommendation_mode: RecommendationMode = RecommendationMode.KEYWORD


@dataclass
class CampaignJob:
    """Job associated with a campaign.

    Tracks the relationship between a campaign and a job,
    including match scores and status.
    """

    campaign_id: str
    job_id: str
    match_score: int = 0
    adjusted_score: int = 0  # Score after feedback penalties
    status: CampaignJobStatus = CampaignJobStatus.PENDING
    rejection_reason: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    applied_at: datetime | None = None
    rejected_at: datetime | None = None
