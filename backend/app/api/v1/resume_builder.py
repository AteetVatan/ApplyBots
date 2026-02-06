"""Resume builder API endpoints.

Standards: python_clean.mdc
- RESTful endpoint design
- Dependency injection
- Proper error handling
"""

import time
import uuid
from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Path, Query, Response, UploadFile, status
from pydantic import BaseModel

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.services.internal_token import (
    generate_printer_token,
    generate_service_token,
    verify_service_token,
)
from app.infra.services.pdf_printer import generate_pdf
from app.infra.storage.s3 import S3Storage
from app.core.domain.resume import (
    Award,
    AwardsSection,
    Basics,
    Certification,
    CertificationsSection,
    ColorDesign,
    Css,
    CustomLink,
    CustomSection,
    CustomSectionItem,
    Design,
    Education,
    EducationSection,
    ExperienceSection,
    InterestItem,
    InterestsSection,
    LanguageSkill,
    LanguagesSection,
    Layout,
    LevelDesign,
    Metadata,
    Page,
    PageLayout,
    PictureSettings,
    ProfileItem,
    ProfilesSection,
    Project,
    ProjectsSection,
    Publication,
    PublicationsSection,
    Reference,
    ReferencesSection,
    ResumeContent,
    ResumeDraft,
    Sections,
    SkillItem,
    SkillsSection,
    Summary,
    Typography,
    TypographyItem,
    Url,
    Volunteer,
    VolunteerSection,
    WorkExperience,
)
from app.core.services.ai_content_service import AIContentService
from app.core.services.ats_scoring_service import ATSScoringService
from app.infra.db.repositories.resume_draft import SQLResumeDraftRepository
from app.infra.db.repositories.job import SQLJobRepository
from app.schemas.resume_builder import (
    ATSScoreRequest,
    ATSScoreResponse,
    BasicsSchema,
    CertificationsSectionSchema,
    CustomSectionSchema as CustomSectionSchemaAPI,
    DraftCreateRequest,
    DraftListResponse,
    DraftResponse,
    DraftUpdateRequest,
    EnhanceBulletRequest,
    EnhanceBulletResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    MetadataSchema,
    PictureSettingsSchema,
    ProfilePictureResponse,
    ResumeContentSchema,
    SectionsSchema,
    SuggestSkillsRequest,
    SuggestSkillsResponse,
    SummarySchema,
    TailorForJobRequest,
    TailorForJobResponse,
    TemplateListResponse,
    TemplateSchema,
    UrlSchema,
)

logger = structlog.get_logger(__name__)

router = APIRouter()

# UUID regex pattern for draft_id validation
UUID_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


# ============================================================================
# Static Asset Handlers (catch misrouted .svg requests)
# ============================================================================


@router.get("/drafts/{filename}.svg", include_in_schema=False)
@router.get("/drafts/{filename}.png", include_in_schema=False)
@router.get("/drafts/{filename}.jpg", include_in_schema=False)
@router.get("/drafts/{filename}.ico", include_in_schema=False)
async def catch_static_assets(filename: str) -> Response:
    """Catch misrouted static asset requests and return 404.
    
    These requests come from Reactive Resume's iframe trying to load
    theme icons with relative paths. No auth required.
    """
    return Response(status_code=404)


# ============================================================================
# CORS Preflight Handler
# ============================================================================


@router.options("/drafts/{draft_id}")
async def options_draft(draft_id: str = Path(..., pattern=UUID_REGEX)) -> Response:
    """Handle OPTIONS preflight requests for draft endpoints.
    
    This explicit handler ensures OPTIONS requests are handled before
    dependency evaluation, preventing 400 errors on CORS preflight.
    No dependencies to avoid any evaluation issues.
    """
    logger.info("options_draft_handler_called", draft_id=draft_id)
    from app.config import get_settings
    
    settings = get_settings()
    response = Response(status_code=200)
    
    # Add CORS headers
    if settings.app_env == "development":
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "3600"
    
    logger.info("options_draft_response_created", status=200)
    return response


# ============================================================================
# Helper functions for domain conversion
# ============================================================================


def _url_schema_to_domain(url_schema: UrlSchema) -> Url:
    """Convert UrlSchema to Url domain model."""
    return Url(url=url_schema.url, label=url_schema.label)


def _url_domain_to_schema(url: Url) -> UrlSchema:
    """Convert Url domain model to UrlSchema."""
    return UrlSchema(url=url.url, label=url.label)


