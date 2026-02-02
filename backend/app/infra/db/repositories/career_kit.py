"""CareerKit session repository implementation."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.career_kit import (
    CareerKitPhase,
    CareerKitSession,
    ConfidenceScore,
    CustomJD,
    DeltaAction,
    DeltaInstruction,
    Evidence,
    GapMapItem,
    GapStatus,
    InterviewPrep,
    InterviewQuestion,
    PrepPlanDay,
    Question,
    QuestionnaireAnswer,
    Requirement,
    RequirementLevel,
    ResumeSource,
    STARStory,
    TailoredCV,
    CVBullet,
)
from app.infra.db.models import CareerKitSessionModel


class SQLCareerKitSessionRepository:
    """SQLAlchemy implementation of CareerKitSessionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, session_id: str) -> CareerKitSession | None:
        """Get session by ID."""
        result = await self._session.get(CareerKitSessionModel, session_id)
        return self._to_domain(result) if result else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CareerKitSession]:
        """Get all sessions for a user."""
        stmt = (
            select(CareerKitSessionModel)
            .where(CareerKitSessionModel.user_id == user_id)
            .order_by(CareerKitSessionModel.updated_at.desc().nulls_last())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_user_and_job(
        self,
        user_id: str,
        job_id: str,
    ) -> CareerKitSession | None:
        """Get existing session for user + job combination."""
        stmt = select(CareerKitSessionModel).where(
            CareerKitSessionModel.user_id == user_id,
            CareerKitSessionModel.job_id == job_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, session: CareerKitSession) -> CareerKitSession:
        """Create a new session."""
        model = CareerKitSessionModel(
            id=session.id,
            user_id=session.user_id,
            job_id=session.job_id,
            custom_jd=self._custom_jd_to_dict(session.custom_jd),
            session_name=session.session_name,
            is_custom_job=session.is_custom_job,
            phase=session.phase.value,
            resume_source_type=session.resume_source.source_type,
            resume_source_id=session.resume_source.resume_id,
            requirements=self._requirements_to_dict(session.requirements),
            selected_bullets=session.selected_bullets,
            gap_map=self._gap_map_to_dict(session.gap_map),
            questionnaire=self._questionnaire_to_dict(session.questionnaire),
            answers=self._answers_to_dict(session.answers),
            delta_instructions=self._delta_instructions_to_dict(session.delta_instructions),
            generated_cv_draft_id=session.generated_cv_draft_id,
            interview_prep=self._interview_prep_to_dict(session.interview_prep),
            pipeline_messages=session.pipeline_messages,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, session: CareerKitSession) -> CareerKitSession:
        """Update an existing session."""
        model = await self._session.get(CareerKitSessionModel, session.id)
        if not model:
            raise ValueError(f"CareerKit session {session.id} not found")

        model.phase = session.phase.value
        model.requirements = self._requirements_to_dict(session.requirements)
        model.selected_bullets = session.selected_bullets
        model.gap_map = self._gap_map_to_dict(session.gap_map)
        model.questionnaire = self._questionnaire_to_dict(session.questionnaire)
        model.answers = self._answers_to_dict(session.answers)
        model.delta_instructions = self._delta_instructions_to_dict(session.delta_instructions)
        model.generated_cv_draft_id = session.generated_cv_draft_id
        model.interview_prep = self._interview_prep_to_dict(session.interview_prep)
        model.pipeline_messages = session.pipeline_messages
        model.updated_at = datetime.utcnow()

        await self._session.flush()
        return self._to_domain(model)

    async def update_phase(self, session_id: str, phase: CareerKitPhase) -> None:
        """Update only the phase of a session."""
        model = await self._session.get(CareerKitSessionModel, session_id)
        if model:
            model.phase = phase.value
            model.updated_at = datetime.utcnow()
            await self._session.flush()

    async def save_answers(
        self,
        session_id: str,
        answers: list[QuestionnaireAnswer],
    ) -> None:
        """Save questionnaire answers (auto-save)."""
        model = await self._session.get(CareerKitSessionModel, session_id)
        if model:
            model.answers = self._answers_to_dict(answers)
            model.updated_at = datetime.utcnow()
            await self._session.flush()

    async def save_pipeline_messages(
        self,
        session_id: str,
        messages: list[dict],
    ) -> None:
        """Save pipeline messages for debugging."""
        model = await self._session.get(CareerKitSessionModel, session_id)
        if model:
            model.pipeline_messages = messages
            model.updated_at = datetime.utcnow()
            await self._session.flush()

    async def delete(self, session_id: str) -> None:
        """Delete a session."""
        model = await self._session.get(CareerKitSessionModel, session_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def count_by_user_id(self, user_id: str) -> int:
        """Count sessions for a user."""
        stmt = (
            select(func.count())
            .select_from(CareerKitSessionModel)
            .where(CareerKitSessionModel.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    # =========================================================================
    # Domain conversion helpers
    # =========================================================================

    def _to_domain(self, model: CareerKitSessionModel) -> CareerKitSession:
        """Convert ORM model to domain entity."""
        return CareerKitSession(
            id=model.id,
            user_id=model.user_id,
            job_id=model.job_id,
            custom_jd=self._dict_to_custom_jd(model.custom_jd),
            session_name=model.session_name,
            is_custom_job=model.is_custom_job,
            phase=CareerKitPhase(model.phase),
            resume_source=ResumeSource(
                source_type=model.resume_source_type,
                resume_id=model.resume_source_id,
            ),
            requirements=self._dict_to_requirements(model.requirements),
            selected_bullets=model.selected_bullets,
            gap_map=self._dict_to_gap_map(model.gap_map),
            questionnaire=self._dict_to_questionnaire(model.questionnaire),
            answers=self._dict_to_answers(model.answers),
            delta_instructions=self._dict_to_delta_instructions(model.delta_instructions),
            generated_cv_draft_id=model.generated_cv_draft_id,
            interview_prep=self._dict_to_interview_prep(model.interview_prep),
            pipeline_messages=model.pipeline_messages,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -------------------------------------------------------------------------
    # CustomJD serialization
    # -------------------------------------------------------------------------

    def _custom_jd_to_dict(self, jd: CustomJD | None) -> dict | None:
        if not jd:
            return None
        return {
            "title": jd.title,
            "company": jd.company,
            "description": jd.description,
            "location": jd.location,
            "url": jd.url,
        }

    def _dict_to_custom_jd(self, data: dict | None) -> CustomJD | None:
        if not data:
            return None
        return CustomJD(
            title=data.get("title", ""),
            company=data.get("company", ""),
            description=data.get("description", ""),
            location=data.get("location"),
            url=data.get("url"),
        )

    # -------------------------------------------------------------------------
    # Requirements serialization
    # -------------------------------------------------------------------------

    def _requirements_to_dict(self, reqs: list[Requirement] | None) -> list[dict] | None:
        if not reqs:
            return None
        return [
            {
                "name": r.name,
                "level": r.level.value,
                "category": r.category,
                "keywords": r.keywords,
                "original_text": r.original_text,
            }
            for r in reqs
        ]

    def _dict_to_requirements(self, data: list[dict] | None) -> list[Requirement] | None:
        if not data:
            return None
        return [
            Requirement(
                name=r.get("name", ""),
                level=RequirementLevel(r.get("level", "must")),
                category=r.get("category", ""),
                keywords=r.get("keywords", []),
                original_text=r.get("original_text"),
            )
            for r in data
        ]

    # -------------------------------------------------------------------------
    # GapMap serialization
    # -------------------------------------------------------------------------

    def _gap_map_to_dict(self, gap_map: list[GapMapItem] | None) -> list[dict] | None:
        if not gap_map:
            return None
        return [
            {
                "requirement_name": g.requirement_name,
                "status": g.status.value,
                "evidence": [
                    {
                        "source": e.source,
                        "quote": e.quote,
                        "cv_section": e.cv_section,
                    }
                    for e in g.evidence
                ],
                "risk_note": g.risk_note,
                "question_needed": g.question_needed,
            }
            for g in gap_map
        ]

    def _dict_to_gap_map(self, data: list[dict] | None) -> list[GapMapItem] | None:
        if not data:
            return None
        return [
            GapMapItem(
                requirement_name=g.get("requirement_name", ""),
                status=GapStatus(g.get("status", "missing")),
                evidence=[
                    Evidence(
                        source=e.get("source", ""),
                        quote=e.get("quote", ""),
                        cv_section=e.get("cv_section"),
                    )
                    for e in g.get("evidence", [])
                ],
                risk_note=g.get("risk_note"),
                question_needed=g.get("question_needed", False),
            )
            for g in data
        ]

    # -------------------------------------------------------------------------
    # Questionnaire serialization
    # -------------------------------------------------------------------------

    def _questionnaire_to_dict(self, qs: list[Question] | None) -> list[dict] | None:
        if not qs:
            return None
        return [
            {
                "id": q.id,
                "topic": q.topic,
                "question": q.question,
                "answer_type": q.answer_type,
                "why_asked": q.why_asked,
                "options": q.options,
            }
            for q in qs
        ]

    def _dict_to_questionnaire(self, data: list[dict] | None) -> list[Question] | None:
        if not data:
            return None
        return [
            Question(
                id=q.get("id", ""),
                topic=q.get("topic", ""),
                question=q.get("question", ""),
                answer_type=q.get("answer_type", "text"),
                why_asked=q.get("why_asked", ""),
                options=q.get("options"),
            )
            for q in data
        ]

    # -------------------------------------------------------------------------
    # Answers serialization
    # -------------------------------------------------------------------------

    def _answers_to_dict(self, answers: list[QuestionnaireAnswer] | None) -> list[dict] | None:
        if not answers:
            return None
        return [
            {
                "question_id": a.question_id,
                "answer": a.answer,
            }
            for a in answers
        ]

    def _dict_to_answers(self, data: list[dict] | None) -> list[QuestionnaireAnswer] | None:
        if not data:
            return None
        return [
            QuestionnaireAnswer(
                question_id=a.get("question_id", ""),
                answer=a.get("answer", ""),
            )
            for a in data
        ]

    # -------------------------------------------------------------------------
    # Delta instructions serialization
    # -------------------------------------------------------------------------

    def _delta_instructions_to_dict(
        self, deltas: list[DeltaInstruction] | None
    ) -> list[dict] | None:
        if not deltas:
            return None
        return [
            {
                "bullet_id": d.bullet_id,
                "action": d.action.value,
                "original_text": d.original_text,
                "new_text": d.new_text,
                "confidence_score": d.confidence_score.value,
                "reason": d.reason,
            }
            for d in deltas
        ]

    def _dict_to_delta_instructions(
        self, data: list[dict] | None
    ) -> list[DeltaInstruction] | None:
        if not data:
            return None
        return [
            DeltaInstruction(
                bullet_id=d.get("bullet_id", ""),
                action=DeltaAction(d.get("action", "keep")),
                original_text=d.get("original_text"),
                new_text=d.get("new_text"),
                confidence_score=ConfidenceScore(d.get("confidence_score", "high")),
                reason=d.get("reason"),
            )
            for d in data
        ]

    # -------------------------------------------------------------------------
    # Interview prep serialization
    # -------------------------------------------------------------------------

    def _interview_prep_to_dict(self, prep: InterviewPrep | None) -> dict | None:
        if not prep:
            return None
        return {
            "role_understanding": prep.role_understanding,
            "likely_questions": [
                {
                    "question": q.question,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "suggested_answer": q.suggested_answer,
                }
                for q in prep.likely_questions
            ],
            "suggested_answers": prep.suggested_answers,
            "story_bank": [
                {
                    "title": s.title,
                    "situation": s.situation,
                    "task": s.task,
                    "action": s.action,
                    "result": s.result,
                    "applicable_to": s.applicable_to,
                }
                for s in prep.story_bank
            ],
            "tech_deep_dive_topics": prep.tech_deep_dive_topics,
            "seven_day_prep_plan": [
                {
                    "day": p.day,
                    "focus": p.focus,
                    "tasks": p.tasks,
                    "time_estimate_minutes": p.time_estimate_minutes,
                }
                for p in prep.seven_day_prep_plan
            ],
        }

    def _dict_to_interview_prep(self, data: dict | None) -> InterviewPrep | None:
        if not data:
            return None
        return InterviewPrep(
            role_understanding=data.get("role_understanding", ""),
            likely_questions=[
                InterviewQuestion(
                    question=q.get("question", ""),
                    category=q.get("category", ""),
                    difficulty=q.get("difficulty", "medium"),
                    suggested_answer=q.get("suggested_answer"),
                )
                for q in data.get("likely_questions", [])
            ],
            suggested_answers=data.get("suggested_answers", {}),
            story_bank=[
                STARStory(
                    title=s.get("title", ""),
                    situation=s.get("situation", ""),
                    task=s.get("task", ""),
                    action=s.get("action", ""),
                    result=s.get("result", ""),
                    applicable_to=s.get("applicable_to", []),
                )
                for s in data.get("story_bank", [])
            ],
            tech_deep_dive_topics=data.get("tech_deep_dive_topics", []),
            seven_day_prep_plan=[
                PrepPlanDay(
                    day=p.get("day", 1),
                    focus=p.get("focus", ""),
                    tasks=p.get("tasks", []),
                    time_estimate_minutes=p.get("time_estimate_minutes", 60),
                )
                for p in data.get("seven_day_prep_plan", [])
            ],
        )
