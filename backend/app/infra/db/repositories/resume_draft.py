"""Resume draft repository implementation."""

from dataclasses import asdict
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.resume import (
    Award,
    Certification,
    CustomLink,
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
from app.infra.db.models import ResumeDraftModel


class SQLResumeDraftRepository:
    """SQLAlchemy implementation of ResumeDraftRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, draft_id: str) -> ResumeDraft | None:
        """Get draft by ID."""
        result = await self._session.get(ResumeDraftModel, draft_id)
        return self._to_domain(result) if result else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        include_published: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResumeDraft]:
        """Get all drafts for a user."""
        stmt = select(ResumeDraftModel).where(ResumeDraftModel.user_id == user_id)

        if not include_published:
            stmt = stmt.where(ResumeDraftModel.is_published == False)  # noqa: E712

        stmt = stmt.order_by(ResumeDraftModel.updated_at.desc().nulls_last())
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, draft: ResumeDraft) -> ResumeDraft:
        """Create a new draft."""
        model = ResumeDraftModel(
            id=draft.id,
            user_id=draft.user_id,
            name=draft.name,
            content=self._content_to_dict(draft.content),
            template_id=draft.template_id,
            ats_score=draft.ats_score,
            is_published=draft.is_published,
            created_at=draft.created_at,
            updated_at=draft.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, draft: ResumeDraft) -> ResumeDraft:
        """Update an existing draft (autosave)."""
        model = await self._session.get(ResumeDraftModel, draft.id)
        if model:
            model.name = draft.name
            model.content = self._content_to_dict(draft.content)
            model.template_id = draft.template_id
            model.ats_score = draft.ats_score
            model.is_published = draft.is_published
            model.updated_at = datetime.utcnow()
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Resume draft {draft.id} not found")

    async def delete(self, draft_id: str) -> None:
        """Delete a draft."""
        model = await self._session.get(ResumeDraftModel, draft_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def count_by_user_id(self, user_id: str) -> int:
        """Count drafts for a user."""
        stmt = select(func.count()).select_from(ResumeDraftModel).where(
            ResumeDraftModel.user_id == user_id,
            ResumeDraftModel.is_published == False,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    def _to_domain(self, model: ResumeDraftModel) -> ResumeDraft:
        """Convert ORM model to domain entity."""
        content = self._dict_to_content(model.content)
        return ResumeDraft(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            content=content,
            template_id=model.template_id,
            ats_score=model.ats_score,
            is_published=model.is_published,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _content_to_dict(self, content: ResumeContent) -> dict:
        """Convert ResumeContent to dict for JSON storage."""
        return {
            "full_name": content.full_name,
            "email": content.email,
            "phone": content.phone,
            "location": content.location,
            "linkedin_url": content.linkedin_url,
            "portfolio_url": content.portfolio_url,
            "github_url": content.github_url,
            "profile_picture_url": content.profile_picture_url,
            "custom_links": [
                {"id": cl.id, "label": cl.label, "url": cl.url}
                for cl in content.custom_links
            ],
            "professional_summary": content.professional_summary,
            "work_experience": [
                {
                    "company": w.company,
                    "title": w.title,
                    "start_date": w.start_date,
                    "end_date": w.end_date,
                    "description": w.description,
                    "achievements": w.achievements,
                    "location": w.location,
                    "is_current": w.is_current,
                }
                for w in content.work_experience
            ],
            "education": [
                {
                    "institution": e.institution,
                    "degree": e.degree,
                    "field_of_study": e.field_of_study,
                    "graduation_date": e.graduation_date,
                    "gpa": e.gpa,
                    "location": e.location,
                    "achievements": e.achievements,
                }
                for e in content.education
            ],
            "skills": {
                "technical": content.skills.technical,
                "soft": content.skills.soft,
                "tools": content.skills.tools,
            },
            "projects": [
                {
                    "name": p.name,
                    "description": p.description,
                    "url": p.url,
                    "technologies": p.technologies,
                    "start_date": p.start_date,
                    "end_date": p.end_date,
                    "highlights": p.highlights,
                }
                for p in content.projects
            ],
            "certifications": [
                {
                    "name": c.name,
                    "issuer": c.issuer,
                    "date": c.date,
                    "expiry_date": c.expiry_date,
                    "credential_id": c.credential_id,
                    "url": c.url,
                }
                for c in content.certifications
            ],
            "awards": [
                {
                    "title": a.title,
                    "issuer": a.issuer,
                    "date": a.date,
                    "description": a.description,
                }
                for a in content.awards
            ],
            "languages": [
                {
                    "language": lang.language,
                    "proficiency": lang.proficiency.value,
                }
                for lang in content.languages
            ],
            "custom_sections": [
                {
                    "id": cs.id,
                    "title": cs.title,
                    "items": cs.items,
                }
                for cs in content.custom_sections
            ],
            "template_id": content.template_id,
            "section_order": content.section_order,
            "ats_score": content.ats_score,
        }

    def _dict_to_content(self, data: dict) -> ResumeContent:
        """Convert dict from JSON storage to ResumeContent."""
        # Parse work experience
        work_experience = [
            WorkExperience(
                company=w.get("company", ""),
                title=w.get("title", ""),
                start_date=w.get("start_date"),
                end_date=w.get("end_date"),
                description=w.get("description"),
                achievements=w.get("achievements", []),
                location=w.get("location"),
                is_current=w.get("is_current", False),
            )
            for w in data.get("work_experience", [])
        ]

        # Parse education
        education = [
            Education(
                institution=e.get("institution", ""),
                degree=e.get("degree", ""),
                field_of_study=e.get("field_of_study"),
                graduation_date=e.get("graduation_date"),
                gpa=e.get("gpa"),
                location=e.get("location"),
                achievements=e.get("achievements", []),
            )
            for e in data.get("education", [])
        ]

        # Parse skills
        skills_data = data.get("skills", {})
        skills = SkillsSection(
            technical=skills_data.get("technical", []),
            soft=skills_data.get("soft", []),
            tools=skills_data.get("tools", []),
        )

        # Parse projects
        projects = [
            Project(
                name=p.get("name", ""),
                description=p.get("description", ""),
                url=p.get("url"),
                technologies=p.get("technologies", []),
                start_date=p.get("start_date"),
                end_date=p.get("end_date"),
                highlights=p.get("highlights", []),
            )
            for p in data.get("projects", [])
        ]

        # Parse certifications
        certifications = [
            Certification(
                name=c.get("name", ""),
                issuer=c.get("issuer", ""),
                date=c.get("date"),
                expiry_date=c.get("expiry_date"),
                credential_id=c.get("credential_id"),
                url=c.get("url"),
            )
            for c in data.get("certifications", [])
        ]

        # Parse awards
        awards = [
            Award(
                title=a.get("title", ""),
                issuer=a.get("issuer", ""),
                date=a.get("date"),
                description=a.get("description"),
            )
            for a in data.get("awards", [])
        ]

        # Parse languages
        languages = [
            LanguageSkill(
                language=lang.get("language", ""),
                proficiency=LanguageProficiency(lang.get("proficiency", "conversational")),
            )
            for lang in data.get("languages", [])
        ]

        # Parse custom sections
        custom_sections = [
            CustomSection(
                id=cs.get("id", ""),
                title=cs.get("title", ""),
                items=cs.get("items", []),
            )
            for cs in data.get("custom_sections", [])
        ]

        # Parse custom links
        custom_links = [
            CustomLink(
                id=cl.get("id", ""),
                label=cl.get("label", ""),
                url=cl.get("url", ""),
            )
            for cl in data.get("custom_links", [])
        ]

        return ResumeContent(
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone"),
            location=data.get("location"),
            linkedin_url=data.get("linkedin_url"),
            portfolio_url=data.get("portfolio_url"),
            github_url=data.get("github_url"),
            profile_picture_url=data.get("profile_picture_url"),
            custom_links=custom_links,
            professional_summary=data.get("professional_summary"),
            work_experience=work_experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            awards=awards,
            languages=languages,
            custom_sections=custom_sections,
            template_id=data.get("template_id", "professional-modern"),
            section_order=data.get("section_order", []),
            ats_score=data.get("ats_score"),
        )
