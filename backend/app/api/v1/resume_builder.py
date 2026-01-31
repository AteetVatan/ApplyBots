"""Resume builder API endpoints.

Standards: python_clean.mdc
- RESTful endpoint design
- Dependency injection
- Proper error handling
"""

import uuid
from datetime import datetime

import structlog
from fastapi import APIRouter, HTTPException, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.domain.resume import (
    Award,
    Certification,
    CustomSection,
    Education,
    LanguageProficiency,
    LanguageSkill,
    Project,
    ResumeContent,
    ResumeDraft,
    SkillsSection,
    WorkExperience,
)
from app.core.services.ai_content_service import AIContentService
from app.core.services.ats_scoring_service import ATSScoringService
from app.infra.db.repositories.resume_draft import SQLResumeDraftRepository
from app.infra.db.repositories.job import SQLJobRepository
from app.infra.services.pdf_generator import PDFGeneratorService
from app.schemas.resume_builder import (
    ATSScoreRequest,
    ATSScoreResponse,
    DraftCreateRequest,
    DraftListResponse,
    DraftResponse,
    DraftUpdateRequest,
    EnhanceBulletRequest,
    EnhanceBulletResponse,
    ExportPDFResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    ResumeContentSchema,
    SuggestSkillsRequest,
    SuggestSkillsResponse,
    TailorForJobRequest,
    TailorForJobResponse,
    TemplateListResponse,
    TemplateSchema,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# Helper functions for domain conversion
# ============================================================================


def schema_to_content(schema: ResumeContentSchema) -> ResumeContent:
    """Convert schema to domain model."""
    return ResumeContent(
        full_name=schema.full_name,
        email=schema.email,
        phone=schema.phone,
        location=schema.location,
        linkedin_url=schema.linkedin_url,
        portfolio_url=schema.portfolio_url,
        github_url=schema.github_url,
        professional_summary=schema.professional_summary,
        work_experience=[
            WorkExperience(
                company=w.company,
                title=w.title,
                start_date=w.start_date,
                end_date=w.end_date,
                description=w.description,
                achievements=w.achievements,
                location=w.location,
                is_current=w.is_current,
            )
            for w in schema.work_experience
        ],
        education=[
            Education(
                institution=e.institution,
                degree=e.degree,
                field_of_study=e.field_of_study,
                graduation_date=e.graduation_date,
                gpa=e.gpa,
                location=e.location,
                achievements=e.achievements,
            )
            for e in schema.education
        ],
        skills=SkillsSection(
            technical=schema.skills.technical,
            soft=schema.skills.soft,
            tools=schema.skills.tools,
        ),
        projects=[
            Project(
                name=p.name,
                description=p.description,
                url=p.url,
                technologies=p.technologies,
                start_date=p.start_date,
                end_date=p.end_date,
                highlights=p.highlights,
            )
            for p in schema.projects
        ],
        certifications=[
            Certification(
                name=c.name,
                issuer=c.issuer,
                date=c.date,
                expiry_date=c.expiry_date,
                credential_id=c.credential_id,
                url=c.url,
            )
            for c in schema.certifications
        ],
        awards=[
            Award(
                title=a.title,
                issuer=a.issuer,
                date=a.date,
                description=a.description,
            )
            for a in schema.awards
        ],
        languages=[
            LanguageSkill(
                language=lang.language,
                proficiency=LanguageProficiency(lang.proficiency),
            )
            for lang in schema.languages
        ],
        custom_sections=[
            CustomSection(
                id=cs.id,
                title=cs.title,
                items=cs.items,
            )
            for cs in schema.custom_sections
        ],
        template_id=schema.template_id,
        section_order=schema.section_order,
        ats_score=schema.ats_score,
    )


def content_to_schema(content: ResumeContent) -> ResumeContentSchema:
    """Convert domain model to schema."""
    from app.schemas.resume_builder import (
        AwardSchema,
        CertificationSchema,
        CustomSectionSchema,
        EducationSchema,
        LanguageSkillSchema,
        ProjectSchema,
        SkillsSectionSchema,
        WorkExperienceSchema,
    )

    return ResumeContentSchema(
        full_name=content.full_name,
        email=content.email,
        phone=content.phone,
        location=content.location,
        linkedin_url=content.linkedin_url,
        portfolio_url=content.portfolio_url,
        github_url=content.github_url,
        professional_summary=content.professional_summary,
        work_experience=[
            WorkExperienceSchema(
                company=w.company,
                title=w.title,
                start_date=w.start_date,
                end_date=w.end_date,
                description=w.description,
                achievements=w.achievements,
                location=w.location,
                is_current=w.is_current,
            )
            for w in content.work_experience
        ],
        education=[
            EducationSchema(
                institution=e.institution,
                degree=e.degree,
                field_of_study=e.field_of_study,
                graduation_date=e.graduation_date,
                gpa=e.gpa,
                location=e.location,
                achievements=e.achievements,
            )
            for e in content.education
        ],
        skills=SkillsSectionSchema(
            technical=content.skills.technical,
            soft=content.skills.soft,
            tools=content.skills.tools,
        ),
        projects=[
            ProjectSchema(
                name=p.name,
                description=p.description,
                url=p.url,
                technologies=p.technologies,
                start_date=p.start_date,
                end_date=p.end_date,
                highlights=p.highlights,
            )
            for p in content.projects
        ],
        certifications=[
            CertificationSchema(
                name=c.name,
                issuer=c.issuer,
                date=c.date,
                expiry_date=c.expiry_date,
                credential_id=c.credential_id,
                url=c.url,
            )
            for c in content.certifications
        ],
        awards=[
            AwardSchema(
                title=a.title,
                issuer=a.issuer,
                date=a.date,
                description=a.description,
            )
            for a in content.awards
        ],
        languages=[
            LanguageSkillSchema(
                language=lang.language,
                proficiency=lang.proficiency.value,
            )
            for lang in content.languages
        ],
        custom_sections=[
            CustomSectionSchema(
                id=cs.id,
                title=cs.title,
                items=cs.items,
            )
            for cs in content.custom_sections
        ],
        template_id=content.template_id,
        section_order=content.section_order,
        ats_score=content.ats_score,
    )


def draft_to_response(draft: ResumeDraft) -> DraftResponse:
    """Convert draft domain model to response schema."""
    return DraftResponse(
        id=draft.id,
        name=draft.name,
        content=content_to_schema(draft.content),
        template_id=draft.template_id,
        ats_score=draft.ats_score,
        is_published=draft.is_published,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


# ============================================================================
# Draft CRUD Endpoints
# ============================================================================


@router.get("/drafts", response_model=DraftListResponse)
async def list_drafts(
    user: CurrentUser,
    db: DBSession,
    limit: int = 50,
    offset: int = 0,
) -> DraftListResponse:
    """List user's resume drafts."""
    repo = SQLResumeDraftRepository(session=db)

    drafts = await repo.get_by_user_id(
        user.id,
        include_published=False,
        limit=limit,
        offset=offset,
    )
    total = await repo.count_by_user_id(user.id)

    return DraftListResponse(
        items=[draft_to_response(d) for d in drafts],
        total=total,
    )


@router.post("/drafts", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    request: DraftCreateRequest,
    user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    """Create a new resume draft."""
    repo = SQLResumeDraftRepository(session=db)

    # Create default content if not provided
    content = (
        schema_to_content(request.content)
        if request.content
        else ResumeContent(template_id=request.template_id)
    )

    draft = ResumeDraft(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=request.name,
        content=content,
        template_id=request.template_id,
        created_at=datetime.utcnow(),
    )

    created = await repo.create(draft)
    logger.info("draft_created", draft_id=created.id, user_id=user.id)

    return draft_to_response(created)


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: str,
    user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    """Get a specific draft by ID."""
    repo = SQLResumeDraftRepository(session=db)
    draft = await repo.get_by_id(draft_id)

    if not draft or draft.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    return draft_to_response(draft)


@router.patch("/drafts/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    request: DraftUpdateRequest,
    user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    """Update a draft (autosave endpoint)."""
    repo = SQLResumeDraftRepository(session=db)
    draft = await repo.get_by_id(draft_id)

    if not draft or draft.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Update fields
    if request.name is not None:
        draft.name = request.name
    if request.content is not None:
        draft.content = schema_to_content(request.content)
    if request.template_id is not None:
        draft.template_id = request.template_id

    draft.updated_at = datetime.utcnow()

    updated = await repo.update(draft)
    logger.debug("draft_updated", draft_id=draft_id)

    return draft_to_response(updated)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: str,
    user: CurrentUser,
    db: DBSession,
) -> None:
    """Delete a draft."""
    repo = SQLResumeDraftRepository(session=db)
    draft = await repo.get_by_id(draft_id)

    if not draft or draft.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    await repo.delete(draft_id)
    logger.info("draft_deleted", draft_id=draft_id, user_id=user.id)


# ============================================================================
# AI Feature Endpoints
# ============================================================================


@router.post("/ai/summary", response_model=GenerateSummaryResponse)
async def generate_summary(
    request: GenerateSummaryRequest,
    user: CurrentUser,
    settings: AppSettings,
) -> GenerateSummaryResponse:
    """Generate AI-powered professional summary."""
    from app.infra.llm.together_client import TogetherLLMClient

    llm_client = TogetherLLMClient(
        api_key=settings.together_api_key.get_secret_value()
    )
    ai_service = AIContentService(llm_client=llm_client)

    # Convert schema to domain
    work_experience = [
        WorkExperience(
            company=w.company,
            title=w.title,
            start_date=w.start_date,
            end_date=w.end_date,
            description=w.description,
            achievements=w.achievements,
            location=w.location,
            is_current=w.is_current,
        )
        for w in request.work_experience
    ]

    skills = SkillsSection(
        technical=request.skills.technical,
        soft=request.skills.soft,
        tools=request.skills.tools,
    )

    result = await ai_service.generate_summary(
        work_experience=work_experience,
        skills=skills,
        target_role=request.target_role,
        years_of_experience=request.years_of_experience,
    )

    return GenerateSummaryResponse(
        content=result.content,
        model_used=result.model_used,
        tokens_used=result.tokens_used,
    )


@router.post("/ai/enhance-bullet", response_model=EnhanceBulletResponse)
async def enhance_bullet(
    request: EnhanceBulletRequest,
    user: CurrentUser,
    settings: AppSettings,
) -> EnhanceBulletResponse:
    """Enhance a bullet point with AI."""
    from app.infra.llm.together_client import TogetherLLMClient

    llm_client = TogetherLLMClient(
        api_key=settings.together_api_key.get_secret_value()
    )
    ai_service = AIContentService(llm_client=llm_client)

    result = await ai_service.enhance_bullet_point(
        original=request.original,
        job_title=request.job_title,
        company=request.company,
    )

    return EnhanceBulletResponse(
        original=result.original,
        enhanced=result.enhanced,
        improvements=result.improvements,
    )


@router.post("/ai/suggest-skills", response_model=SuggestSkillsResponse)
async def suggest_skills(
    request: SuggestSkillsRequest,
    user: CurrentUser,
    settings: AppSettings,
) -> SuggestSkillsResponse:
    """Suggest skills based on job title."""
    from app.infra.llm.together_client import TogetherLLMClient

    llm_client = TogetherLLMClient(
        api_key=settings.together_api_key.get_secret_value()
    )
    ai_service = AIContentService(llm_client=llm_client)

    existing_skills = SkillsSection(
        technical=request.existing_skills.technical,
        soft=request.existing_skills.soft,
        tools=request.existing_skills.tools,
    )

    result = await ai_service.suggest_skills(
        job_title=request.job_title,
        existing_skills=existing_skills,
        industry=request.industry,
    )

    return SuggestSkillsResponse(
        technical=result.technical,
        soft=result.soft,
        tools=result.tools,
        reasoning=result.reasoning,
    )


@router.post("/ai/tailor", response_model=TailorForJobResponse)
async def tailor_for_job(
    request: TailorForJobRequest,
    user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> TailorForJobResponse:
    """Tailor resume for a specific job."""
    from app.infra.llm.together_client import TogetherLLMClient

    # Get the job
    job_repo = SQLJobRepository(session=db)
    job = await job_repo.get_by_id(request.job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    llm_client = TogetherLLMClient(
        api_key=settings.together_api_key.get_secret_value()
    )
    ai_service = AIContentService(llm_client=llm_client)

    content = schema_to_content(request.content)
    result = await ai_service.tailor_for_job(content=content, job=job)

    return TailorForJobResponse(
        content=content_to_schema(result.content),
        changes_made=result.changes_made,
        keyword_matches=result.keyword_matches,
        suggestions=result.suggestions,
    )


# ============================================================================
# ATS Scoring Endpoint
# ============================================================================


@router.post("/ats-score", response_model=ATSScoreResponse)
async def calculate_ats_score(
    request: ATSScoreRequest,
    user: CurrentUser,
) -> ATSScoreResponse:
    """Calculate ATS compatibility score."""
    ats_service = ATSScoringService()
    content = schema_to_content(request.content)

    result = ats_service.calculate_score(
        content=content,
        job_description=request.job_description,
    )

    return ATSScoreResponse(
        total_score=result.total_score,
        keyword_match_score=result.keyword_match_score,
        formatting_score=result.formatting_score,
        section_completeness_score=result.section_completeness_score,
        quantified_achievements_score=result.quantified_achievements_score,
        length_score=result.length_score,
        contact_info_score=result.contact_info_score,
        suggestions=result.suggestions,
        matched_keywords=result.matched_keywords,
        missing_keywords=result.missing_keywords,
    )


# ============================================================================
# PDF Export Endpoint
# ============================================================================


@router.post("/drafts/{draft_id}/export-pdf", response_model=ExportPDFResponse)
async def export_pdf(
    draft_id: str,
    user: CurrentUser,
    db: DBSession,
    template_id: str | None = None,
) -> ExportPDFResponse:
    """Export draft as PDF."""
    repo = SQLResumeDraftRepository(session=db)
    draft = await repo.get_by_id(draft_id)

    if not draft or draft.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    pdf_service = PDFGeneratorService()

    # Generate PDF bytes
    pdf_bytes = await pdf_service.generate_pdf(
        content=draft.content,
        template_id=template_id or draft.template_id,
    )

    # For now, return the PDF as base64 data URL
    # In production, upload to S3 and return presigned URL
    import base64

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    data_url = f"data:application/pdf;base64,{pdf_base64}"

    filename = f"{draft.content.full_name or 'resume'}.pdf".replace(" ", "_")

    logger.info(
        "pdf_exported",
        draft_id=draft_id,
        user_id=user.id,
        size_bytes=len(pdf_bytes),
    )

    return ExportPDFResponse(
        url=data_url,
        filename=filename,
    )


# ============================================================================
# Template Endpoints
# ============================================================================


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates() -> TemplateListResponse:
    """List available resume templates."""
    pdf_service = PDFGeneratorService()
    templates = pdf_service.get_available_templates()

    return TemplateListResponse(
        templates=[
            TemplateSchema(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                ats_score=t["ats_score"],
            )
            for t in templates
        ]
    )
