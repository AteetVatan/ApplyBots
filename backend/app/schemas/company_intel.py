"""Company intelligence API schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime

from pydantic import BaseModel, Field


class NewsArticleResponse(BaseModel):
    """News article response."""

    title: str
    description: str
    url: str
    source: str
    published_at: datetime | None
    sentiment: str | None


class CompanyFinancialsResponse(BaseModel):
    """Company financials response."""

    fiscal_year: int
    revenue: float | None
    net_income: float | None
    total_assets: float | None
    employees: int | None
    currency: str = "USD"


class HiringSignalsResponse(BaseModel):
    """Hiring signals response."""

    active_job_count: int
    hiring_trend: str
    recent_funding: bool
    layoff_news: bool


class CompanyIntelligenceResponse(BaseModel):
    """Complete company intelligence response."""

    company_name: str
    domain: str | None
    logo_url: str | None
    description: str | None
    industry: str | None
    size_range: str | None
    founded_year: int | None
    headquarters: str | None
    website: str | None

    # Wikipedia data
    wikipedia_summary: str | None
    wikipedia_url: str | None

    # External data
    recent_news: list[NewsArticleResponse]
    financials: CompanyFinancialsResponse | None
    hiring_signals: HiringSignalsResponse

    # Metadata
    data_sources: list[str]
    confidence_score: int = Field(ge=0, le=100)
    last_updated: datetime
