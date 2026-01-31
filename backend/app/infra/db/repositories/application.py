"""Application repository implementation."""

from datetime import date, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.application import Application, ApplicationStatus
from app.infra.db.models import ApplicationModel


class SQLApplicationRepository:
    """SQLAlchemy implementation of ApplicationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, application_id: str) -> Application | None:
        """Get application by ID."""
        result = await self._session.get(ApplicationModel, application_id)
        return self._to_domain(result) if result else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        status: ApplicationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Application]:
        """Get applications for a user, optionally filtered by status."""
        conditions = [ApplicationModel.user_id == user_id]
        if status:
            conditions.append(ApplicationModel.status == status)

        stmt = (
            select(ApplicationModel)
            .where(and_(*conditions))
            .order_by(ApplicationModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, application: Application) -> Application:
        """Create a new application."""
        model = ApplicationModel(
            id=application.id,
            user_id=application.user_id,
            job_id=application.job_id,
            resume_id=application.resume_id,
            status=application.status,
            match_score=application.match_score,
            match_explanation=None,  # Would serialize MatchExplanation
            cover_letter=application.cover_letter,
            generated_answers=application.generated_answers,
            qc_approved=application.qc_approved,
            qc_feedback=application.qc_feedback,
            created_at=application.created_at,
            submitted_at=application.submitted_at,
            error_message=application.error_message,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, application: Application) -> Application:
        """Update an existing application."""
        model = await self._session.get(ApplicationModel, application.id)
        if model:
            model.status = application.status
            model.match_score = application.match_score
            model.cover_letter = application.cover_letter
            model.generated_answers = application.generated_answers
            model.qc_approved = application.qc_approved
            model.qc_feedback = application.qc_feedback
            model.submitted_at = application.submitted_at
            model.error_message = application.error_message
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Application {application.id} not found")

    async def count_today(self, *, user_id: str) -> int:
        """Count applications submitted today by user."""
        today_start = datetime.combine(date.today(), datetime.min.time())
        stmt = (
            select(func.count())
            .select_from(ApplicationModel)
            .where(
                and_(
                    ApplicationModel.user_id == user_id,
                    ApplicationModel.submitted_at >= today_start,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _to_domain(self, model: ApplicationModel) -> Application:
        """Convert ORM model to domain entity."""
        return Application(
            id=model.id,
            user_id=model.user_id,
            job_id=model.job_id,
            resume_id=model.resume_id,
            status=model.status,
            match_score=model.match_score,
            match_explanation=None,  # Would deserialize
            cover_letter=model.cover_letter,
            generated_answers=model.generated_answers or {},
            qc_approved=model.qc_approved,
            qc_feedback=model.qc_feedback,
            created_at=model.created_at,
            submitted_at=model.submitted_at,
            error_message=model.error_message,
        )
