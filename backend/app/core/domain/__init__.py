"""Domain models - dataclasses and Pydantic models for business entities."""

from app.core.domain.application import Application, ApplicationStatus, MatchWeights
from app.core.domain.career_kit import (
    CareerKitPhase,
    CareerKitSession,
    ConfidenceScore,
    CustomJD,
    DeltaAction,
    DeltaInstruction,
    GapMapItem,
    GapStatus,
    InterviewPrep,
    Question,
    Requirement,
    RequirementLevel,
    ResumeSource,
    TailoredCV,
)
from app.core.domain.job import Job, JobRequirements, JobSource
from app.core.domain.profile import Preferences, Profile
from app.core.domain.resume import ParsedResume, Resume
from app.core.domain.subscription import Plan, Subscription, SubscriptionStatus
from app.core.domain.user import User, UserRole

__all__ = [
    "Application",
    "ApplicationStatus",
    "CareerKitPhase",
    "CareerKitSession",
    "ConfidenceScore",
    "CustomJD",
    "DeltaAction",
    "DeltaInstruction",
    "GapMapItem",
    "GapStatus",
    "InterviewPrep",
    "Job",
    "JobRequirements",
    "JobSource",
    "MatchWeights",
    "ParsedResume",
    "Plan",
    "Preferences",
    "Profile",
    "Question",
    "Requirement",
    "RequirementLevel",
    "Resume",
    "ResumeSource",
    "Subscription",
    "SubscriptionStatus",
    "TailoredCV",
    "User",
    "UserRole",
]