def schema_to_content(schema: ResumeContentSchema) -> ResumeContent:
    """Convert ResumeContentSchema to ResumeContent domain model."""
    # Convert picture
    picture = PictureSettings(
        hidden=schema.picture.hidden,
        url=schema.picture.url,
        size=schema.picture.size,
        rotation=schema.picture.rotation,
        aspect_ratio=schema.picture.aspect_ratio,
        border_radius=schema.picture.border_radius,
        border_color=schema.picture.border_color,
        border_width=schema.picture.border_width,
        shadow_color=schema.picture.shadow_color,
        shadow_width=schema.picture.shadow_width,
    )

    # Convert basics
    basics = Basics(
        name=schema.basics.name,
        headline=schema.basics.headline,
        email=schema.basics.email,
        phone=schema.basics.phone,
        location=schema.basics.location,
        website=_url_schema_to_domain(schema.basics.website),
        custom_fields=[
            CustomLink(id=cf.id, icon=cf.icon, text=cf.text, link=cf.link)
            for cf in schema.basics.custom_fields
        ],
    )

    # Convert summary
    summary = Summary(
        title=schema.summary.title,
        columns=schema.summary.columns,
        hidden=schema.summary.hidden,
        content=schema.summary.content,
    )

    # Convert sections
    sections = _schema_sections_to_domain(schema.sections)

    # Convert custom sections
    custom_sections = [
        _schema_custom_section_to_domain(cs)
        for cs in schema.custom_sections
    ]

    # Convert metadata
    metadata = _schema_metadata_to_domain(schema.metadata)

    return ResumeContent(
        picture=picture,
        basics=basics,
        summary=summary,
        sections=sections,
        custom_sections=custom_sections,
        metadata=metadata,
    )


def _schema_sections_to_domain(schema: SectionsSchema) -> Sections:
    """Convert SectionsSchema to Sections domain model."""
    return Sections(
        profiles=ProfilesSection(
            title=schema.profiles.title,
            columns=schema.profiles.columns,
            hidden=schema.profiles.hidden,
            items=[
                ProfileItem(
                    id=p.id, hidden=p.hidden, icon=p.icon,
                    network=p.network, username=p.username,
                    website=_url_schema_to_domain(p.website),
                )
                for p in schema.profiles.items
            ],
        ),
        experience=ExperienceSection(
            title=schema.experience.title,
            columns=schema.experience.columns,
            hidden=schema.experience.hidden,
            items=[
                WorkExperience(
                    id=e.id, hidden=e.hidden, company=e.company,
                    title=e.title, location=e.location, period=e.period,
                    website=_url_schema_to_domain(e.website),
                    description=e.description,
                )
                for e in schema.experience.items
            ],
        ),
        education=EducationSection(
            title=schema.education.title,
            columns=schema.education.columns,
            hidden=schema.education.hidden,
            items=[
                Education(
                    id=e.id, hidden=e.hidden, school=e.school,
                    degree=e.degree, area=e.area, grade=e.grade,
                    location=e.location, period=e.period,
                    website=_url_schema_to_domain(e.website),
                    description=e.description,
                )
                for e in schema.education.items
            ],
        ),
        skills=SkillsSection(
            title=schema.skills.title,
            columns=schema.skills.columns,
            hidden=schema.skills.hidden,
            items=[
                SkillItem(
                    id=s.id, hidden=s.hidden, icon=s.icon,
                    name=s.name, proficiency=s.proficiency,
                    level=s.level, keywords=s.keywords,
                )
                for s in schema.skills.items
            ],
        ),
        projects=ProjectsSection(
            title=schema.projects.title,
            columns=schema.projects.columns,
            hidden=schema.projects.hidden,
            items=[
                Project(
                    id=p.id, hidden=p.hidden, name=p.name,
                    period=p.period, website=_url_schema_to_domain(p.website),
                    description=p.description,
                )
                for p in schema.projects.items
            ],
        ),
        awards=AwardsSection(
            title=schema.awards.title,
            columns=schema.awards.columns,
            hidden=schema.awards.hidden,
            items=[
                Award(
                    id=a.id, hidden=a.hidden, title=a.title,
                    awarder=a.awarder, date=a.date,
                    website=_url_schema_to_domain(a.website),
                    description=a.description,
                )
                for a in schema.awards.items
            ],
        ),
        certifications=CertificationsSection(
            title=schema.certifications.title,
            columns=schema.certifications.columns,
            hidden=schema.certifications.hidden,
            items=[
                Certification(
                    id=c.id, hidden=c.hidden, title=c.title,
                    issuer=c.issuer, date=c.date,
                    website=_url_schema_to_domain(c.website),
                    description=c.description,
                )
                for c in schema.certifications.items
            ],
        ),
        languages=LanguagesSection(
            title=schema.languages.title,
            columns=schema.languages.columns,
            hidden=schema.languages.hidden,
            items=[
                LanguageSkill(
                    id=l.id, hidden=l.hidden, language=l.language,
                    fluency=l.fluency, level=l.level,
                )
                for l in schema.languages.items
            ],
        ),
        interests=InterestsSection(
            title=schema.interests.title,
            columns=schema.interests.columns,
            hidden=schema.interests.hidden,
            items=[
                InterestItem(
                    id=i.id, hidden=i.hidden, icon=i.icon,
                    name=i.name, keywords=i.keywords,
                )
                for i in schema.interests.items
            ],
        ),
        volunteer=VolunteerSection(
            title=schema.volunteer.title,
            columns=schema.volunteer.columns,
            hidden=schema.volunteer.hidden,
            items=[
                Volunteer(
                    id=v.id, hidden=v.hidden, organization=v.organization,
                    location=v.location, period=v.period,
                    website=_url_schema_to_domain(v.website),
                    description=v.description,
                )
                for v in schema.volunteer.items
            ],
        ),
        publications=PublicationsSection(
            title=schema.publications.title,
            columns=schema.publications.columns,
            hidden=schema.publications.hidden,
            items=[
                Publication(
                    id=p.id, hidden=p.hidden, title=p.title,
                    publisher=p.publisher, date=p.date,
                    website=_url_schema_to_domain(p.website),
                    description=p.description,
                )
                for p in schema.publications.items
            ],
        ),
        references=ReferencesSection(
            title=schema.references.title,
            columns=schema.references.columns,
            hidden=schema.references.hidden,
            items=[
                Reference(
                    id=r.id, hidden=r.hidden, name=r.name,
                    position=r.position, phone=r.phone,
                    website=_url_schema_to_domain(r.website),
                    description=r.description,
                )
                for r in schema.references.items
            ],
        ),
    )


