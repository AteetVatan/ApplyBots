"""SQLAlchemy ORM models.

Standards: python_clean.mdc
- Mapped types for type hints
- Relationship definitions
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.domain.alert import AlertType
from app.core.domain.application import ApplicationStage, ApplicationStatus
from app.core.domain.campaign import CampaignStatus, RecommendationMode
from app.core.domain.job import JobSource, RemoteType
from app.core.domain.subscription import Plan, SubscriptionStatus
from app.core.domain.user import UserRole
from app.infra.db.session import Base


def generate_cuid() -> str:
    """Generate a CUID-like ID."""
    import uuid
    return str(uuid.uuid4())


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    profile: Mapped[Optional["ProfileModel"]] = relationship(back_populates="user", uselist=False)
    resumes: Mapped[List["ResumeModel"]] = relationship(back_populates="user")
    resume_drafts: Mapped[List["ResumeDraftModel"]] = relationship(back_populates="user")
    applications: Mapped[List["ApplicationModel"]] = relationship(back_populates="user")
    campaigns: Mapped[List["CampaignModel"]] = relationship(back_populates="user")
    subscription: Mapped[Optional["SubscriptionModel"]] = relationship(back_populates="user", uselist=False)
    refresh_sessions: Mapped[List["RefreshSessionModel"]] = relationship(back_populates="user")
    agent_sessions: Mapped[List["AgentSessionModel"]] = relationship(back_populates="user")
    alerts: Mapped[List["AlertModel"]] = relationship(back_populates="user")
    alert_preferences: Mapped[Optional["AlertPreferenceModel"]] = relationship(
        back_populates="user", uselist=False
    )
    user_streak: Mapped[Optional["UserStreakModel"]] = relationship(
        back_populates="user", uselist=False
    )
    achievements: Mapped[List["UserAchievementModel"]] = relationship(back_populates="user")


class ProfileModel(Base):
    """Profile database model."""

    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    headline: Mapped[Optional[str]] = mapped_column(String(500))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="profile")


class ResumeModel(Base):
    """Resume database model."""

    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    parsed_data: Mapped[Optional[dict]] = mapped_column(JSON)
    embedding: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="resumes")


class JobModel(Base):
    """Job database model."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(1000), default="")
    source: Mapped[JobSource] = mapped_column(Enum(JobSource), default=JobSource.MANUAL)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    remote_type: Mapped[RemoteType] = mapped_column(
        Enum(RemoteType), default=RemoteType.ONSITE
    )
    remote_score: Mapped[int] = mapped_column(Integer, default=0)
    timezone_requirements: Mapped[list] = mapped_column(JSON, default=list)
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    embedding: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    applications: Mapped[List["ApplicationModel"]] = relationship(back_populates="job")


class ApplicationModel(Base):
    """Application database model."""

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"))
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING_REVIEW
    )
    stage: Mapped[ApplicationStage] = mapped_column(
        Enum(ApplicationStage), default=ApplicationStage.SAVED
    )
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    match_explanation: Mapped[Optional[dict]] = mapped_column(JSON)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    generated_answers: Mapped[dict] = mapped_column(JSON, default=dict)
    qc_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    qc_feedback: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    stage_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timing intelligence columns
    applied_day_of_week: Mapped[Optional[int]] = mapped_column(Integer)
    applied_hour: Mapped[Optional[int]] = mapped_column(Integer)
    days_after_posting: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="applications")
    job: Mapped["JobModel"] = relationship(back_populates="applications")
    audit_logs: Mapped[List["AuditLogModel"]] = relationship(back_populates="application")
    notes: Mapped[List["ApplicationNoteModel"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class SubscriptionModel(Base):
    """Subscription database model."""

    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.FREE)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255))
    daily_limit: Mapped[int] = mapped_column(Integer, default=5)
    used_today: Mapped[int] = mapped_column(Integer, default=0)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="subscription")


class RefreshSessionModel(Base):
    """Refresh token session model."""

    __tablename__ = "refresh_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="refresh_sessions")


