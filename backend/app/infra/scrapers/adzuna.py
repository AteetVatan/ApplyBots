"""Adzuna job aggregator scraper.

Standards: python_clean.mdc
- Async HTTP client
- REST API with country-specific endpoints
- Covers 16 countries with millions of jobs
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.job import Job, JobRequirements, JobSource
from app.infra.scrapers.base import BaseJobScraper, SearchFilters

logger = structlog.get_logger(__name__)

# Adzuna country codes mapping
COUNTRY_CODES = {
    "united states": "us",
    "usa": "us",
    "united kingdom": "gb",
    "uk": "gb",
    "canada": "ca",
    "australia": "au",
    "germany": "de",
    "france": "fr",
    "india": "in",
    "netherlands": "nl",
    "brazil": "br",
    "poland": "pl",
    "russia": "ru",
    "singapore": "sg",
    "south africa": "za",
    "new zealand": "nz",
    "austria": "at",
    "switzerland": "ch",
}


class AdzunaAdapter(BaseJobScraper):
    """Adzuna job aggregator adapter.

    Aggregates jobs from thousands of sources across 16 countries.
    API docs: https://developer.adzuna.com/
    """

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(
        self,
        *,
        app_id: str,
        api_key: str,
        default_country: str = "us",
    ) -> None:
        """Initialize Adzuna adapter.

        Args:
            app_id: Adzuna application ID
            api_key: Adzuna API key
            default_country: Default country code (e.g., 'us', 'gb')
        """
        self._app_id = app_id
        self._api_key = api_key
        self._default_country = default_country

    @property
    def name(self) -> str:
        return "adzuna"

    async def search(
        self,
        *,
        filters: SearchFilters,
        limit: int = 50,
        country: str | None = None,
    ) -> list[Job]:
        """Search for jobs on Adzuna.

        Args:
            filters: Search filter criteria
            limit: Maximum number of results
            country: Country code or name to search in

        Returns:
            List of matching jobs
        """
        country_code = self._resolve_country(country or filters.location)

        logger.info(
            "adzuna_search",
            query=filters.query,
            location=filters.location,
            country=country_code,
            limit=limit,
        )

        jobs: list[Job] = []

        if not self._app_id or not self._api_key:
            logger.warning("adzuna_not_configured")
            return []

        try:
            # Build API URL with country
            url = f"{self.BASE_URL}/{country_code}/search/1"

            params: dict[str, str | int] = {
                "app_id": self._app_id,
                "app_key": self._api_key,
                "results_per_page": min(limit, 50),  # Adzuna max is 50
                "content-type": "application/json",
            }

            if filters.query:
                params["what"] = filters.query
            if filters.location and country_code == self._default_country:
                params["where"] = filters.location
            if filters.salary_min:
                params["salary_min"] = filters.salary_min

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    logger.warning(
                        "adzuna_search_failed",
                        status_code=response.status_code,
                        response=response.text[:200],
                    )
                    return []

                data = response.json()
                results = data.get("results", [])

                for job_data in results[:limit]:
                    try:
                        job = self._parse_job(job_data)
                        jobs.append(job)
                    except Exception as e:
                        logger.warning(
                            "adzuna_parse_error",
                            error=str(e),
                            job_id=job_data.get("id"),
                        )

        except httpx.TimeoutException:
            logger.warning("adzuna_timeout")
        except Exception as e:
            logger.error("adzuna_search_error", error=str(e))

        logger.info("adzuna_search_complete", job_count=len(jobs))
        return jobs

    async def search_multiple_countries(
        self,
        *,
        filters: SearchFilters,
        countries: list[str],
        limit_per_country: int = 20,
    ) -> list[Job]:
        """Search for jobs across multiple countries.

        Args:
            filters: Search filter criteria
            countries: List of country codes or names
            limit_per_country: Max results per country

        Returns:
            Combined list of jobs from all countries
        """
        all_jobs: list[Job] = []

        for country in countries:
            jobs = await self.search(
                filters=filters,
                limit=limit_per_country,
                country=country,
            )
            all_jobs.extend(jobs)

        return all_jobs

    async def health_check(self) -> bool:
        """Check if Adzuna API is accessible."""
        if not self._app_id or not self._api_key:
            return False

        try:
            url = f"{self.BASE_URL}/us/search/1"
            params = {
                "app_id": self._app_id,
                "app_key": self._api_key,
                "results_per_page": 1,
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                return response.status_code == 200
        except Exception:
            return False

    def _resolve_country(self, location: str | None) -> str:
        """Resolve location to country code."""
        if not location:
            return self._default_country

        location_lower = location.lower().strip()

        # Check direct mapping
        if location_lower in COUNTRY_CODES:
            return COUNTRY_CODES[location_lower]

        # Check if location contains a country name
        for country_name, code in COUNTRY_CODES.items():
            if country_name in location_lower:
                return code

        return self._default_country

    def _parse_job(self, data: dict) -> Job:
        """Parse Adzuna API response into Job domain model."""
        # Extract salary info
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")

        # Handle salary that comes as floats
        if salary_min:
            salary_min = int(salary_min)
        if salary_max:
            salary_max = int(salary_max)

        # Parse location
        location = data.get("location", {})
        location_display = ", ".join(location.get("display_name", "").split(", ")[:2])

        # Determine if remote
        title_lower = data.get("title", "").lower()
        desc_lower = data.get("description", "").lower()
        is_remote = "remote" in title_lower or "remote" in desc_lower

        return Job(
            id=str(uuid.uuid4()),
            external_id=f"adzuna_{data.get('id', '')}",
            title=data.get("title", ""),
            company=data.get("company", {}).get("display_name", "Unknown Company"),
            location=location_display or "Unknown",
            description=data.get("description", ""),
            url=data.get("redirect_url", ""),
            source=JobSource.ADZUNA,
            salary_min=salary_min,
            salary_max=salary_max,
            remote=is_remote,
            requirements=JobRequirements(
                required_skills=[],
                preferred_skills=[],
            ),
            posted_at=self._parse_date(data.get("created")),
            ingested_at=datetime.utcnow(),
        )

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse ISO date string to datetime."""
        if not date_str:
            return None

        try:
            # Adzuna uses ISO format: 2024-01-15T12:00:00Z
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None
