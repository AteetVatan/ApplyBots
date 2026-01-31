"""Application repository implementation."""

from datetime import date, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.domain.application import (
    Application,
    ApplicationNote,
    ApplicationStage,
    ApplicationStatus,
)
from app.infra.db.models import ApplicationModel, ApplicationNoteModel


class SQLApplicationRepository:
    """SQLAlchemy implementation of ApplicationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, application_id: str) -> Application | None:
        """Get application by ID with notes."""
        stmt = (
            select(ApplicationModel)
            .where(ApplicationModel.id == application_id)
            .options(selectinload(ApplicationModel.notes))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        status: ApplicationStatus | None = None,
        stage: ApplicationStage | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Application]:
        """Get applications for a user, optionally filtered by status/stage."""
        conditions = [ApplicationModel.user_id == user_id]
        if status:
            conditions.append(ApplicationModel.status == status)
        if stage:
            conditions.append(ApplicationModel.stage == stage)

        stmt = (
            select(ApplicationModel)
            .where(and_(*conditions))
            .options(selectinload(ApplicationModel.notes))
            .order_by(ApplicationModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_grouped_by_stage(
        self,
        user_id: str,
        *,
        search: str | None = None,
    ) -> dict[ApplicationStage, list[Application]]:
        """Get applications grouped by stage for Kanban view."""
        conditions = [
            ApplicationModel.user_id == user_id,
            ApplicationModel.stage != ApplicationStage.REJECTED,
        ]

        stmt = (
            select(ApplicationModel)
            .where(and_(*conditions))
            .options(selectinload(ApplicationModel.notes))
            .order_by(ApplicationModel.stage_updated_at.desc().nulls_last())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        grouped: dict[ApplicationStage, list[Application]] = {
            ApplicationStage.SAVED: [],
            ApplicationStage.APPLIED: [],
            ApplicationStage.INTERVIEWING: [],
            ApplicationStage.OFFER: [],
        }
        for model in models:
            app = self._to_domain(model)
            if model.stage in grouped:
                grouped[model.stage].append(app)

        return grouped

    async def create(self, application: Application) -> Application:
        """Create a new application."""
        model = ApplicationModel(
            id=application.id,
            user_id=application.user_id,
            job_id=application.job_id,
            resume_id=application.resume_id,
            status=application.status,
            stage=application.stage,
            match_score=application.match_score,
            match_explanation=None,  # Would serialize MatchExplanation
            cover_letter=application.cover_letter,
            generated_answers=application.generated_answers,
            qc_approved=application.qc_approved,
            qc_feedback=application.qc_feedback,
            created_at=application.created_at,
            submitted_at=application.submitted_at,
            stage_updated_at=application.stage_updated_at,
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
            model.stage = application.stage
            model.match_score = application.match_score
            model.cover_letter = application.cover_letter
            model.generated_answers = application.generated_answers
            model.qc_approved = application.qc_approved
            model.qc_feedback = application.qc_feedback
            model.submitted_at = application.submitted_at
            model.stage_updated_at = application.stage_updated_at
            model.error_message = application.error_message
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Application {application.id} not found")

    async def update_stage(
        self,
        application_id: str,
        *,
        stage: ApplicationStage,
    ) -> Application | None:
        """Update application stage (for drag-drop)."""
        model = await self._session.get(ApplicationModel, application_id)
        if model:
            model.stage = stage
            model.stage_updated_at = datetime.utcnow()
            await self._session.flush()
            return self._to_domain(model)
        return None

    async def add_note(
        self,
        application_id: str,
        *,
        note_id: str,
        content: str,
    ) -> ApplicationNote:
        """Add a note to an application."""
        note_model = ApplicationNoteModel(
            id=note_id,
            application_id=application_id,
            content=content,
            created_at=datetime.utcnow(),
        )
        self._session.add(note_model)
        await self._session.flush()
        return ApplicationNote(
            id=note_model.id,
            content=note_model.content,
            created_at=note_model.created_at,
        )

    async def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        note = await self._session.get(ApplicationNoteModel, note_id)
        if note:
            await self._session.delete(note)
            await self._session.flush()
            return True
        return False

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
        notes = [
            ApplicationNote(
                id=n.id,
                content=n.content,
                created_at=n.created_at,
            )
            for n in (model.notes or [])
        ]
        return Application(
            id=model.id,
            user_id=model.user_id,
            job_id=model.job_id,
            resume_id=model.resume_id,
            status=model.status,
            stage=model.stage,
            match_score=model.match_score,
            match_explanation=None,  # Would deserialize
            cover_letter=model.cover_letter,
            generated_answers=model.generated_answers or {},
            notes=notes,
            qc_approved=model.qc_approved,
            qc_feedback=model.qc_feedback,
            created_at=model.created_at,
            submitted_at=model.submitted_at,
            stage_updated_at=model.stage_updated_at,
            error_message=model.error_message,
        )
