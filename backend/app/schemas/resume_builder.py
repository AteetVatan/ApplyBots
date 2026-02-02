"""Resume builder schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================================
# Sub-schemas for resume content
# ============================================================================


class WorkExperienceSchema(BaseModel):
    """Work experience entry schema."""

    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    location: str | None = None
    is_current: bool = False


class EducationSchema(BaseModel):
    """Education entry schema."""

    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_date: str | None = None
    gpa: float | None = None
    location: str | None = None
    achievements: list[str] = Field(default_factory=list)


class ProjectSchema(BaseModel):
    """Project entry schema."""

    name: str
    description: str
    url: str | None = None
    technologies: list[str] = Field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None
    highlights: list[str] = Field(default_factory=list)


class AwardSchema(BaseModel):
    """Award entry schema."""

    title: str
    issuer: str
    date: str | None = None
    description: str | None = None


class CertificationSchema(BaseModel):
    """Certification entry schema."""

    name: str
    issuer: str
    date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None
    url: str | None = None


class LanguageSkillSchema(BaseModel):
    """Language skill schema."""

    language: str
    proficiency: Literal["native", "fluent", "conversational", "basic"] = "conversational"


class SkillsSectionSchema(BaseModel):
    """Skills section schema."""

    technical: list[str] = Field(default_factory=list)
    soft: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class CustomSectionSchema(BaseModel):
    """Custom section schema."""

    id: str
    title: str
    items: list[str] = Field(default_factory=list)


class CustomLinkSchema(BaseModel):
    """Custom link schema."""

    id: str
    label: str
    url: str


# ============================================================================
# Resume Content Schema
# ============================================================================


class ResumeContentSchema(BaseModel):
    """Complete resume content schema."""

    # Contact Information
    full_name: str = ""
    email: str = ""
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    profile_picture_url: str | None = None
    custom_links: list[CustomLinkSchema] = Field(default_factory=list)

    # Professional Summary
    professional_summary: str | None = None

    # Main Sections
    work_experience: list[WorkExperienceSchema] = Field(default_factory=list)
    education: list[EducationSchema] = Field(default_factory=list)
    skills: SkillsSectionSchema = Field(default_factory=SkillsSectionSchema)
    projects: list[ProjectSchema] = Field(default_factory=list)
    certifications: list[CertificationSchema] = Field(default_factory=list)
    awards: list[AwardSchema] = Field(default_factory=list)
    languages: list[LanguageSkillSchema] = Field(default_factory=list)
    custom_sections: list[CustomSectionSchema] = Field(default_factory=list)

    # Metadata
    template_id: str = "professional-modern"
    section_order: list[str] = Field(default_factory=list)
    ats_score: int | None = None


# ============================================================================
# Draft CRUD Schemas
# ============================================================================


class DraftCreateRequest(BaseModel):
    """Request to create a new draft."""

    name: str = Field(..., max_length=255)
    content: ResumeContentSchema | None = None
    template_id: str = "professional-modern"


class DraftUpdateRequest(BaseModel):
    """Request to update a draft (autosave)."""

    name: str | None = Field(None, max_length=255)
    content: ResumeContentSchema | None = None
    template_id: str | None = None


class DraftResponse(BaseModel):
    """Draft response schema."""

    id: str
    name: str
    content: ResumeContentSchema
    template_id: str
    ats_score: int | None
    is_published: bool
    created_at: datetime
    updated_at: datetime | None


class DraftListResponse(BaseModel):
    """List of drafts response."""

    items: list[DraftResponse]
    total: int


# ============================================================================
# AI Feature Schemas
# ============================================================================


class GenerateSummaryRequest(BaseModel):
    """Request to generate AI summary."""

    work_experience: list[WorkExperienceSchema] = Field(default_factory=list)
    skills: SkillsSectionSchema = Field(default_factory=SkillsSectionSchema)
    target_role: str | None = None
    years_of_experience: float | None = None


class GenerateSummaryResponse(BaseModel):
    """AI summary generation response."""

    content: str
    model_used: str
    tokens_used: int


class EnhanceBulletRequest(BaseModel):
    """Request to enhance a bullet point."""

    original: str
    job_title: str | None = None
    company: str | None = None


class EnhanceBulletResponse(BaseModel):
    """Enhanced bullet point response."""

    original: str
    enhanced: str
    improvements: list[str]


class SuggestSkillsRequest(BaseModel):
    """Request to suggest skills."""

    job_title: str
    existing_skills: SkillsSectionSchema = Field(default_factory=SkillsSectionSchema)
    industry: str | None = None


class SuggestSkillsResponse(BaseModel):
    """Skill suggestions response."""

    technical: list[str]
    soft: list[str]
    tools: list[str]
    reasoning: str


class TailorForJobRequest(BaseModel):
    """Request to tailor resume for a job."""

    content: ResumeContentSchema
    job_id: str


class TailorForJobResponse(BaseModel):
    """Tailored resume response."""

    content: ResumeContentSchema
    changes_made: list[str]
    keyword_matches: list[str]
    suggestions: list[str]


# ============================================================================
# ATS Scoring Schemas
# ============================================================================


class ATSScoreRequest(BaseModel):
    """Request to calculate ATS score."""

    content: ResumeContentSchema
    job_description: str | None = None


class ATSScoreResponse(BaseModel):
    """ATS score calculation response."""

    total_score: int
    keyword_match_score: int
    formatting_score: int
    section_completeness_score: int
    quantified_achievements_score: int
    length_score: int
    contact_info_score: int
    suggestions: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]


# ============================================================================
# Template Schemas
# ============================================================================


class TemplateSchema(BaseModel):
    """Resume template schema."""

    id: str
    name: str
    description: str
    ats_score: int


class TemplateListResponse(BaseModel):
    """List of templates response."""

    templates: list[TemplateSchema]


# ============================================================================
# Profile Picture Schemas
# ============================================================================


class ProfilePictureResponse(BaseModel):
    """Response after uploading a profile picture."""

    url: str
    filename: str