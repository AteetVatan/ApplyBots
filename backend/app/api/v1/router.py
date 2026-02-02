"""Main API router.

Standards: python_clean.mdc
- Clean separation of endpoint modules
"""

from fastapi import APIRouter

from app.api.v1 import (
    agents,
    alerts,
    analytics,
    applications,
    auth,
    billing,
    campaigns,
    career_kit,
    company_intel,
    gamification,
    jobs,
    profile,
    resume_builder,
    resumes,
    tools,
    wellness,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(resume_builder.router, prefix="/resume-builder", tags=["resume-builder"])
api_router.include_router(tools.router, prefix="/tools", tags=["career-tools"])
api_router.include_router(career_kit.router, prefix="/career-kit", tags=["career-kit"])
api_router.include_router(alerts.router)
api_router.include_router(gamification.router)
api_router.include_router(analytics.router)
api_router.include_router(wellness.router)
api_router.include_router(company_intel.router)