def _schema_custom_section_to_domain(schema: CustomSectionSchemaAPI) -> CustomSection:
    """Convert CustomSectionSchema to CustomSection domain model."""
    return CustomSection(
        id=schema.id,
        title=schema.title,
        type=schema.type,
        columns=schema.columns,
        hidden=schema.hidden,
        items=[
            CustomSectionItem(
                id=item.id,
                hidden=item.hidden,
                name=item.name,
                title=item.title,
                company=item.company,
                school=item.school,
                organization=item.organization,
                position=item.position,
                location=item.location,
                period=item.period,
                date=item.date,
                website=_url_schema_to_domain(item.website),
                description=item.description,
                content=item.content,
                icon=item.icon,
                keywords=item.keywords,
                proficiency=item.proficiency,
                level=item.level,
                fluency=item.fluency,
                language=item.language,
                awarder=item.awarder,
                issuer=item.issuer,
                publisher=item.publisher,
                phone=item.phone,
                network=item.network,
                username=item.username,
                recipient=item.recipient,
            )
            for item in schema.items
        ],
    )


def _schema_metadata_to_domain(schema: MetadataSchema) -> Metadata:
    """Convert MetadataSchema to Metadata domain model."""
    return Metadata(
        template=schema.template,
        layout=Layout(
            sidebar_width=schema.layout.sidebar_width,
            pages=[
                PageLayout(
                    full_width=p.full_width,
                    main=p.main,
                    sidebar=p.sidebar,
                )
                for p in schema.layout.pages
            ],
        ),
        css=Css(enabled=schema.css.enabled, value=schema.css.value),
        page=Page(
            gap_x=schema.page.gap_x,
            gap_y=schema.page.gap_y,
            margin_x=schema.page.margin_x,
            margin_y=schema.page.margin_y,
            format=schema.page.format,
            locale=schema.page.locale,
            hide_icons=schema.page.hide_icons,
        ),
        design=Design(
            level=LevelDesign(icon=schema.design.level.icon, type=schema.design.level.type),
            colors=ColorDesign(
                primary=schema.design.colors.primary,
                text=schema.design.colors.text,
                background=schema.design.colors.background,
            ),
        ),
        typography=Typography(
            body=TypographyItem(
                font_family=schema.typography.body.font_family,
                font_weights=schema.typography.body.font_weights,
                font_size=schema.typography.body.font_size,
                line_height=schema.typography.body.line_height,
            ),
            heading=TypographyItem(
                font_family=schema.typography.heading.font_family,
                font_weights=schema.typography.heading.font_weights,
                font_size=schema.typography.heading.font_size,
                line_height=schema.typography.heading.line_height,
            ),
        ),
        notes=schema.notes,
    )


