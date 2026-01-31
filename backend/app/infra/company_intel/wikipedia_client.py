"""Wikipedia API client for company information.

Standards: python_clean.mdc
- Async HTTP client
- Free API, no auth required
"""

from dataclasses import dataclass

import httpx
import structlog

logger = structlog.get_logger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1"
WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"


@dataclass
class WikipediaResult:
    """Wikipedia search result."""

    title: str
    summary: str
    url: str
    extract: str | None = None


class WikipediaClient:
    """Client for Wikipedia API."""

    def __init__(self, *, timeout: float = 10.0) -> None:
        self._timeout = timeout

    async def get_company_summary(self, company_name: str) -> WikipediaResult | None:
        """Get Wikipedia summary for a company.

        Args:
            company_name: Company name to search for

        Returns:
            WikipediaResult or None if not found
        """
        try:
            # First search for the company
            page_title = await self._search_company(company_name)
            if not page_title:
                return None

            # Get the page summary
            return await self._get_page_summary(page_title)

        except Exception as e:
            logger.warning(
                "wikipedia_lookup_failed",
                company=company_name,
                error=str(e),
            )
            return None

    async def _search_company(self, company_name: str) -> str | None:
        """Search Wikipedia for company page.

        Args:
            company_name: Company name

        Returns:
            Page title or None
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{company_name} company",
            "format": "json",
            "srlimit": 5,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(WIKIPEDIA_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

        search_results = data.get("query", {}).get("search", [])

        if not search_results:
            return None

        # Find best match - prefer exact company name matches
        company_lower = company_name.lower()
        for result in search_results:
            title_lower = result["title"].lower()
            if company_lower in title_lower:
                return result["title"]

        # Return first result as fallback
        return search_results[0]["title"]

    async def _get_page_summary(self, page_title: str) -> WikipediaResult | None:
        """Get Wikipedia page summary.

        Args:
            page_title: Wikipedia page title

        Returns:
            WikipediaResult with summary
        """
        # URL encode the title
        encoded_title = page_title.replace(" ", "_")
        url = f"{WIKIPEDIA_API_URL}/page/summary/{encoded_title}"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

        return WikipediaResult(
            title=data.get("title", page_title),
            summary=data.get("description", ""),
            url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            extract=data.get("extract", ""),
        )
