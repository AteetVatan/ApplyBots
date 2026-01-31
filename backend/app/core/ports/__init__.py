"""Port interfaces - Protocol classes for dependency inversion."""

from app.core.ports.ats import ATSAdapter
from app.core.ports.llm import LLMClient
from app.core.ports.repositories import (
    ApplicationRepository,
    JobRepository,
    ProfileRepository,
    ResumeRepository,
    SubscriptionRepository,
    UserRepository,
)
from app.core.ports.storage import FileStorage
from app.core.ports.vector_store import VectorStore

__all__ = [
    "ApplicationRepository",
    "ATSAdapter",
    "FileStorage",
    "JobRepository",
    "LLMClient",
    "ProfileRepository",
    "ResumeRepository",
    "SubscriptionRepository",
    "UserRepository",
    "VectorStore",
]
