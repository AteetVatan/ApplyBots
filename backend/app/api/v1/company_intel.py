"""Company intelligence API endpoints.

Standards: python_clean.mdc
- FastAPI router
- Dependency injection
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_db_session
from app.config import get_settings
from app.core.services.company_intel import CompanyIntelligenceService
from app.schemas.company_intel import (
    CompanyFinancialsResponse,
    CompanyIntelligenceResponse,
    HiringSignalsResponse,
    NewsArticleResponse,
)

router = APIRouter(prefix="/company", tags=["company-intelligence"])


def _get_company_intel_service() -> CompanyIntelligenceService:
    """Create company intelligence service."""
    settings = get_settings()
    return CompanyIntelligenceService(
        newsapi_key=settings.newsapi_key if hasattr(settings, "newsapi_key") else None,
        redis_client=None,  # Would inject Redis client in production
    )


@router.get("/{company_name}/intelligence", response_model=CompanyIntelligenceResponse)
async def get_company_intelligence(
    company_name: str,
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
    refresh: bool = Query(False, description="Force refresh (bypass cache)"),
):
    """Get comprehensive intelligence about a company.

    Aggregates data from Wikipedia, SEC EDGAR, and news sources.
    """
    service = _get_company_intel_service()

    if refresh:
        intel = await service.refresh_company_data(company_name)
    else:
        intel = await service.get_company_intelligence(company_name)

    # Convert to response
    financials = None
    if intel.financials:
        financials = CompanyFinancialsResponse(
            fiscal_year=intel.financials.fiscal_year,
            revenue=intel.financials.revenue,
            net_income=intel.financials.net_income,
            total_assets=intel.financials.total_assets,
            employees=intel.financials.employees,
            currency=intel.financials.currency,
        )

    return CompanyIntelligenceResponse(
        company_name=intel.company_name,
        domain=intel.domain,
        logo_url=intel.logo_url,
        description=intel.description,
        industry=intel.industry,
        size_range=intel.size_range,
        founded_year=intel.founded_year,
        headquarters=intel.headquarters,
        website=intel.website,
        wikipedia_summary=intel.wikipedia_summary,
        wikipedia_url=intel.wikipedia_url,
        recent_news=[
            NewsArticleResponse(
                title=n.title,
                description=n.description,
                url=n.url,
                source=n.source,
                published_at=n.published_at,
                sentiment=n.sentiment,
            )
            for n in intel.recent_news
        ],
        financials=financials,
        hiring_signals=HiringSignalsResponse(
            active_job_count=intel.hiring_signals.active_job_count,
            hiring_trend=intel.hiring_signals.hiring_trend,
            recent_funding=intel.hiring_signals.recent_funding,
            layoff_news=intel.hiring_signals.layoff_news,
        ),
        data_sources=intel.data_sources,
        confidence_score=intel.confidence_score,
        last_updated=intel.last_updated,
    )
