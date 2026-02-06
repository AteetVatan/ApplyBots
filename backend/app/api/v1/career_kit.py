"""CareerKit Expert Apply API endpoints.

Standards: python_clean.mdc
- Async operations
- Proper error handling
- kw-only args
"""

import structlog
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.config import get_settings
from app.core.domain.career_kit import (
    CareerKitPhase,
    CustomJD,
    QuestionnaireAnswer,
    ResumeSource,
)
from app.infra.db.repositories.career_kit import SQLCareerKitSessionRepository
from app.infra.db.repositories.job import SQLJobRepository
from app.infra.db.repositories.resume import SQLResumeRepository
from app.infra.db.repositories.resume_draft import SQLResumeDraftRepository
from app.infra.llm.together_client import TogetherLLMClient
from app.schemas.career_kit import (
    AnalyzeRequest,
    AnalyzeResponse,
    AvailableResumesResponse,
    BulletSchema,
    DeltaInstructionSchema,
    EvidenceSchema,
    GapMapItemSchema,
    GenerateRequest,
    GenerateResponse,
    InterviewPrepSchema,
    InterviewQuestionSchema,
    PrepPlanDaySchema,
    QuestionnaireAnswerSchema,
    QuestionSchema,
    RequirementSchema,
    ResumeOptionSchema,
    SaveAnswersRequest,
    SessionDetailResponse,
    SessionListResponse,
    SessionSummarySchema,
    STARStorySchema,
    TailoredCVSchema,
)

router = APIRouter()
logger = structlog.get_logger()


def _get_llm_client() -> TogetherLLMClient:
    """Get configured LLM client."""
    settings = get_settings()
    return TogetherLLMClient(
        api_key=settings.together_api_key.get_secret_value(),
    )


# =============================================================================
# Resume Selection Endpoint
# =============================================================================


@router.get("/resumes", response_model=AvailableResumesResponse)
async def list_available_resumes(
    current_user: CurrentUser,
    db: DBSession,
) -> AvailableResumesResponse:
    """List all available resumes (uploaded + builder drafts) for selection."""
    resume_repo = SQLResumeRepository(session=db)
    draft_repo = SQLResumeDraftRepository(session=db)

    # Get uploaded resumes
    uploaded = await resume_repo.get_by_user_id(current_user.id)
    uploaded_options = [
        ResumeOptionSchema(
            id=r.id,
            name=r.filename,
            source_type="uploaded",
            is_primary=r.is_primary,
            updated_at=r.created_at,
            preview=_get_resume_preview(r.parsed_data) if r.parsed_data else None,
        )
        for r in uploaded
    ]

    # Get builder drafts
    drafts = await draft_repo.get_by_user_id(current_user.id, include_published=True)
    draft_options = [
        ResumeOptionSchema(
            id=d.id,
            name=d.name,
            source_type="draft",
            is_primary=False,
            updated_at=d.updated_at or d.created_at,
            preview=d.content.summary.content[:100] if d.content.summary.content else None,
        )
        for d in drafts
    ]

    return AvailableResumesResponse(
        uploaded_resumes=uploaded_options,
        builder_drafts=draft_options,
    )


def _get_resume_preview(parsed_data) -> str | None:
    """Extract preview text from parsed resume data."""
    if hasattr(parsed_data, "summary") and parsed_data.summary:
        return parsed_data.summary[:100]
    if hasattr(parsed_data, "skills") and parsed_data.skills:
        return f"Skills: {', '.join(parsed_data.skills[:5])}"
    return None


