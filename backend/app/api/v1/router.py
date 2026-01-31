"""Main API router.

Standards: python_clean.mdc
- Clean separation of endpoint modules
"""

from fastapi import APIRouter

from app.api.v1 import agents, applications, auth, billing, jobs, profile

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
