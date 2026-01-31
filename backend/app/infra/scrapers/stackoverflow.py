"""Stack Overflow Jobs scraper.

Standards: python_clean.mdc
- Async HTTP client
- Rate limiting
- Proper error handling

Note: Stack Overflow Jobs was discontinued in 2022, but this serves as a
template for similar job board APIs.
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.job import Job, JobRequirements, JobSource
from app.infra.scrapers.base import BaseJobScraper, SearchFilters

logger = structlog.get_logger(__name__)


class StackOverflowAdapter(BaseJobScraper):
    """Stack Overflow Jobs scraper adapter.

    Note: Stack Overflow shut down their jobs platform in 2022.
    This implementation serves as a template and could be adapted
    for similar job board APIs (e.g., Stack Overflow Talent).
    """

    # Alternative: Use similar APIs
    BASE_URL = "https://api.stackexchange.com/2.3"

    @property
    def name(self) -> str:
        return "stackoverflow"

    async def search(
        self,
        *,
        filters: SearchFilters,
        limit: int = 50,
    ) -> list[Job]:
        """Search for jobs.

        Since Stack Overflow Jobs is discontinued, this returns an empty list.
        In a real implementation, this would:
        1. Build query parameters from filters
        2. Make API request
        3. Parse response into Job objects
        """
        logger.info(
            "stackoverflow_search",
            query=filters.query,
            location=filters.location,
            limit=limit,
        )

        # Stack Overflow Jobs is discontinued
        # Return empty list - this adapter serves as a template
        return []

    async def health_check(self) -> bool:
        """Check if Stack Overflow API is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.BASE_URL}/info")
                return response.status_code == 200
        except Exception:
            return False

    def _parse_job(self, data: dict) -> Job:
        """Parse API response into Job domain model.

        Template method for parsing job data.
        """
        return Job(
            id=str(uuid.uuid4()),
            external_id=f"stackoverflow_{data.get('id', '')}",
            title=data.get("title", ""),
            company=data.get("company", {}).get("name", ""),
            location=data.get("location", "Remote"),
            description=data.get("description", ""),
            url=data.get("url", ""),
            source=JobSource.OTHER,
            salary_min=None,
            salary_max=None,
            remote="remote" in data.get("location", "").lower(),
            requirements=JobRequirements(),
            posted_at=datetime.utcnow(),
            ingested_at=datetime.utcnow(),
        )
