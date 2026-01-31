"""Campaign repository implementation.

Standards: python_clean.mdc
- Async SQLAlchemy operations
- Domain model mapping
"""

from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.domain.campaign import (
    Campaign,
    CampaignJob,
    CampaignJobStatus,
    CampaignStatus,
)
from app.infra.db.models import CampaignJobModel, CampaignModel


class SQLCampaignRepository:
    """SQLAlchemy implementation of CampaignRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, campaign_id: str) -> Campaign | None:
        """Get campaign by ID."""
        stmt = (
            select(CampaignModel)
            .where(CampaignModel.id == campaign_id)
            .options(selectinload(CampaignModel.campaign_jobs))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        status: CampaignStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Campaign]:
        """Get campaigns for a user, optionally filtered by status."""
        conditions = [CampaignModel.user_id == user_id]
        if status:
            conditions.append(CampaignModel.status == status)

        stmt = (
            select(CampaignModel)
            .where(and_(*conditions))
            .order_by(CampaignModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_active_campaigns(self) -> list[Campaign]:
        """Get all active campaigns for scheduled processing."""
        stmt = (
            select(CampaignModel)
            .where(CampaignModel.status == CampaignStatus.ACTIVE)
            .order_by(CampaignModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, campaign: Campaign) -> Campaign:
        """Create a new campaign."""
        model = CampaignModel(
            id=campaign.id,
            user_id=campaign.user_id,
            name=campaign.name,
            resume_id=campaign.resume_id,
            target_roles=campaign.target_roles,
            target_locations=campaign.target_locations,
            target_countries=campaign.target_countries,
            target_companies=campaign.target_companies,
            remote_only=campaign.remote_only,
            salary_min=campaign.salary_min,
            salary_max=campaign.salary_max,
            negative_keywords=campaign.negative_keywords,
            auto_apply=campaign.auto_apply,
            daily_limit=campaign.daily_limit,
            min_match_score=campaign.min_match_score,
            send_per_app_email=campaign.send_per_app_email,
            cover_letter_template=campaign.cover_letter_template,
            status=campaign.status,
            jobs_found=campaign.jobs_found,
            jobs_applied=campaign.jobs_applied,
            interviews=campaign.interviews,
            offers=campaign.offers,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            completed_at=campaign.completed_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, campaign: Campaign) -> Campaign:
        """Update an existing campaign."""
        model = await self._session.get(CampaignModel, campaign.id)
        if not model:
            raise ValueError(f"Campaign {campaign.id} not found")

        model.name = campaign.name
        model.resume_id = campaign.resume_id
        model.target_roles = campaign.target_roles
        model.target_locations = campaign.target_locations
        model.target_countries = campaign.target_countries
        model.target_companies = campaign.target_companies
        model.remote_only = campaign.remote_only
        model.salary_min = campaign.salary_min
        model.salary_max = campaign.salary_max
        model.negative_keywords = campaign.negative_keywords
        model.auto_apply = campaign.auto_apply
        model.daily_limit = campaign.daily_limit
        model.min_match_score = campaign.min_match_score
        model.send_per_app_email = campaign.send_per_app_email
        model.cover_letter_template = campaign.cover_letter_template
        model.status = campaign.status
        model.jobs_found = campaign.jobs_found
        model.jobs_applied = campaign.jobs_applied
        model.interviews = campaign.interviews
        model.offers = campaign.offers
        model.updated_at = datetime.utcnow()
        model.completed_at = campaign.completed_at

        await self._session.flush()
        return self._to_domain(model)

    async def delete(self, campaign_id: str) -> bool:
        """Delete a campaign by ID."""
        model = await self._session.get(CampaignModel, campaign_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def update_status(
        self,
        campaign_id: str,
        *,
        status: CampaignStatus,
    ) -> Campaign | None:
        """Update campaign status."""
        model = await self._session.get(CampaignModel, campaign_id)
        if not model:
            return None

        model.status = status
        model.updated_at = datetime.utcnow()

        if status == CampaignStatus.COMPLETED:
            model.completed_at = datetime.utcnow()

        await self._session.flush()
        return self._to_domain(model)

    async def increment_stats(
        self,
        campaign_id: str,
        *,
        jobs_found: int = 0,
        jobs_applied: int = 0,
        interviews: int = 0,
        offers: int = 0,
    ) -> None:
        """Increment campaign statistics."""
        model = await self._session.get(CampaignModel, campaign_id)
        if model:
            model.jobs_found += jobs_found
            model.jobs_applied += jobs_applied
            model.interviews += interviews
            model.offers += offers
            model.updated_at = datetime.utcnow()
            await self._session.flush()

    # Campaign Job operations
    async def add_job(self, campaign_job: CampaignJob) -> CampaignJob:
        """Add a job to a campaign."""
        model = CampaignJobModel(
            campaign_id=campaign_job.campaign_id,
            job_id=campaign_job.job_id,
            match_score=campaign_job.match_score,
            adjusted_score=campaign_job.adjusted_score,
            status=campaign_job.status.value,
            rejection_reason=campaign_job.rejection_reason,
            created_at=campaign_job.created_at,
            applied_at=campaign_job.applied_at,
            rejected_at=campaign_job.rejected_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._campaign_job_to_domain(model)

    async def get_campaign_job(
        self,
        campaign_id: str,
        job_id: str,
    ) -> CampaignJob | None:
        """Get a specific campaign-job relationship."""
        model = await self._session.get(
            CampaignJobModel,
            (campaign_id, job_id),
        )
        return self._campaign_job_to_domain(model) if model else None

    async def get_campaign_jobs(
        self,
        campaign_id: str,
        *,
        status: CampaignJobStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CampaignJob]:
        """Get jobs for a campaign, optionally filtered by status."""
        conditions = [CampaignJobModel.campaign_id == campaign_id]
        if status:
            conditions.append(CampaignJobModel.status == status.value)

        stmt = (
            select(CampaignJobModel)
            .where(and_(*conditions))
            .order_by(CampaignJobModel.adjusted_score.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._campaign_job_to_domain(m) for m in models]

    async def update_job_status(
        self,
        campaign_id: str,
        job_id: str,
        *,
        status: CampaignJobStatus,
        rejection_reason: str | None = None,
    ) -> CampaignJob | None:
        """Update campaign-job status (e.g., reject)."""
        model = await self._session.get(
            CampaignJobModel,
            (campaign_id, job_id),
        )
        if not model:
            return None

        model.status = status.value

        if status == CampaignJobStatus.REJECTED:
            model.rejected_at = datetime.utcnow()
            model.rejection_reason = rejection_reason
        elif status == CampaignJobStatus.APPLIED:
            model.applied_at = datetime.utcnow()

        await self._session.flush()
        return self._campaign_job_to_domain(model)

    async def count_applied_today(self, campaign_id: str) -> int:
        """Count jobs applied today for a campaign."""
        today_start = datetime.combine(
            datetime.utcnow().date(),
            datetime.min.time(),
        )
        stmt = (
            select(func.count())
            .select_from(CampaignJobModel)
            .where(
                and_(
                    CampaignJobModel.campaign_id == campaign_id,
                    CampaignJobModel.status == CampaignJobStatus.APPLIED.value,
                    CampaignJobModel.applied_at >= today_start,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def job_exists_in_campaign(
        self,
        campaign_id: str,
        job_id: str,
    ) -> bool:
        """Check if a job is already in a campaign."""
        model = await self._session.get(
            CampaignJobModel,
            (campaign_id, job_id),
        )
        return model is not None

    def _to_domain(self, model: CampaignModel) -> Campaign:
        """Convert ORM model to domain entity."""
        return Campaign(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            resume_id=model.resume_id,
            target_roles=model.target_roles or [],
            target_locations=model.target_locations or [],
            target_countries=model.target_countries or [],
            target_companies=model.target_companies or [],
            remote_only=model.remote_only,
            salary_min=model.salary_min,
            salary_max=model.salary_max,
            negative_keywords=model.negative_keywords or [],
            auto_apply=model.auto_apply,
            daily_limit=model.daily_limit,
            min_match_score=model.min_match_score,
            send_per_app_email=model.send_per_app_email,
            cover_letter_template=model.cover_letter_template,
            status=model.status,
            jobs_found=model.jobs_found,
            jobs_applied=model.jobs_applied,
            interviews=model.interviews,
            offers=model.offers,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
        )

    def _campaign_job_to_domain(self, model: CampaignJobModel) -> CampaignJob:
        """Convert campaign job ORM model to domain entity."""
        return CampaignJob(
            campaign_id=model.campaign_id,
            job_id=model.job_id,
            match_score=model.match_score,
            adjusted_score=model.adjusted_score,
            status=CampaignJobStatus(model.status),
            rejection_reason=model.rejection_reason,
            created_at=model.created_at,
            applied_at=model.applied_at,
            rejected_at=model.rejected_at,
        )
