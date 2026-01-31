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

from app.core.domain.application import ApplicationStatus
from app.core.domain.job import JobSource
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
    applications: Mapped[List["ApplicationModel"]] = relationship(back_populates="user")
    subscription: Mapped[Optional["SubscriptionModel"]] = relationship(back_populates="user", uselist=False)
    refresh_sessions: Mapped[List["RefreshSessionModel"]] = relationship(back_populates="user")
    agent_sessions: Mapped[List["AgentSessionModel"]] = relationship(back_populates="user")


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
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    match_explanation: Mapped[Optional[dict]] = mapped_column(JSON)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    generated_answers: Mapped[dict] = mapped_column(JSON, default=dict)
    qc_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    qc_feedback: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="applications")
    job: Mapped["JobModel"] = relationship(back_populates="applications")
    audit_logs: Mapped[List["AuditLogModel"]] = relationship(back_populates="application")


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
