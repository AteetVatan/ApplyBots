"""News API client for company news.

Standards: python_clean.mdc
- Async HTTP client
- NewsAPI.org free tier (100 requests/day)
"""

from datetime import datetime, timedelta

import httpx
import structlog
from pydantic import SecretStr

from app.core.domain.company_intel import NewsArticle

logger = structlog.get_logger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/everything"


class NewsAPIClient:
    """Client for NewsAPI.org."""

    def __init__(
        self,
        *,
        api_key: SecretStr,
        timeout: float = 10.0,
    ) -> None:
        """Initialize NewsAPI client.

        Args:
            api_key: NewsAPI.org API key
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._timeout = timeout

    async def get_company_news(
        self,
        company_name: str,
        *,
        days: int = 30,
        max_articles: int = 5,
    ) -> list[NewsArticle]:
        """Get recent news about a company.

        Args:
            company_name: Company name to search for
            days: Number of days back to search
            max_articles: Maximum articles to return

        Returns:
            List of NewsArticle
        """
        if not self._api_key.get_secret_value():
            logger.debug("newsapi_key_not_configured")
            return []

        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

            params = {
                "q": f'"{company_name}"',
                "from": from_date,
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": max_articles,
            }

            headers = {
                "X-Api-Key": self._api_key.get_secret_value(),
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    NEWSAPI_URL,
                    params=params,
                    headers=headers,
                )

                if response.status_code == 401:
                    logger.warning("newsapi_invalid_key")
                    return []

                if response.status_code == 429:
                    logger.warning("newsapi_rate_limited")
                    return []

                response.raise_for_status()
                data = response.json()

            articles = []
            for article in data.get("articles", []):
                # Parse published date
                published_at = None
                if article.get("publishedAt"):
                    try:
                        published_at = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                # Simple sentiment analysis based on title
                sentiment = self._analyze_sentiment(
                    article.get("title", ""),
                    article.get("description", ""),
                )

                articles.append(
                    NewsArticle(
                        title=article.get("title", ""),
                        description=article.get("description", ""),
                        url=article.get("url", ""),
                        source=article.get("source", {}).get("name", "Unknown"),
                        published_at=published_at,
                        sentiment=sentiment,
                    )
                )

            logger.debug(
                "newsapi_articles_fetched",
                company=company_name,
                count=len(articles),
            )

            return articles

        except Exception as e:
            logger.warning(
                "newsapi_fetch_failed",
                company=company_name,
                error=str(e),
            )
            return []

    def _analyze_sentiment(self, title: str, description: str) -> str:
        """Simple keyword-based sentiment analysis.

        Args:
            title: Article title
            description: Article description

        Returns:
            "positive", "negative", or "neutral"
        """
        text = f"{title} {description}".lower()

        positive_keywords = [
            "growth", "profit", "success", "expansion", "hire",
            "funding", "raise", "launch", "innovation", "award",
            "milestone", "partnership", "record",
        ]

        negative_keywords = [
            "layoff", "loss", "decline", "cut", "lawsuit",
            "investigation", "scandal", "bankruptcy", "shutdown",
            "downturn", "recession", "struggle", "fail",
        ]

        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)

        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        return "neutral"