class AgentSessionModel(Base):
    """Agent conversation session model."""

    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    session_type: Mapped[Optional[str]] = mapped_column(String(50))
    messages: Mapped[list] = mapped_column(JSON, default=list)
    agents_used: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="agent_sessions")


class AuditLogModel(Base):
    """Audit log for automation actions."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    action_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    screenshot_s3_key: Mapped[Optional[str]] = mapped_column(String(500))
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    application: Mapped["ApplicationModel"] = relationship(back_populates="audit_logs")


class ResumeDraftModel(Base):
    """Resume draft database model for the builder with autosave."""

    __tablename__ = "resume_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    template_id: Mapped[str] = mapped_column(String(50), default="professional-modern")
    ats_score: Mapped[Optional[int]] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="resume_drafts")


class ApplicationNoteModel(Base):
    """Application note database model."""

    __tablename__ = "application_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    application: Mapped["ApplicationModel"] = relationship(back_populates="notes")


class CampaignModel(Base):
    """Campaign (copilot) database model.

    Each campaign represents a targeted job search with its own
    resume, criteria, and settings.
    """

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))

    # Search criteria
    target_roles: Mapped[list] = mapped_column(JSON, default=list)
    target_locations: Mapped[list] = mapped_column(JSON, default=list)
    target_countries: Mapped[list] = mapped_column(JSON, default=list)
    target_companies: Mapped[list] = mapped_column(JSON, default=list)
    remote_only: Mapped[bool] = mapped_column(Boolean, default=False)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    negative_keywords: Mapped[list] = mapped_column(JSON, default=list)

    # Behavior settings
    auto_apply: Mapped[bool] = mapped_column(Boolean, default=False)
    daily_limit: Mapped[int] = mapped_column(Integer, default=10)
    min_match_score: Mapped[int] = mapped_column(Integer, default=70)
    send_per_app_email: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_letter_template: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), default=CampaignStatus.ACTIVE
    )

    # Statistics
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    jobs_applied: Mapped[int] = mapped_column(Integer, default=0)
    interviews: Mapped[int] = mapped_column(Integer, default=0)
    offers: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Recommendation mode (keyword vs learned)
    recommendation_mode: Mapped[RecommendationMode] = mapped_column(
        Enum(RecommendationMode), default=RecommendationMode.KEYWORD
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="campaigns")
    resume: Mapped["ResumeModel"] = relationship()
    campaign_jobs: Mapped[List["CampaignJobModel"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignJobModel(Base):
    """Campaign-job association with campaign-specific status.

    Links campaigns to jobs and tracks per-campaign status
    (pending, applied, rejected, saved).
    """

    __tablename__ = "campaign_jobs"

    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    adjusted_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship(back_populates="campaign_jobs")
    job: Mapped["JobModel"] = relationship()


class AnswerEditModel(Base):
    """Answer edit history for copilot learning.

    Stores user edits to AI-generated screening question answers
    to enable few-shot learning for future answer generation.
    """

    __tablename__ = "answer_edits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    question_normalized: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    question_original: Mapped[str] = mapped_column(Text, nullable=False)
    original_answer: Mapped[str] = mapped_column(Text, nullable=False)
    edited_answer: Mapped[str] = mapped_column(Text, nullable=False)
    job_title: Mapped[Optional[str]] = mapped_column(String(500))
    job_company: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship()


# =============================================================================
# Alert System Models
# =============================================================================


class AlertModel(Base):
    """Alert notification database model."""

    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="alerts")


class AlertPreferenceModel(Base):
    """User preferences for alerts."""

    __tablename__ = "alert_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    dream_job_threshold: Mapped[int] = mapped_column(Integer, default=90)
    interview_reminder_hours: Mapped[int] = mapped_column(Integer, default=24)
    daily_digest: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled_types: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="alert_preferences")


# =============================================================================
# Gamification Models
# =============================================================================


class UserStreakModel(Base):
    """User activity streak tracking."""

    __tablename__ = "user_streaks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="user_streak")


class UserAchievementModel(Base):
    """User achievements/badges earned."""

    __tablename__ = "user_achievements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_cuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    achievement_id: Mapped[str] = mapped_column(String(50), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="achievements")