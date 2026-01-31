"""WellFound (formerly AngelList Talent) job scraper.

Standards: python_clean.mdc
- Async HTTP client
- GraphQL API
- Rate limiting
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.job import Job, JobRequirements, JobSource
from app.infra.scrapers.base import BaseJobScraper, SearchFilters

logger = structlog.get_logger(__name__)


class WellFoundAdapter(BaseJobScraper):
    """WellFound job scraper adapter.

    Uses WellFound's public job listings API.
    """

    BASE_URL = "https://wellfound.com/api"
    GRAPHQL_URL = "https://api.wellfound.com/graphql"

    @property
    def name(self) -> str:
        return "wellfound"

    async def search(
        self,
        *,
        filters: SearchFilters,
        limit: int = 50,
    ) -> list[Job]:
        """Search for jobs on WellFound.

        Args:
            filters: Search filter criteria
            limit: Maximum number of results

        Returns:
            List of matching jobs
        """
        logger.info(
            "wellfound_search",
            query=filters.query,
            location=filters.location,
            remote_only=filters.remote_only,
            limit=limit,
        )

        jobs: list[Job] = []

        try:
            # Build GraphQL query
            query = self._build_search_query(filters, limit)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.GRAPHQL_URL,
                    json={"query": query},
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

                if response.status_code != 200:
                    logger.warning(
                        "wellfound_search_failed",
                        status_code=response.status_code,
                    )
                    return []

                data = response.json()

                # Parse jobs from response
                job_listings = (
                    data.get("data", {})
                    .get("talent", {})
                    .get("seoLandingPageJobSearchResults", {})
                    .get("startupJobs", [])
                )

                for job_data in job_listings[:limit]:
                    try:
                        job = self._parse_job(job_data)
                        jobs.append(job)
                    except Exception as e:
                        logger.warning(
                            "wellfound_parse_error",
                            error=str(e),
                        )

        except httpx.TimeoutException:
            logger.warning("wellfound_timeout")
        except Exception as e:
            logger.error("wellfound_search_error", error=str(e))

        logger.info("wellfound_search_complete", job_count=len(jobs))
        return jobs

    async def health_check(self) -> bool:
        """Check if WellFound API is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://wellfound.com/")
                return response.status_code == 200
        except Exception:
            return False

    def _build_search_query(self, filters: SearchFilters, limit: int) -> str:
        """Build GraphQL query for job search."""
        # Build filter variables
        role_filter = filters.query or "software engineer"
        location_filter = filters.location or "United States"

        # GraphQL query for WellFound job search
        return f"""
        query {{
            talent {{
                seoLandingPageJobSearchResults(
                    roleFilter: "{role_filter}"
                    locationFilter: "{location_filter}"
                    remoteFilter: {str(filters.remote_only).lower()}
                    first: {limit}
                ) {{
                    startupJobs {{
                        id
                        title
                        slug
                        description
                        remoteOk
                        primaryRoleTitle
                        compensation
                        startup {{
                            id
                            name
                            slug
                            companyUrl
                            logoUrl
                            highConcept
                            location
                        }}
                        jobPostingLocation
                        createdAt
                    }}
                }}
            }}
        }}
        """

    def _parse_job(self, data: dict) -> Job:
        """Parse WellFound API response into Job domain model."""
        startup = data.get("startup", {})
        compensation = data.get("compensation", "")

        # Parse salary from compensation string
        salary_min, salary_max = self._parse_compensation(compensation)

        # Build job URL
        startup_slug = startup.get("slug", "")
        job_slug = data.get("slug", "")
        job_url = f"https://wellfound.com/company/{startup_slug}/jobs/{job_slug}"

        return Job(
            id=str(uuid.uuid4()),
            external_id=f"wellfound_{data.get('id', '')}",
            title=data.get("title", ""),
            company=startup.get("name", ""),
            location=data.get("jobPostingLocation", startup.get("location", "Remote")),
            description=data.get("description", startup.get("highConcept", "")),
            url=job_url,
            source=JobSource.WELLFOUND,
            salary_min=salary_min,
            salary_max=salary_max,
            remote=data.get("remoteOk", False),
            requirements=JobRequirements(
                required_skills=[],
                preferred_skills=[],
            ),
            posted_at=self._parse_date(data.get("createdAt")),
            ingested_at=datetime.utcnow(),
        )

    def _parse_compensation(self, comp_str: str) -> tuple[int | None, int | None]:
        """Parse compensation string into min/max values."""
        if not comp_str:
            return None, None

        import re

        # Look for numbers in the compensation string
        numbers = re.findall(r"[\d,]+", comp_str.replace(",", ""))

        try:
            if len(numbers) >= 2:
                return int(numbers[0]) * 1000, int(numbers[1]) * 1000
            elif len(numbers) == 1:
                return int(numbers[0]) * 1000, None
        except ValueError:
            pass

        return None, None

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None