def content_to_schema(content: ResumeContent) -> ResumeContentSchema:
    """Convert ResumeContent domain model to ResumeContentSchema."""
    from app.schemas.resume_builder import (
        AwardSchema,
        AwardsSectionSchema,
        BasicsSchema,
        CertificationSchema,
        CertificationsSectionSchema,
        ColorDesignSchema,
        CssSchema,
        CustomLinkSchema,
        CustomSectionItemSchema,
        CustomSectionSchema,
        DesignSchema,
        EducationSchema,
        EducationSectionSchema,
        ExperienceSectionSchema,
        InterestItemSchema,
        InterestsSectionSchema,
        LanguageSkillSchema,
        LanguagesSectionSchema,
        LayoutSchema,
        LevelDesignSchema,
        MetadataSchema,
        PageLayoutSchema,
        PageSchema,
        PictureSettingsSchema,
        ProfileItemSchema,
        ProfilesSectionSchema,
        ProjectSchema,
        ProjectsSectionSchema,
        PublicationSchema,
        PublicationsSectionSchema,
        ReferenceSchema,
        ReferencesSectionSchema,
        SectionsSchema,
        SkillItemSchema,
        SkillsSectionSchema,
        SummarySchema,
        TypographyItemSchema,
        TypographySchema,
        UrlSchema,
        VolunteerSchema,
        VolunteerSectionSchema,
        WorkExperienceSchema,
    )

    # Convert picture
    picture = PictureSettingsSchema(
        hidden=content.picture.hidden,
        url=content.picture.url,
        size=content.picture.size,
        rotation=content.picture.rotation,
        aspectRatio=content.picture.aspect_ratio,
        borderRadius=content.picture.border_radius,
        borderColor=content.picture.border_color,
        borderWidth=content.picture.border_width,
        shadowColor=content.picture.shadow_color,
        shadowWidth=content.picture.shadow_width,
    )

    # Convert basics
    basics = BasicsSchema(
        name=content.basics.name,
        headline=content.basics.headline,
        email=content.basics.email,
        phone=content.basics.phone,
        location=content.basics.location,
        website=UrlSchema(url=content.basics.website.url, label=content.basics.website.label),
        customFields=[
            CustomLinkSchema(id=cf.id, icon=cf.icon, text=cf.text, link=cf.link)
            for cf in content.basics.custom_fields
        ],
    )

    # Convert summary
    summary = SummarySchema(
        title=content.summary.title,
        columns=content.summary.columns,
        hidden=content.summary.hidden,
        content=content.summary.content,
    )

    # Convert sections
    sections = SectionsSchema(
        profiles=ProfilesSectionSchema(
            title=content.sections.profiles.title,
            columns=content.sections.profiles.columns,
            hidden=content.sections.profiles.hidden,
            items=[
                ProfileItemSchema(
                    id=p.id, hidden=p.hidden, icon=p.icon,
                    network=p.network, username=p.username,
                    website=UrlSchema(url=p.website.url, label=p.website.label),
                )
                for p in content.sections.profiles.items
            ],
        ),
        experience=ExperienceSectionSchema(
            title=content.sections.experience.title,
            columns=content.sections.experience.columns,
            hidden=content.sections.experience.hidden,
            items=[
                WorkExperienceSchema(
                    id=e.id, hidden=e.hidden, company=e.company,
                    title=e.title, location=e.location, period=e.period,
                    website=UrlSchema(url=e.website.url, label=e.website.label),
                    description=e.description,
                )
                for e in content.sections.experience.items
            ],
        ),
        education=EducationSectionSchema(
            title=content.sections.education.title,
            columns=content.sections.education.columns,
            hidden=content.sections.education.hidden,
            items=[
                EducationSchema(
                    id=e.id, hidden=e.hidden, school=e.school,
                    degree=e.degree, area=e.area, grade=e.grade,
                    location=e.location, period=e.period,
                    website=UrlSchema(url=e.website.url, label=e.website.label),
                    description=e.description,
                )
                for e in content.sections.education.items
            ],
        ),
        skills=SkillsSectionSchema(
            title=content.sections.skills.title,
            columns=content.sections.skills.columns,
            hidden=content.sections.skills.hidden,
            items=[
                SkillItemSchema(
                    id=s.id, hidden=s.hidden, icon=s.icon,
                    name=s.name, proficiency=s.proficiency,
                    level=s.level, keywords=s.keywords,
                )
                for s in content.sections.skills.items
            ],
        ),
        projects=ProjectsSectionSchema(
            title=content.sections.projects.title,
            columns=content.sections.projects.columns,
            hidden=content.sections.projects.hidden,
            items=[
                ProjectSchema(
                    id=p.id, hidden=p.hidden, name=p.name,
                    period=p.period,
                    website=UrlSchema(url=p.website.url, label=p.website.label),
                    description=p.description,
                )
                for p in content.sections.projects.items
            ],
        ),
        awards=AwardsSectionSchema(
            title=content.sections.awards.title,
            columns=content.sections.awards.columns,
            hidden=content.sections.awards.hidden,
            items=[
                AwardSchema(
                    id=a.id, hidden=a.hidden, title=a.title,
                    awarder=a.awarder, date=a.date,
                    website=UrlSchema(url=a.website.url, label=a.website.label),
                    description=a.description,
                )
                for a in content.sections.awards.items
            ],
        ),
        certifications=CertificationsSectionSchema(
            title=content.sections.certifications.title,
            columns=content.sections.certifications.columns,
            hidden=content.sections.certifications.hidden,
            items=[
                CertificationSchema(
                    id=c.id, hidden=c.hidden, title=c.title,
                    issuer=c.issuer, date=c.date,
                    website=UrlSchema(url=c.website.url, label=c.website.label),
                    description=c.description,
                )
                for c in content.sections.certifications.items
            ],
        ),
        languages=LanguagesSectionSchema(
            title=content.sections.languages.title,
            columns=content.sections.languages.columns,
            hidden=content.sections.languages.hidden,
            items=[
                LanguageSkillSchema(
                    id=l.id, hidden=l.hidden, language=l.language,
                    fluency=l.fluency, level=l.level,
                )
                for l in content.sections.languages.items
            ],
        ),
        interests=InterestsSectionSchema(
            title=content.sections.interests.title,
            columns=content.sections.interests.columns,
            hidden=content.sections.interests.hidden,
            items=[
                InterestItemSchema(
                    id=i.id, hidden=i.hidden, icon=i.icon,
                    name=i.name, keywords=i.keywords,
                )
                for i in content.sections.interests.items
            ],
        ),
        volunteer=VolunteerSectionSchema(
            title=content.sections.volunteer.title,
            columns=content.sections.volunteer.columns,
            hidden=content.sections.volunteer.hidden,
            items=[
                VolunteerSchema(
                    id=v.id, hidden=v.hidden, organization=v.organization,
                    location=v.location, period=v.period,
                    website=UrlSchema(url=v.website.url, label=v.website.label),
                    description=v.description,
                )
                for v in content.sections.volunteer.items
            ],
        ),
        publications=PublicationsSectionSchema(
            title=content.sections.publications.title,
            columns=content.sections.publications.columns,
            hidden=content.sections.publications.hidden,
            items=[
                PublicationSchema(
                    id=p.id, hidden=p.hidden, title=p.title,
                    publisher=p.publisher, date=p.date,
                    website=UrlSchema(url=p.website.url, label=p.website.label),
                    description=p.description,
                )
                for p in content.sections.publications.items
            ],
        ),
        references=ReferencesSectionSchema(
            title=content.sections.references.title,
            columns=content.sections.references.columns,
            hidden=content.sections.references.hidden,
            items=[
                ReferenceSchema(
                    id=r.id, hidden=r.hidden, name=r.name,
                    position=r.position, phone=r.phone,
                    website=UrlSchema(url=r.website.url, label=r.website.label),
                    description=r.description,
                )
                for r in content.sections.references.items
            ],
        ),
    )

    # Convert custom sections
    custom_sections = [
        CustomSectionSchema(
            id=cs.id,
            title=cs.title,
            type=cs.type,
            columns=cs.columns,
            hidden=cs.hidden,
            items=[
                CustomSectionItemSchema(
                    id=item.id,
                    hidden=item.hidden,
                    name=item.name,
                    title=item.title,
                    company=item.company,
                    school=item.school,
                    organization=item.organization,
                    position=item.position,
                    location=item.location,
                    period=item.period,
                    date=item.date,
                    website=UrlSchema(url=item.website.url, label=item.website.label),
                    description=item.description,
                    content=item.content,
                    icon=item.icon,
                    keywords=item.keywords,
                    proficiency=item.proficiency,
                    level=item.level,
                    fluency=item.fluency,
                    language=item.language,
                    awarder=item.awarder,
                    issuer=item.issuer,
                    publisher=item.publisher,
                    phone=item.phone,
                    network=item.network,
                    username=item.username,
                    recipient=item.recipient,
                )
                for item in cs.items
            ],
        )
        for cs in content.custom_sections
    ]

    # Convert metadata
    metadata = MetadataSchema(
        template=content.metadata.template,
        layout=LayoutSchema(
            sidebarWidth=content.metadata.layout.sidebar_width,
            pages=[
                PageLayoutSchema(
                    fullWidth=p.full_width,
                    main=p.main,
                    sidebar=p.sidebar,
                )
                for p in content.metadata.layout.pages
            ],
        ),
        css=CssSchema(enabled=content.metadata.css.enabled, value=content.metadata.css.value),
        page=PageSchema(
            gapX=content.metadata.page.gap_x,
            gapY=content.metadata.page.gap_y,
            marginX=content.metadata.page.margin_x,
            marginY=content.metadata.page.margin_y,
            format=content.metadata.page.format,
            locale=content.metadata.page.locale,
            hideIcons=content.metadata.page.hide_icons,
        ),
        design=DesignSchema(
            level=LevelDesignSchema(
                icon=content.metadata.design.level.icon,
                type=content.metadata.design.level.type,
            ),
            colors=ColorDesignSchema(
                primary=content.metadata.design.colors.primary,
                text=content.metadata.design.colors.text,
                background=content.metadata.design.colors.background,
            ),
        ),
        typography=TypographySchema(
            body=TypographyItemSchema(
                fontFamily=content.metadata.typography.body.font_family,
                fontWeights=content.metadata.typography.body.font_weights,
                fontSize=content.metadata.typography.body.font_size,
                lineHeight=content.metadata.typography.body.line_height,
            ),
            heading=TypographyItemSchema(
                fontFamily=content.metadata.typography.heading.font_family,
                fontWeights=content.metadata.typography.heading.font_weights,
                fontSize=content.metadata.typography.heading.font_size,
                lineHeight=content.metadata.typography.heading.line_height,
            ),
        ),
        notes=content.metadata.notes,
    )

    return ResumeContentSchema(
        picture=picture,
        basics=basics,
        summary=summary,
        sections=sections,
        customSections=custom_sections,
        metadata=metadata,
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
        else ResumeContent()
    )

    # Set template in metadata
    content.metadata.template = request.template_id

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
    draft_id: str = Path(..., pattern=UUID_REGEX),
    *,
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
    draft_id: str = Path(..., pattern=UUID_REGEX),
    *,
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
        draft.content.metadata.template = request.template_id

    draft.updated_at = datetime.utcnow()

    updated = await repo.update(draft)
    logger.debug("draft_updated", draft_id=draft_id)

    return draft_to_response(updated)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_draft(
    draft_id: str = Path(..., pattern=UUID_REGEX),
    *,
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


def _extract_skills_for_ai(content: ResumeContent) -> dict:
    """Extract skills in legacy format for AI services."""
    technical = []
    soft = []
    tools = []
    
    for skill in content.sections.skills.items:
        name = skill.name
        proficiency = skill.proficiency.lower() if skill.proficiency else ""
        
        # Categorize based on proficiency or keywords
        if "soft" in proficiency or any(kw.lower() in ["communication", "leadership", "teamwork"] for kw in skill.keywords):
            soft.append(name)
        elif "tool" in proficiency or "framework" in proficiency:
            tools.append(name)
        else:
            technical.append(name)
            # Add keywords as technical skills
            technical.extend(skill.keywords)
    
    return {"technical": technical, "soft": soft, "tools": tools}


def _extract_work_experience_for_ai(content: ResumeContent) -> list:
    """Extract work experience in legacy format for AI services."""
    return [
        {
            "company": exp.company,
            "title": exp.title,
            "start_date": None,  # Period is stored as string
            "end_date": None,
            "description": exp.description,
            "achievements": [],  # Parse from description if needed
            "location": exp.location,
            "is_current": "present" in exp.period.lower() if exp.period else False,
        }
        for exp in content.sections.experience.items
        if not exp.hidden
    ]


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

    # Convert legacy schema to domain for AI service
    work_experience = [
        WorkExperience(
            company=w.company,
            title=w.title,
            description=w.description or "",
        )
        for w in request.work_experience
    ]

    skills = SkillsSection(items=[
        SkillItem(name=s) for s in (
            request.skills.technical + request.skills.soft + request.skills.tools
        )
    ])

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

    existing_skills = SkillsSection(items=[
        SkillItem(name=s) for s in (
            request.existing_skills.technical + 
            request.existing_skills.soft + 
            request.existing_skills.tools
        )
    ])

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
# Template Endpoints
# ============================================================================

# Template metadata (PDF generation now happens on frontend)
TEMPLATES = [
    # Single-column (ATS Score: 95)
    {"id": "bronzor", "name": "Bronzor", "description": "Clean, minimalist single-column design with profile picture left of name", "ats_score": 95},
    {"id": "kakuna", "name": "Kakuna", "description": "Clean single-column design with subtle styling variations", "ats_score": 95},
    {"id": "rhyhorn", "name": "Rhyhorn", "description": "Clean minimalist single-column design with professional layout", "ats_score": 95},
    {"id": "onyx", "name": "Onyx", "description": "Single-column design with thin border and blue accent line", "ats_score": 95},
    {"id": "lapras", "name": "Lapras", "description": "Single-column layout with pink/magenta header accent and elegant serif typography", "ats_score": 95},
    {"id": "leafish", "name": "Leafish", "description": "Single-column layout with green accent bars and modern typography", "ats_score": 95},
    # Two-column (ATS Score: 88)
    {"id": "azurill", "name": "Azurill", "description": "Two-column layout with purple/magenta gradient sidebar", "ats_score": 88},
    {"id": "chikorita", "name": "Chikorita", "description": "Two-column layout with green sidebar for profile, skills, and certifications", "ats_score": 88},
    {"id": "ditto", "name": "Ditto", "description": "Two-column layout with teal/cyan RIGHT sidebar - unique reversed layout", "ats_score": 88},
    {"id": "ditgar", "name": "Ditgar", "description": "Two-column layout with sky blue sidebar featuring skill progress bars", "ats_score": 88},
    {"id": "gengar", "name": "Gengar", "description": "Two-column layout with blue sidebar for profile, skills, and certifications", "ats_score": 88},
    {"id": "glalie", "name": "Glalie", "description": "Two-column layout with dark emerald sidebar - compact professional design", "ats_score": 88},
    {"id": "pikachu", "name": "Pikachu", "description": "Two-column layout with vibrant yellow/gold sidebar", "ats_score": 88},
]


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates() -> TemplateListResponse:
    """List available resume templates."""
    return TemplateListResponse(
        templates=[
            TemplateSchema(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                ats_score=t["ats_score"],
            )
            for t in TEMPLATES
        ]
    )


# ============================================================================
# Profile Picture Endpoints
# ============================================================================

# Allowed image MIME types and extensions
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


@router.post("/profile-picture", response_model=ProfilePictureResponse)
async def upload_profile_picture(
    file: UploadFile,
    user: CurrentUser,
    settings: AppSettings,
) -> ProfilePictureResponse:
    """Upload a profile picture for the resume.

    - Accepts JPEG, PNG, or WebP images
    - Maximum file size: 5MB
    - Returns the URL to the uploaded image
    """
    # Validate content type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: JPEG, PNG, WebP. Got: {content_type}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: 5MB. Got: {len(content) / 1024 / 1024:.2f}MB",
        )

    # Generate unique filename
    file_ext = ALLOWED_IMAGE_TYPES[content_type]
    file_id = str(uuid.uuid4())
    s3_key = f"profile-pictures/{user.id}/{file_id}.{file_ext}"

    # Upload to S3
    storage = S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )

    url = await storage.upload(
        key=s3_key,
        data=content,
        content_type=content_type,
    )

    logger.info(
        "profile_picture_uploaded",
        user_id=user.id,
        s3_key=s3_key,
        size_bytes=len(content),
        content_type=content_type,
    )

    return ProfilePictureResponse(
        url=url,
        filename=file.filename or f"{file_id}.{file_ext}",
    )


