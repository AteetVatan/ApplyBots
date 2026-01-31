"""Company intelligence domain model.

Standards: python_clean.mdc
- Dataclass for domain models
- Clear data structures for API responses
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsArticle:
    """News article about a company."""

    title: str
    description: str
    url: str
    source: str
    published_at: datetime | None = None
    sentiment: str | None = None  # "positive", "negative", "neutral"


@dataclass
class CompanyFinancials:
    """Company financial data from SEC EDGAR."""

    fiscal_year: int
    revenue: float | None = None
    net_income: float | None = None
    total_assets: float | None = None
    employees: int | None = None
    currency: str = "USD"


@dataclass
class HiringSignals:
    """Signals about company's hiring activity."""

    active_job_count: int = 0
    hiring_trend: str = "stable"  # "growing", "stable", "declining"
    recent_funding: bool = False
    layoff_news: bool = False


@dataclass
class CompanyIntelligence:
    """Complete company intelligence data."""

    company_name: str
    domain: str | None = None
    logo_url: str | None = None
    description: str | None = None
    industry: str | None = None
    size_range: str | None = None  # "1-10", "11-50", "51-200", etc.
    founded_year: int | None = None
    headquarters: str | None = None
    website: str | None = None
    linkedin_url: str | None = None

    # External data
    recent_news: list[NewsArticle] = field(default_factory=list)
    financials: CompanyFinancials | None = None
    hiring_signals: HiringSignals = field(default_factory=HiringSignals)

    # Wikipedia data
    wikipedia_summary: str | None = None
    wikipedia_url: str | None = None

    # Metadata
    data_sources: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    confidence_score: int = 0  # 0-100 based on data quality


# Size range definitions
SIZE_RANGES = [
    "1-10",
    "11-50",
    "51-200",
    "201-500",
    "501-1000",
    "1001-5000",
    "5001-10000",
    "10000+",
]
