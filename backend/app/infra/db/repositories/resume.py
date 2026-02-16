"""Resume repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.resume import Education, ParsedResume, Resume, WorkExperience
from app.infra.db.models import ResumeModel


class SQLResumeRepository:
    """SQLAlchemy implementation of ResumeRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, resume_id: str) -> Resume | None:
        """Get resume by ID."""
        result = await self._session.get(ResumeModel, resume_id)
        return self._to_domain(result) if result else None

    async def get_by_user_id(self, user_id: str) -> list[Resume]:
        """Get all resumes for a user."""
        stmt = select(ResumeModel).where(ResumeModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_primary(self, *, user_id: str) -> Resume | None:
        """Get primary resume for a user."""
        stmt = select(ResumeModel).where(
            ResumeModel.user_id == user_id,
            ResumeModel.is_primary == True,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, resume: Resume) -> Resume:
        """Create a new resume."""
        model = ResumeModel(
            id=resume.id,
            user_id=resume.user_id,
            filename=resume.filename,
            s3_key=resume.s3_key,
            raw_text=resume.raw_text,
            parsed_data=self._parsed_to_dict(resume.parsed_data) if resume.parsed_data else None,
            embedding=resume.embedding,
            is_primary=resume.is_primary,
            extraction_error=resume.extraction_error,
            created_at=resume.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, resume: Resume) -> Resume:
        """Update an existing resume."""
        model = await self._session.get(ResumeModel, resume.id)
        if model:
            model.filename = resume.filename
            model.s3_key = resume.s3_key
            model.raw_text = resume.raw_text
            model.parsed_data = self._parsed_to_dict(resume.parsed_data) if resume.parsed_data else None
            model.embedding = resume.embedding
            model.is_primary = resume.is_primary
            model.extraction_error = resume.extraction_error
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Resume {resume.id} not found")

    async def delete(self, resume_id: str) -> None:
        """Delete a resume."""
        model = await self._session.get(ResumeModel, resume_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: ResumeModel) -> Resume:
        """Convert ORM model to domain entity."""
        parsed_data = None
        if model.parsed_data:
            data = model.parsed_data
            work_exp = [
                WorkExperience(
                    company=w.get("company", ""),
                    title=w.get("title", ""),
                    start_date=w.get("start_date"),
                    end_date=w.get("end_date"),
                    description=w.get("description"),
                    achievements=w.get("achievements", []),
                )
                for w in data.get("work_experience", [])
            ]
            education = [
                Education(
                    school=e.get("school") or e.get("institution", ""),
                    institution=e.get("institution") or e.get("school", ""),
                    degree=e.get("degree", ""),
                    area=e.get("area") or e.get("field_of_study", ""),
                    field_of_study=e.get("field_of_study") or e.get("area"),
                    grade=e.get("grade") or (str(e.get("gpa", "")) if e.get("gpa") else ""),
                    gpa=e.get("gpa") or (e.get("grade") if e.get("grade") else None),
                    location=e.get("location", ""),
                    period=e.get("period") or e.get("graduation_date", ""),
                    graduation_date=e.get("graduation_date") or e.get("period"),
                )
                for e in data.get("education", [])
            ]
            parsed_data = ParsedResume(
                full_name=data.get("full_name"),
                email=data.get("email"),
                phone=data.get("phone"),
                location=data.get("location"),
                summary=data.get("summary"),
                skills=data.get("skills", []),
                work_experience=work_exp,
                education=education,
                certifications=data.get("certifications", []),
                languages=data.get("languages", []),
                total_years_experience=data.get("total_years_experience"),
            )

        return Resume(
            id=model.id,
            user_id=model.user_id,
            filename=model.filename,
            s3_key=model.s3_key,
            raw_text=model.raw_text,
            parsed_data=parsed_data,
            embedding=model.embedding,
            is_primary=model.is_primary,
            extraction_error=model.extraction_error,
            created_at=model.created_at,
        )

    def _parsed_to_dict(self, parsed: ParsedResume) -> dict:
        """Convert ParsedResume to dict for JSON storage."""
        return {
            "full_name": parsed.full_name,
            "email": parsed.email,
            "phone": parsed.phone,
            "location": parsed.location,
            "summary": parsed.summary,
            "skills": parsed.skills,
            "work_experience": [
                {
                    "company": w.company,
                    "title": w.title,
                    "start_date": w.start_date,
                    "end_date": w.end_date,
                    "description": w.description,
                    "achievements": w.achievements,
                }
                for w in parsed.work_experience
            ],
            "education": [
                {
                    "school": e.school or e.institution,
                    "institution": e.institution or e.school,
                    "degree": e.degree,
                    "area": e.area or (e.field_of_study or ""),
                    "field_of_study": e.field_of_study or e.area,
                    "grade": e.grade or (str(e.gpa) if e.gpa else ""),
                    "gpa": e.gpa or (e.grade if e.grade else None),
                    "location": e.location,
                    "period": e.period or (e.graduation_date or ""),
                    "graduation_date": e.graduation_date or e.period,
                }
                for e in parsed.education
            ],
            "certifications": parsed.certifications,
            "languages": parsed.languages,
            "total_years_experience": parsed.total_years_experience,
        }