# ============================================================================
# PDF Export Endpoints
# ============================================================================


class PrinterResumeResponse(BaseModel):
    """Response model for internal printer endpoint."""

    id: str
    name: str
    slug: str
    tags: list[str]
    data: dict[str, Any]
    user_id: str
    is_locked: bool
    updated_at: datetime


class PDFExportResponse(BaseModel):
    """Response model for PDF export endpoint."""

    url: str
    key: str


def content_to_reactive_resume_format(
    content: ResumeContent,
    draft_name: str,
) -> dict[str, Any]:
    """Convert ResumeContent to Reactive Resume data format for PDF printing.
    
    Since the new schema mirrors Reactive Resume's format, this is now a direct
    conversion using the repository's serialization logic.
    """
    from app.infra.db.repositories.resume_draft import SQLResumeDraftRepository
    
    # Create a temporary repository instance just for serialization
    # This is a bit of a hack, but it reuses the same serialization logic
    class TempRepo(SQLResumeDraftRepository):
        def __init__(self):
            pass  # Don't need session for serialization
    
    repo = TempRepo()
    return repo._content_to_dict(content)


@router.get(
    "/internal/printer/resume/{draft_id}",
    response_model=PrinterResumeResponse,
    include_in_schema=False,
)
async def get_resume_for_printer(
    draft_id: str = Path(..., pattern=UUID_REGEX),
    service_token: str = Query(..., description="Internal service token"),
    *,
    settings: AppSettings,
    db: DBSession,
) -> PrinterResumeResponse:
    """Internal endpoint for printer service. Uses service token for auth.

    This endpoint is called by Reactive Resume's printer route when
    generating PDFs. It validates the service token and returns resume
    data in Reactive Resume format.
    """
    # Verify service token
    payload = verify_service_token(
        token=service_token,
        secret=settings.internal_service_secret.get_secret_value(),
    )
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired service token",
        )

    if payload.resume_id != draft_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token/resume mismatch",
        )

    # Get draft
    repo = SQLResumeDraftRepository(session=db)
    draft = await repo.get_by_id(draft_id)

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Verify ownership (token user_id must match draft owner)
    if draft.user_id != payload.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Convert to Reactive Resume format
    rr_data = content_to_reactive_resume_format(draft.content, draft.name)

    logger.info(
        "internal_printer_resume_fetched",
        draft_id=draft_id,
        user_id=payload.user_id,
    )

    return PrinterResumeResponse(
        id=draft.id,
        name=draft.name,
        slug=draft.id,  # Use ID as slug
        tags=[],
        data=rr_data,
        user_id=draft.user_id,
        is_locked=False,
        updated_at=draft.updated_at or draft.created_at,
    )


