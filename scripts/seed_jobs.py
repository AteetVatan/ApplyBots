#!/usr/bin/env python3
"""Seed database with sample jobs for development.

Usage: python scripts/seed_jobs.py
"""

import asyncio
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.domain.job import Job, JobRequirements, JobSource


SAMPLE_JOBS = [
    {
        "title": "Senior Software Engineer",
        "company": "TechCorp Inc.",
        "location": "San Francisco, CA",
        "remote": True,
        "salary_min": 150000,
        "salary_max": 200000,
        "description": "We're looking for a senior software engineer to join our platform team.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "preferred_skills": ["Kubernetes", "AWS", "React"],
        "experience_min": 5,
    },
    {
        "title": "Full Stack Developer",
        "company": "StartupXYZ",
        "location": "New York, NY",
        "remote": True,
        "salary_min": 120000,
        "salary_max": 160000,
        "description": "Join our fast-growing startup as a full stack developer.",
        "required_skills": ["TypeScript", "React", "Node.js"],
        "preferred_skills": ["Next.js", "PostgreSQL", "Redis"],
        "experience_min": 3,
    },
    {
        "title": "Backend Developer",
        "company": "DataFlow Systems",
        "location": "Austin, TX",
        "remote": True,
        "salary_min": 130000,
        "salary_max": 170000,
        "description": "Build scalable backend systems for our data platform.",
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "preferred_skills": ["Redis", "Celery", "Docker"],
        "experience_min": 4,
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudNative Co.",
        "location": "Seattle, WA",
        "remote": True,
        "salary_min": 140000,
        "salary_max": 180000,
        "description": "Manage our cloud infrastructure and CI/CD pipelines.",
        "required_skills": ["AWS", "Kubernetes", "Terraform"],
        "preferred_skills": ["Python", "Go", "Prometheus"],
        "experience_min": 4,
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Labs",
        "location": "Boston, MA",
        "remote": True,
        "salary_min": 160000,
        "salary_max": 220000,
        "description": "Develop and deploy ML models at scale.",
        "required_skills": ["Python", "PyTorch", "scikit-learn"],
        "preferred_skills": ["MLOps", "Kubernetes", "AWS SageMaker"],
        "experience_min": 5,
    },
    {
        "title": "Frontend Developer",
        "company": "DesignFirst",
        "location": "Los Angeles, CA",
        "remote": False,
        "salary_min": 110000,
        "salary_max": 150000,
        "description": "Create beautiful user interfaces for our design platform.",
        "required_skills": ["React", "TypeScript", "CSS"],
        "preferred_skills": ["Next.js", "Tailwind", "Figma"],
        "experience_min": 3,
    },
    {
        "title": "Site Reliability Engineer",
        "company": "Reliability Inc.",
        "location": "Chicago, IL",
        "remote": True,
        "salary_min": 145000,
        "salary_max": 190000,
        "description": "Ensure 99.99% uptime for our critical systems.",
        "required_skills": ["Linux", "Python", "Kubernetes"],
        "preferred_skills": ["Go", "Prometheus", "Grafana"],
        "experience_min": 5,
    },
    {
        "title": "Data Engineer",
        "company": "BigData Corp",
        "location": "Denver, CO",
        "remote": True,
        "salary_min": 135000,
        "salary_max": 175000,
        "description": "Build data pipelines for our analytics platform.",
        "required_skills": ["Python", "Apache Spark", "SQL"],
        "preferred_skills": ["Airflow", "Databricks", "AWS"],
        "experience_min": 4,
    },
]


async def seed_jobs():
    """Seed the database with sample jobs."""
    from sqlalchemy.exc import ProgrammingError

    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.session import async_session_factory

    try:
        async with async_session_factory() as session:
            job_repo = SQLJobRepository(session=session)

            for i, job_data in enumerate(SAMPLE_JOBS):
                job = Job(
                    id=str(uuid.uuid4()),
                    external_id=f"seed_{i}_{uuid.uuid4().hex[:8]}",
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    remote=job_data["remote"],
                    description=job_data["description"],
                    url=f"https://careers.example.com/job/{i}",
                    source=JobSource.MANUAL,
                    salary_min=job_data["salary_min"],
                    salary_max=job_data["salary_max"],
                    requirements=JobRequirements(
                        required_skills=job_data["required_skills"],
                        preferred_skills=job_data.get("preferred_skills", []),
                        experience_years_min=job_data.get("experience_min"),
                    ),
                    posted_at=(datetime.now(UTC) - timedelta(days=i)).replace(tzinfo=None),
                    ingested_at=datetime.now(UTC).replace(tzinfo=None),
                )

                await job_repo.upsert(job)
                print(f"[OK] Created job: {job.title} at {job.company}")

            await session.commit()

        print(f"\n[SUCCESS] Seeded {len(SAMPLE_JOBS)} jobs successfully!")
    except ProgrammingError as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "UndefinedTableError" in error_msg:
            print("\n[ERROR] Database tables do not exist!")
            print("\n[TIP] Solution: Run database migrations first:")
            print("   cd backend")
            print("   alembic upgrade head")
            print("   cd ..")
            print("   python scripts/seed_jobs.py")
            sys.exit(1)
        raise


if __name__ == "__main__":
    asyncio.run(seed_jobs())
