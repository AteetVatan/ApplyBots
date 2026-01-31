"""Repository port interfaces.

Standards: python_clean.mdc
- Protocol for interfaces (DIP)
- Async methods
- kw-only args after *
"""

from typing import Protocol

from app.core.domain.application import Application, ApplicationStatus
from app.core.domain.job import Job
from app.core.domain.profile import Profile
from app.core.domain.resume import Resume
from app.core.domain.subscription import Subscription
from app.core.domain.user import User


class UserRepository(Protocol):
    """User repository interface."""

    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        ...

    async def create(self, user: User) -> User:
        """Create a new user."""
        ...

    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    async def delete(self, user_id: str) -> None:
        """Delete a user."""
        ...


class ProfileRepository(Protocol):
    """Profile repository interface."""

    async def get_by_user_id(self, user_id: str) -> Profile | None:
        """Get profile by user ID."""
        ...

    async def create(self, profile: Profile) -> Profile:
        """Create a new profile."""
        ...

    async def update(self, profile: Profile) -> Profile:
        """Update an existing profile."""
        ...


class ResumeRepository(Protocol):
    """Resume repository interface."""

    async def get_by_id(self, resume_id: str) -> Resume | None:
        """Get resume by ID."""
        ...

    async def get_by_user_id(self, user_id: str) -> list[Resume]:
        """Get all resumes for a user."""
        ...

    async def get_primary(self, *, user_id: str) -> Resume | None:
        """Get primary resume for a user."""
        ...

    async def create(self, resume: Resume) -> Resume:
        """Create a new resume."""
        ...

    async def update(self, resume: Resume) -> Resume:
        """Update an existing resume."""
        ...

    async def delete(self, resume_id: str) -> None:
        """Delete a resume."""
        ...


class JobRepository(Protocol):
    """Job repository interface."""

    async def get_by_id(self, job_id: str) -> Job | None:
        """Get job by ID."""
        ...

    async def get_by_external_id(self, external_id: str) -> Job | None:
        """Get job by external ID (for deduplication)."""
        ...

    async def find_matching(
        self,
        *,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Job]:
        """Find jobs matching user preferences."""
        ...

    async def create(self, job: Job) -> Job:
        """Create a new job."""
        ...

    async def upsert(self, job: Job) -> Job:
        """Create or update a job."""
        ...

    async def count(self) -> int:
        """Count total jobs."""
        ...


class ApplicationRepository(Protocol):
    """Application repository interface."""

    async def get_by_id(self, application_id: str) -> Application | None:
        """Get application by ID."""
        ...

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        status: ApplicationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Application]:
        """Get applications for a user, optionally filtered by status."""
        ...

    async def create(self, application: Application) -> Application:
        """Create a new application."""
        ...

    async def update(self, application: Application) -> Application:
        """Update an existing application."""
        ...

    async def count_today(self, *, user_id: str) -> int:
        """Count applications submitted today by user."""
        ...


class SubscriptionRepository(Protocol):
    """Subscription repository interface."""

    async def get_by_user_id(self, user_id: str) -> Subscription | None:
        """Get subscription by user ID."""
        ...

    async def get_by_stripe_customer_id(self, customer_id: str) -> Subscription | None:
        """Get subscription by Stripe customer ID."""
        ...

    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription."""
        ...

    async def update(self, subscription: Subscription) -> Subscription:
        """Update an existing subscription."""
        ...

    async def reset_daily_usage(self) -> int:
        """Reset daily usage counters, return count of updated records."""
        ...
