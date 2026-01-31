"""Jooble job aggregator scraper.

Standards: python_clean.mdc
- Async HTTP client
- REST API aggregating 140k+ sources
- Global job search across multiple countries
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.job import Job, JobRequirements, JobSource
from app.infra.scrapers.base import BaseJobScraper, SearchFilters

logger = structlog.get_logger(__name__)

# Jooble country-specific API endpoints
COUNTRY_ENDPOINTS = {
    "us": "https://jooble.org/api/",
    "gb": "https://gb.jooble.org/api/",
    "uk": "https://gb.jooble.org/api/",
    "ca": "https://ca.jooble.org/api/",
    "au": "https://au.jooble.org/api/",
    "de": "https://de.jooble.org/api/",
    "fr": "https://fr.jooble.org/api/",
    "in": "https://in.jooble.org/api/",
    "nl": "https://nl.jooble.org/api/",
    "br": "https://br.jooble.org/api/",
    "pl": "https://pl.jooble.org/api/",
    "sg": "https://sg.jooble.org/api/",
    "za": "https://za.jooble.org/api/",
    "nz": "https://nz.jooble.org/api/",
    "at": "https://at.jooble.org/api/",
    "ch": "https://ch.jooble.org/api/",
    "default": "https://jooble.org/api/",
}


class JoobleAdapter(BaseJobScraper):
    """Jooble job aggregator adapter.

    Aggregates jobs from 140,000+ sources worldwide.
    API docs: https://jooble.org/api/about
    """

    def __init__(
        self,
        *,
        api_key: str,
        default_country: str = "us",
    ) -> None:
        """Initialize Jooble adapter.

        Args:
            api_key: Jooble API key
            default_country: Default country code
        """
        self._api_key = api_key
        self._default_country = default_country

    @property
    def name(self) -> str:
        return "jooble"

    async def search(
        self,
        *,
        filters: SearchFilters,
        limit: int = 50,
        country: str | None = None,
    ) -> list[Job]:
        """Search for jobs on Jooble.

        Args:
            filters: Search filter criteria
            limit: Maximum number of results
            country: Country code to search in

        Returns:
            List of matching jobs
        """
        country_code = (country or self._default_country).lower()
        endpoint = COUNTRY_ENDPOINTS.get(country_code, COUNTRY_ENDPOINTS["default"])

        logger.info(
            "jooble_search",
            query=filters.query,
            location=filters.location,
            country=country_code,
            limit=limit,
        )

        jobs: list[Job] = []

        if not self._api_key:
            logger.warning("jooble_not_configured")
            return []

        try:
            url = f"{endpoint}{self._api_key}"

            # Build request payload
            payload: dict[str, str | int] = {
                "page": 1,
            }

            if filters.query:
                payload["keywords"] = filters.query
            if filters.location:
                payload["location"] = filters.location
            if filters.salary_min:
                payload["salary"] = str(filters.salary_min)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code != 200:
                    logger.warning(
                        "jooble_search_failed",
                        status_code=response.status_code,
                        response=response.text[:200],
                    )
                    return []

                data = response.json()
                results = data.get("jobs", [])

                for job_data in results[:limit]:
                    try:
                        job = self._parse_job(job_data, country_code)
                        jobs.append(job)
                    except Exception as e:
                        logger.warning(
                            "jooble_parse_error",
                            error=str(e),
                        )

        except httpx.TimeoutException:
            logger.warning("jooble_timeout")
        except Exception as e:
            logger.error("jooble_search_error", error=str(e))

        logger.info("jooble_search_complete", job_count=len(jobs))
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
            countries: List of country codes
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
        """Check if Jooble API is accessible."""
        if not self._api_key:
            return False

        try:
            url = f"{COUNTRY_ENDPOINTS['default']}{self._api_key}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={"keywords": "software", "page": 1},
                    headers={"Content-Type": "application/json"},
                )
                return response.status_code == 200
        except Exception:
            return False

    def _parse_job(self, data: dict, country_code: str) -> Job:
        """Parse Jooble API response into Job domain model."""
        # Extract salary - Jooble returns salary as string
        salary_str = data.get("salary", "")
        salary_min, salary_max = self._parse_salary(salary_str)

        # Determine if remote
        title_lower = data.get("title", "").lower()
        snippet_lower = data.get("snippet", "").lower()
        is_remote = "remote" in title_lower or "remote" in snippet_lower

        # Build location
        location = data.get("location", "")
        if not location:
            location = country_code.upper()

        return Job(
            id=str(uuid.uuid4()),
            external_id=f"jooble_{data.get('id', str(uuid.uuid4())[:8])}",
            title=data.get("title", ""),
            company=data.get("company", "Unknown Company"),
            location=location,
            description=data.get("snippet", ""),
            url=data.get("link", ""),
            source=JobSource.JOOBLE,
            salary_min=salary_min,
            salary_max=salary_max,
            remote=is_remote,
            requirements=JobRequirements(
                required_skills=[],
                preferred_skills=[],
            ),
            posted_at=self._parse_date(data.get("updated")),
            ingested_at=datetime.utcnow(),
        )

    def _parse_salary(self, salary_str: str) -> tuple[int | None, int | None]:
        """Parse salary string into min/max values."""
        if not salary_str:
            return None, None

        import re

        # Look for numbers in the salary string
        numbers = re.findall(r"[\d,]+", salary_str.replace(",", ""))

        try:
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                return int(numbers[0]), None
        except ValueError:
            pass

        return None, None

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None

        try:
            # Jooble uses various date formats
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            try:
                # Try parsing as timestamp
                from datetime import timezone
                return datetime.fromtimestamp(int(date_str), tz=timezone.utc)
            except Exception:
                return None
