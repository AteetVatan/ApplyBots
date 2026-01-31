"""Repository implementations."""

from app.infra.db.repositories.application import SQLApplicationRepository
from app.infra.db.repositories.audit import SQLAuditRepository
from app.infra.db.repositories.campaign import SQLCampaignRepository
from app.infra.db.repositories.job import SQLJobRepository
from app.infra.db.repositories.profile import SQLProfileRepository
from app.infra.db.repositories.resume import SQLResumeRepository
from app.infra.db.repositories.resume_draft import SQLResumeDraftRepository
from app.infra.db.repositories.subscription import SQLSubscriptionRepository
from app.infra.db.repositories.user import SQLUserRepository

__all__ = [
    "SQLApplicationRepository",
    "SQLAuditRepository",
    "SQLCampaignRepository",
    "SQLJobRepository",
    "SQLProfileRepository",
    "SQLResumeRepository",
    "SQLResumeDraftRepository",
    "SQLSubscriptionRepository",
    "SQLUserRepository",
]
