"""The Muse job aggregator scraper.

Standards: python_clean.mdc
- Async HTTP client
- REST API with curated tech jobs
- High-quality job listings with company profiles
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.job import Job, JobRequirements, JobSource
from app.infra.scrapers.base import BaseJobScraper, SearchFilters

logger = structlog.get_logger(__name__)

# The Muse job categories
JOB_CATEGORIES = {
    "software": "Software Engineering",
    "data": "Data Science",
    "design": "Design",
    "product": "Product",
    "marketing": "Marketing",
    "finance": "Finance & Accounting",
    "hr": "Human Resources",
    "operations": "Operations",
    "sales": "Sales",
    "customer": "Customer Service",
}

# Experience levels
EXPERIENCE_LEVELS = {
    "junior": "Entry Level",
    "entry": "Entry Level",
    "mid": "Mid Level",
    "senior": "Senior Level",
    "manager": "Management",
    "executive": "Executive",
}


class TheMuseAdapter(BaseJobScraper):
    """The Muse job aggregator adapter.

    Provides curated tech jobs with detailed company profiles.
    API docs: https://www.themuse.com/developers/api/v2
    """

    BASE_URL = "https://www.themuse.com/api/public/jobs"

    def __init__(
        self,
        *,
        api_key: str | None = None,
    ) -> None:
        """Initialize The Muse adapter.

        Args:
            api_key: The Muse API key (optional for public API)
        """
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "themuse"

    async def search(
        self,
        *,
        filters: SearchFilters,
        limit: int = 50,
        category: str | None = None,
    ) -> list[Job]:
        """Search for jobs on The Muse.

        Args:
            filters: Search filter criteria
            limit: Maximum number of results
            category: Job category (e.g., 'Software Engineering')

        Returns:
            List of matching jobs
        """
        logger.info(
            "themuse_search",
            query=filters.query,
            location=filters.location,
            category=category,
            limit=limit,
        )

        jobs: list[Job] = []

        try:
            # Calculate pages needed (The Muse returns 20 per page)
            page_size = 20
            pages_needed = (limit + page_size - 1) // page_size

            for page in range(pages_needed):
                params: dict[str, str | int] = {
                    "page": page,
                }

                # Add category filter
                if category:
                    params["category"] = category
                elif filters.query:
                    # Map query to category
                    resolved_category = self._resolve_category(filters.query)
                    if resolved_category:
                        params["category"] = resolved_category

                # Add location filter
                if filters.location:
                    params["location"] = filters.location

                # Add experience level
                if filters.experience_level:
                    level = EXPERIENCE_LEVELS.get(
                        filters.experience_level.lower(),
                        filters.experience_level,
                    )
                    params["level"] = level

                # Add API key if available
                if self._api_key:
                    params["api_key"] = self._api_key

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(self.BASE_URL, params=params)

                    if response.status_code != 200:
                        logger.warning(
                            "themuse_search_failed",
                            status_code=response.status_code,
                            page=page,
                        )
                        break

                    data = response.json()
                    results = data.get("results", [])

                    if not results:
                        break

                    for job_data in results:
                        if len(jobs) >= limit:
                            break
                        try:
                            job = self._parse_job(job_data)
                            jobs.append(job)
                        except Exception as e:
                            logger.warning(
                                "themuse_parse_error",
                                error=str(e),
                                job_id=job_data.get("id"),
                            )

                    if len(jobs) >= limit:
                        break

        except httpx.TimeoutException:
            logger.warning("themuse_timeout")
        except Exception as e:
            logger.error("themuse_search_error", error=str(e))

        logger.info("themuse_search_complete", job_count=len(jobs))
        return jobs[:limit]

    async def search_by_category(
        self,
        *,
        category: str,
        location: str | None = None,
        limit: int = 50,
    ) -> list[Job]:
        """Search for jobs by specific category.

        Args:
            category: Job category (e.g., 'Software Engineering')
            location: Optional location filter
            limit: Maximum number of results

        Returns:
            List of matching jobs
        """
        filters = SearchFilters(
            location=location,
        )
        return await self.search(
            filters=filters,
            limit=limit,
            category=category,
        )

    async def health_check(self) -> bool:
        """Check if The Muse API is accessible."""
        try:
            params: dict[str, str | int] = {"page": 0}
            if self._api_key:
                params["api_key"] = self._api_key

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                return response.status_code == 200
        except Exception:
            return False

    def _resolve_category(self, query: str) -> str | None:
        """Resolve search query to The Muse category."""
        query_lower = query.lower()

        for keyword, category in JOB_CATEGORIES.items():
            if keyword in query_lower:
                return category

        return None

    def _parse_job(self, data: dict) -> Job:
        """Parse The Muse API response into Job domain model."""
        # Extract company info
        company = data.get("company", {})
        company_name = company.get("name", "Unknown Company")

        # Extract locations
        locations = data.get("locations", [])
        location_str = ", ".join(loc.get("name", "") for loc in locations[:2])
        if not location_str:
            location_str = "Unknown"

        # Determine if remote
        is_remote = any(
            "remote" in loc.get("name", "").lower()
            for loc in locations
        )

        # Extract levels
        levels = data.get("levels", [])
        experience_level = levels[0].get("name") if levels else None

        # Build job URL
        job_id = data.get("id", "")
        short_name = data.get("short_name", "")
        job_url = f"https://www.themuse.com/jobs/{company_name.lower().replace(' ', '-')}/{short_name}"

        # Extract categories for skills
        categories = data.get("categories", [])
        category_names = [cat.get("name", "") for cat in categories]

        return Job(
            id=str(uuid.uuid4()),
            external_id=f"themuse_{job_id}",
            title=data.get("name", ""),
            company=company_name,
            location=location_str,
            description=data.get("contents", ""),
            url=data.get("refs", {}).get("landing_page", job_url),
            source=JobSource.THEMUSE,
            salary_min=None,  # The Muse doesn't provide salary in API
            salary_max=None,
            remote=is_remote,
            requirements=JobRequirements(
                required_skills=category_names,
                preferred_skills=[],
                experience_years=self._parse_experience_years(experience_level),
            ),
            posted_at=self._parse_date(data.get("publication_date")),
            ingested_at=datetime.utcnow(),
        )

    def _parse_experience_years(self, level: str | None) -> int | None:
        """Map experience level to years."""
        if not level:
            return None

        level_lower = level.lower()
        if "entry" in level_lower:
            return 0
        elif "mid" in level_lower:
            return 3
        elif "senior" in level_lower:
            return 5
        elif "management" in level_lower or "manager" in level_lower:
            return 7
        elif "executive" in level_lower:
            return 10

        return None

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None

        try:
            # The Muse uses ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None