@router.post(
    "/drafts/{draft_id}/export-pdf",
    response_model=PDFExportResponse,
)
async def export_draft_as_pdf(
    draft_id: str = Path(..., pattern=UUID_REGEX),
    *,
    user: CurrentUser,
    settings: AppSettings,
    db: DBSession,
) -> PDFExportResponse:
    """Export resume draft as PDF using Playwright + Reactive Resume templates.

    This endpoint:
    1. Validates user ownership of the draft
    2. Generates secure tokens for the PDF generation service
    3. Uses Playwright to render the resume via Reactive Resume's printer route
    4. Uploads the generated PDF to S3
    5. Returns the URL to the PDF
    """
    # Verify ownership
    repo = SQLResumeDraftRepository(session=db)
    draft = await repo.get_by_id(draft_id)

    if not draft or draft.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Generate tokens
    service_token = generate_service_token(
        user_id=user.id,
        resume_id=draft_id,
        secret=settings.internal_service_secret.get_secret_value(),
    )
    printer_token = generate_printer_token(
        resume_id=draft_id,
        secret=settings.printer_token_secret.get_secret_value(),
    )

    # Get page metadata from content
    page_metadata = draft.content.metadata.page
    page_format = page_metadata.format
    margin_x = page_metadata.margin_x
    margin_y = page_metadata.margin_y

    logger.info(
        "pdf_export_starting",
        draft_id=draft_id,
        user_id=user.id,
        page_format=page_format,
        margin_x=margin_x,
        margin_y=margin_y,
    )

    # Generate PDF using Playwright
    try:
        pdf_buffer = await generate_pdf(
            reactive_resume_url=settings.reactive_resume_url,
            resume_id=draft_id,
            printer_token=printer_token,
            service_token=service_token,
            page_format=page_format,
            margin_x=margin_x,
            margin_y=margin_y,
        )
    except RuntimeError as e:
        logger.error(
            "pdf_export_failed",
            draft_id=draft_id,
            user_id=user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {e}",
        )

    # Upload to S3
    storage = S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )

    timestamp = int(time.time() * 1000)
    s3_key = f"uploads/{user.id}/pdfs/{draft_id}/{timestamp}.pdf"

    # Upload the PDF
    await storage.upload(
        key=s3_key,
        data=pdf_buffer,
        content_type="application/pdf",
    )

    # Get a presigned URL for download (valid for 1 hour)
    presigned_url = await storage.get_presigned_url(
        key=s3_key,
        expires_in=3600,
    )

    logger.info(
        "pdf_export_completed",
        draft_id=draft_id,
        user_id=user.id,
        s3_key=s3_key,
        size_bytes=len(pdf_buffer),
    )

    return PDFExportResponse(url=presigned_url, key=s3_key)