# =============================================================================
# Phase 1: Analyze Endpoint
# =============================================================================


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_job_vs_cv(
    request: AnalyzeRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AnalyzeResponse:
    """Analyze JD vs CV - Phase 1 of Expert Apply.

    Extracts requirements, selects relevant CV bullets, performs gap analysis,
    and generates clarification questionnaire.
    """
    from app.core.services.career_kit import CareerKitService

    try:
        llm = _get_llm_client()
        service = CareerKitService(llm_client=llm)
        session_repo = SQLCareerKitSessionRepository(session=db)

        # Get job details
        job = None
        custom_jd = None
        if request.job_id:
            job_repo = SQLJobRepository(session=db)
            job = await job_repo.get_by_id(request.job_id)
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found",
                )
        elif request.custom_jd:
            custom_jd = CustomJD(
                title=request.custom_jd.title,
                company=request.custom_jd.company,
                description=request.custom_jd.description,
                location=request.custom_jd.location,
                url=request.custom_jd.url,
            )

        # Get resume content
        resume_content = await _get_resume_content(
            db=db,
            source=request.resume_source,
        )

        # Run analysis
        resume_source = ResumeSource(
            source_type=request.resume_source.source_type,
            resume_id=request.resume_source.resume_id,
        )

        result = await service.analyze(
            user_id=current_user.id,
            job=job,
            custom_jd=custom_jd,
            resume_source=resume_source,
            resume_content=resume_content,
        )

        # Save session
        await session_repo.create(result.session)
        await db.commit()

        logger.info(
            "careerkit_analyze_success",
            user_id=current_user.id,
            session_id=result.session.id,
        )

        return AnalyzeResponse(
            session_id=result.session.id,
            session_name=result.session.session_name,
            phase="questionnaire",
            is_custom_job=result.session.is_custom_job,
            requirements=[
                RequirementSchema(
                    name=r.name,
                    level=r.level.value,
                    category=r.category,
                    keywords=r.keywords,
                    original_text=r.original_text,
                )
                for r in result.requirements
            ],
            gap_map=[
                GapMapItemSchema(
                    requirement_name=g.requirement_name,
                    status=g.status.value,
                    evidence=[
                        EvidenceSchema(
                            source=e.source,
                            quote=e.quote,
                            cv_section=e.cv_section,
                        )
                        for e in g.evidence
                    ],
                    risk_note=g.risk_note,
                    question_needed=g.question_needed,
                )
                for g in result.gap_map
            ],
            questionnaire=[
                QuestionSchema(
                    id=q.id,
                    topic=q.topic,
                    question=q.question,
                    answer_type=q.answer_type,
                    why_asked=q.why_asked,
                    options=q.options,
                )
                for q in result.questionnaire
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "careerkit_analyze_error",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


# =============================================================================
# Phase 2: Generate Endpoint
# =============================================================================


@router.post("/generate", response_model=GenerateResponse)
async def generate_tailored_cv(
    request: GenerateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> GenerateResponse:
    """Generate tailored CV and interview prep - Phase 2 of Expert Apply.

    Takes questionnaire answers and generates:
    - Delta instructions for CV modification
    - ATS-optimized tailored CV
    - Interview preparation kit
    """
    from app.core.services.career_kit import CareerKitService

    try:
        llm = _get_llm_client()
        service = CareerKitService(llm_client=llm)
        session_repo = SQLCareerKitSessionRepository(session=db)

        # Load session
        session = await session_repo.get_by_id(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Get original resume content
        resume_content = await _get_resume_content(
            db=db,
            source=session.resume_source,
        )

        # Convert answers
        answers = [
            QuestionnaireAnswer(
                question_id=a.question_id,
                answer=a.answer,
            )
            for a in request.answers
        ]

        # Run generation
        result = await service.generate(
            session=session,
            answers=answers,
            original_cv_content=resume_content,
        )

        # Update session
        await session_repo.update(result.session)
        await db.commit()

        logger.info(
            "careerkit_generate_success",
            user_id=current_user.id,
            session_id=result.session.id,
        )

        return GenerateResponse(
            session_id=result.session.id,
            session_name=result.session.session_name,
            phase="complete",
            is_custom_job=result.session.is_custom_job,
            requirements=[
                RequirementSchema(
                    name=r.name,
                    level=r.level.value,
                    category=r.category,
                    keywords=r.keywords,
                    original_text=r.original_text,
                )
                for r in (result.session.requirements or [])
            ],
            gap_map=[
                GapMapItemSchema(
                    requirement_name=g.requirement_name,
                    status=g.status.value,
                    evidence=[
                        EvidenceSchema(
                            source=e.source,
                            quote=e.quote,
                            cv_section=e.cv_section,
                        )
                        for e in g.evidence
                    ],
                    risk_note=g.risk_note,
                    question_needed=g.question_needed,
                )
                for g in (result.session.gap_map or [])
            ],
            questionnaire=[
                QuestionSchema(
                    id=q.id,
                    topic=q.topic,
                    question=q.question,
                    answer_type=q.answer_type,
                    why_asked=q.why_asked,
                    options=q.options,
                )
                for q in (result.session.questionnaire or [])
            ],
            delta_instructions=[
                DeltaInstructionSchema(
                    bullet_id=d.bullet_id,
                    action=d.action.value,
                    original_text=d.original_text,
                    new_text=d.new_text,
                    confidence_score=d.confidence_score.value,
                    reason=d.reason,
                )
                for d in result.delta_instructions
            ],
            tailored_cv=TailoredCVSchema(
                targeted_title=result.tailored_cv.targeted_title,
                summary=result.tailored_cv.summary,
                skills=result.tailored_cv.skills,
                experience_bullets={
                    k: [
                        BulletSchema(
                            text=b.text,
                            confidence_score=b.confidence_score.value,
                            source_ref=b.source_ref,
                            needs_verification=b.needs_verification,
                        )
                        for b in v
                    ]
                    for k, v in result.tailored_cv.experience_bullets.items()
                },
                projects=[
                    BulletSchema(
                        text=b.text,
                        confidence_score=b.confidence_score.value,
                        source_ref=b.source_ref,
                        needs_verification=b.needs_verification,
                    )
                    for b in result.tailored_cv.projects
                ],
                education=result.tailored_cv.education,
                truth_notes=result.tailored_cv.truth_notes,
            ),
            generated_cv_draft_id=result.session.generated_cv_draft_id,
            interview_prep=InterviewPrepSchema(
                role_understanding=result.interview_prep.role_understanding,
                likely_questions=[
                    InterviewQuestionSchema(
                        question=q.question,
                        category=q.category,
                        difficulty=q.difficulty,
                        suggested_answer=q.suggested_answer,
                    )
                    for q in result.interview_prep.likely_questions
                ],
                suggested_answers=result.interview_prep.suggested_answers,
                story_bank=[
                    STARStorySchema(
                        title=s.title,
                        situation=s.situation,
                        task=s.task,
                        action=s.action,
                        result=s.result,
                        applicable_to=s.applicable_to,
                    )
                    for s in result.interview_prep.story_bank
                ],
                tech_deep_dive_topics=result.interview_prep.tech_deep_dive_topics,
                seven_day_prep_plan=[
                    PrepPlanDaySchema(
                        day=p.day,
                        focus=p.focus,
                        tasks=p.tasks,
                        time_estimate_minutes=p.time_estimate_minutes,
                    )
                    for p in result.interview_prep.seven_day_prep_plan
                ],
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "careerkit_generate_error",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}",
        )


# =============================================================================
# Session Management Endpoints
# =============================================================================


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: CurrentUser,
    db: DBSession,
) -> SessionListResponse:
    """List user's CareerKit sessions."""
    session_repo = SQLCareerKitSessionRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    sessions = await session_repo.get_by_user_id(current_user.id)

    items = []
    for s in sessions:
        # Get job title/company
        if s.job_id:
            job = await job_repo.get_by_id(s.job_id)
            job_title = job.title if job else "Unknown"
            company = job.company if job else "Unknown"
        elif s.custom_jd:
            job_title = s.custom_jd.title
            company = s.custom_jd.company
        else:
            job_title = "Unknown"
            company = "Unknown"

        items.append(
            SessionSummarySchema(
                id=s.id,
                session_name=s.session_name,
                phase=s.phase.value,
                is_custom_job=s.is_custom_job,
                job_title=job_title,
                company=company,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
        )

    return SessionListResponse(
        items=items,
        total=len(items),
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> SessionDetailResponse:
    """Get session details for resuming workflow."""
    session_repo = SQLCareerKitSessionRepository(session=db)

    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return _session_to_detail_response(session)


@router.patch("/sessions/{session_id}/answers")
async def save_answers(
    session_id: str,
    request: SaveAnswersRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Save questionnaire answers (auto-save)."""
    session_repo = SQLCareerKitSessionRepository(session=db)

    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    answers = [
        QuestionnaireAnswer(question_id=a.question_id, answer=a.answer)
        for a in request.answers
    ]

    await session_repo.save_answers(session_id, answers)
    await db.commit()

    return {"status": "saved", "answers_count": len(answers)}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a CareerKit session."""
    session_repo = SQLCareerKitSessionRepository(session=db)

    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    await session_repo.delete(session_id)
    await db.commit()

    return {"status": "deleted"}


# =============================================================================
# Helpers
# =============================================================================


async def _get_resume_content(
    *,
    db,
    source,
):
    """Get resume content based on source type."""
    if source.source_type == "uploaded":
        resume_repo = SQLResumeRepository(session=db)
        resume = await resume_repo.get_by_id(source.resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )
        return resume.parsed_data
    else:
        draft_repo = SQLResumeDraftRepository(session=db)
        draft = await draft_repo.get_by_id(source.resume_id)
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume draft not found",
            )
        return draft.content


def _session_to_detail_response(session) -> SessionDetailResponse:
    """Convert domain session to API response."""
    from app.schemas.career_kit import CustomJDSchema, ResumeSourceSchema

    return SessionDetailResponse(
        id=session.id,
        session_name=session.session_name,
        phase=session.phase.value,
        is_custom_job=session.is_custom_job,
        job_id=session.job_id,
        custom_jd=CustomJDSchema(
            title=session.custom_jd.title,
            company=session.custom_jd.company,
            description=session.custom_jd.description,
            location=session.custom_jd.location,
            url=session.custom_jd.url,
        ) if session.custom_jd else None,
        resume_source=ResumeSourceSchema(
            source_type=session.resume_source.source_type,
            resume_id=session.resume_source.resume_id,
        ),
        requirements=[
            RequirementSchema(
                name=r.name,
                level=r.level.value,
                category=r.category,
                keywords=r.keywords,
                original_text=r.original_text,
            )
            for r in (session.requirements or [])
        ],
        gap_map=[
            GapMapItemSchema(
                requirement_name=g.requirement_name,
                status=g.status.value,
                evidence=[
                    EvidenceSchema(source=e.source, quote=e.quote, cv_section=e.cv_section)
                    for e in g.evidence
                ],
                risk_note=g.risk_note,
                question_needed=g.question_needed,
            )
            for g in (session.gap_map or [])
        ],
        questionnaire=[
            QuestionSchema(
                id=q.id,
                topic=q.topic,
                question=q.question,
                answer_type=q.answer_type,
                why_asked=q.why_asked,
                options=q.options,
            )
            for q in (session.questionnaire or [])
        ],
        answers=[
            QuestionnaireAnswerSchema(question_id=a.question_id, answer=a.answer)
            for a in (session.answers or [])
        ],
        delta_instructions=[
            DeltaInstructionSchema(
                bullet_id=d.bullet_id,
                action=d.action.value,
                original_text=d.original_text,
                new_text=d.new_text,
                confidence_score=d.confidence_score.value,
                reason=d.reason,
            )
            for d in (session.delta_instructions or [])
        ],
        tailored_cv=None,  # Would need to reconstruct from generated_cv
        generated_cv_draft_id=session.generated_cv_draft_id,
        interview_prep=None,  # Would need to reconstruct from interview_prep
        created_at=session.created_at,
        updated_at=session.updated_at,
    )
