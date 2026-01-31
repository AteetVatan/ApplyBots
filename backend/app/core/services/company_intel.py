"""Company intelligence service.

Standards: python_clean.mdc
- Aggregates data from multiple free APIs
- Redis caching for performance
"""

from datetime import datetime, timedelta

import structlog
from pydantic import SecretStr

from app.core.domain.company_intel import (
    CompanyIntelligence,
    HiringSignals,
    NewsArticle,
)

logger = structlog.get_logger(__name__)

# Cache TTL in seconds (24 hours)
CACHE_TTL = 86400


class CompanyIntelligenceService:
    """Service for aggregating company intelligence from free APIs."""

    def __init__(
        self,
        *,
        newsapi_key: SecretStr | None = None,
        redis_client=None,
    ) -> None:
        """Initialize company intelligence service.

        Args:
            newsapi_key: Optional NewsAPI.org API key
            redis_client: Optional Redis client for caching
        """
        self._newsapi_key = newsapi_key or SecretStr("")
        self._redis = redis_client

    async def get_company_intelligence(
        self,
        company_name: str,
        *,
        use_cache: bool = True,
    ) -> CompanyIntelligence:
        """Get comprehensive company intelligence.

        Aggregates data from Wikipedia, SEC EDGAR, and NewsAPI.

        Args:
            company_name: Company name to research
            use_cache: Whether to use cached data

        Returns:
            CompanyIntelligence with all available data
        """
        # Check cache first
        if use_cache and self._redis:
            cached = await self._get_from_cache(company_name)
            if cached:
                logger.debug("company_intel_cache_hit", company=company_name)
                return cached

        # Initialize result
        result = CompanyIntelligence(
            company_name=company_name,
            data_sources=[],
        )

        # Fetch from all sources in parallel
        import asyncio

        wiki_task = self._fetch_wikipedia(company_name)
        sec_task = self._fetch_sec_edgar(company_name)
        news_task = self._fetch_news(company_name)

        wiki_result, sec_result, news_result = await asyncio.gather(
            wiki_task,
            sec_task,
            news_task,
            return_exceptions=True,
        )

        # Process Wikipedia results
        if not isinstance(wiki_result, Exception) and wiki_result:
            result.description = wiki_result.get("summary")
            result.wikipedia_summary = wiki_result.get("extract")
            result.wikipedia_url = wiki_result.get("url")
            result.data_sources.append("wikipedia")

        # Process SEC EDGAR results
        if not isinstance(sec_result, Exception) and sec_result:
            result.financials = sec_result
            result.data_sources.append("sec_edgar")

        # Process news results
        if not isinstance(news_result, Exception) and news_result:
            result.recent_news = news_result
            result.hiring_signals = self._analyze_news_for_signals(news_result)
            result.data_sources.append("newsapi")

        # Get logo URL
        from app.infra.company_intel.clearbit_client import ClearbitLogoClient
        logo_client = ClearbitLogoClient()
        result.logo_url = logo_client.get_logo_url_from_company_name(company_name)

        # Calculate confidence score
        result.confidence_score = self._calculate_confidence(result)
        result.last_updated = datetime.utcnow()

        # Cache the result
        if self._redis:
            await self._save_to_cache(company_name, result)

        logger.info(
            "company_intel_fetched",
            company=company_name,
            sources=result.data_sources,
            confidence=result.confidence_score,
        )

        return result

    async def refresh_company_data(self, company_name: str) -> CompanyIntelligence:
        """Force refresh of company data (bypass cache).

        Args:
            company_name: Company name

        Returns:
            Fresh CompanyIntelligence
        """
        # Clear cache
        if self._redis:
            cache_key = self._get_cache_key(company_name)
            await self._redis.delete(cache_key)

        return await self.get_company_intelligence(company_name, use_cache=False)

    async def _fetch_wikipedia(self, company_name: str) -> dict | None:
        """Fetch data from Wikipedia."""
        try:
            from app.infra.company_intel.wikipedia_client import WikipediaClient

            client = WikipediaClient()
            result = await client.get_company_summary(company_name)

            if result:
                return {
                    "summary": result.summary,
                    "extract": result.extract,
                    "url": result.url,
                }
            return None

        except Exception as e:
            logger.warning("wikipedia_fetch_error", company=company_name, error=str(e))
            return None

    async def _fetch_sec_edgar(self, company_name: str):
        """Fetch data from SEC EDGAR."""
        try:
            from app.infra.company_intel.sec_edgar_client import SECEdgarClient

            client = SECEdgarClient()
            return await client.get_company_financials(company_name)

        except Exception as e:
            logger.warning("sec_edgar_fetch_error", company=company_name, error=str(e))
            return None

    async def _fetch_news(self, company_name: str) -> list[NewsArticle]:
        """Fetch news from NewsAPI."""
        try:
            from app.infra.company_intel.news_client import NewsAPIClient

            client = NewsAPIClient(api_key=self._newsapi_key)
            return await client.get_company_news(company_name)

        except Exception as e:
            logger.warning("news_fetch_error", company=company_name, error=str(e))
            return []

    def _analyze_news_for_signals(
        self,
        articles: list[NewsArticle],
    ) -> HiringSignals:
        """Analyze news articles for hiring signals.

        Args:
            articles: List of news articles

        Returns:
            HiringSignals based on news analysis
        """
        signals = HiringSignals()

        if not articles:
            return signals

        # Analyze article content
        positive_hiring_keywords = ["hiring", "expansion", "growth", "funding", "raise"]
        negative_keywords = ["layoff", "layoffs", "cut", "downsizing", "restructuring"]

        positive_count = 0
        negative_count = 0

        for article in articles:
            text = f"{article.title} {article.description}".lower()

            for kw in positive_hiring_keywords:
                if kw in text:
                    positive_count += 1
                    if "funding" in text or "raise" in text:
                        signals.recent_funding = True

            for kw in negative_keywords:
                if kw in text:
                    negative_count += 1
                    signals.layoff_news = True

        # Determine hiring trend
        if positive_count > negative_count + 2:
            signals.hiring_trend = "growing"
        elif negative_count > positive_count + 2:
            signals.hiring_trend = "declining"
        else:
            signals.hiring_trend = "stable"

        return signals

    def _calculate_confidence(self, intel: CompanyIntelligence) -> int:
        """Calculate confidence score based on data quality.

        Args:
            intel: Company intelligence data

        Returns:
            Confidence score 0-100
        """
        score = 0

        # Wikipedia data (+30)
        if intel.wikipedia_summary:
            score += 30
        elif intel.description:
            score += 15

        # SEC data (+30)
        if intel.financials:
            score += 30

        # News data (+20)
        if intel.recent_news:
            score += min(20, len(intel.recent_news) * 4)

        # Logo (+10)
        if intel.logo_url:
            score += 10

        # Multiple sources bonus (+10)
        if len(intel.data_sources) >= 2:
            score += 10

        return min(100, score)

    def _get_cache_key(self, company_name: str) -> str:
        """Generate cache key for company."""
        # Normalize company name
        normalized = company_name.lower().strip().replace(" ", "_")
        return f"company_intel:{normalized}"

    async def _get_from_cache(
        self,
        company_name: str,
    ) -> CompanyIntelligence | None:
        """Get company intel from cache."""
        if not self._redis:
            return None

        try:
            import json

            cache_key = self._get_cache_key(company_name)
            data = await self._redis.get(cache_key)

            if not data:
                return None

            # Deserialize
            cached_dict = json.loads(data)
            return self._dict_to_intel(cached_dict)

        except Exception as e:
            logger.warning("cache_get_error", company=company_name, error=str(e))
            return None

    async def _save_to_cache(
        self,
        company_name: str,
        intel: CompanyIntelligence,
    ) -> None:
        """Save company intel to cache."""
        if not self._redis:
            return

        try:
            import json

            cache_key = self._get_cache_key(company_name)
            data = self._intel_to_dict(intel)
            await self._redis.setex(cache_key, CACHE_TTL, json.dumps(data))

        except Exception as e:
            logger.warning("cache_save_error", company=company_name, error=str(e))

    def _intel_to_dict(self, intel: CompanyIntelligence) -> dict:
        """Convert CompanyIntelligence to dict for caching."""
        return {
            "company_name": intel.company_name,
            "domain": intel.domain,
            "logo_url": intel.logo_url,
            "description": intel.description,
            "industry": intel.industry,
            "size_range": intel.size_range,
            "founded_year": intel.founded_year,
            "headquarters": intel.headquarters,
            "website": intel.website,
            "wikipedia_summary": intel.wikipedia_summary,
            "wikipedia_url": intel.wikipedia_url,
            "data_sources": intel.data_sources,
            "confidence_score": intel.confidence_score,
            "last_updated": intel.last_updated.isoformat(),
            "recent_news": [
                {
                    "title": n.title,
                    "description": n.description,
                    "url": n.url,
                    "source": n.source,
                    "published_at": n.published_at.isoformat() if n.published_at else None,
                    "sentiment": n.sentiment,
                }
                for n in intel.recent_news
            ],
            "financials": (
                {
                    "fiscal_year": intel.financials.fiscal_year,
                    "revenue": intel.financials.revenue,
                    "net_income": intel.financials.net_income,
                    "total_assets": intel.financials.total_assets,
                    "employees": intel.financials.employees,
                    "currency": intel.financials.currency,
                }
                if intel.financials
                else None
            ),
            "hiring_signals": {
                "active_job_count": intel.hiring_signals.active_job_count,
                "hiring_trend": intel.hiring_signals.hiring_trend,
                "recent_funding": intel.hiring_signals.recent_funding,
                "layoff_news": intel.hiring_signals.layoff_news,
            },
        }

    def _dict_to_intel(self, data: dict) -> CompanyIntelligence:
        """Convert dict to CompanyIntelligence."""
        from app.core.domain.company_intel import CompanyFinancials

        financials = None
        if data.get("financials"):
            f = data["financials"]
            financials = CompanyFinancials(
                fiscal_year=f["fiscal_year"],
                revenue=f.get("revenue"),
                net_income=f.get("net_income"),
                total_assets=f.get("total_assets"),
                employees=f.get("employees"),
                currency=f.get("currency", "USD"),
            )

        news = []
        for n in data.get("recent_news", []):
            published_at = None
            if n.get("published_at"):
                published_at = datetime.fromisoformat(n["published_at"])
            news.append(
                NewsArticle(
                    title=n["title"],
                    description=n["description"],
                    url=n["url"],
                    source=n["source"],
                    published_at=published_at,
                    sentiment=n.get("sentiment"),
                )
            )

        hs = data.get("hiring_signals", {})
        hiring_signals = HiringSignals(
            active_job_count=hs.get("active_job_count", 0),
            hiring_trend=hs.get("hiring_trend", "stable"),
            recent_funding=hs.get("recent_funding", False),
            layoff_news=hs.get("layoff_news", False),
        )

        return CompanyIntelligence(
            company_name=data["company_name"],
            domain=data.get("domain"),
            logo_url=data.get("logo_url"),
            description=data.get("description"),
            industry=data.get("industry"),
            size_range=data.get("size_range"),
            founded_year=data.get("founded_year"),
            headquarters=data.get("headquarters"),
            website=data.get("website"),
            wikipedia_summary=data.get("wikipedia_summary"),
            wikipedia_url=data.get("wikipedia_url"),
            recent_news=news,
            financials=financials,
            hiring_signals=hiring_signals,
            data_sources=data.get("data_sources", []),
            confidence_score=data.get("confidence_score", 0),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )
