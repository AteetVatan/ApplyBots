"""Base job scraper interface.

Standards: python_clean.mdc
- ABC for interfaces
- Async methods
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.domain.job import Job


@dataclass
class SearchFilters:
    """Search filter options."""

    query: str | None = None
    location: str | None = None
    remote_only: bool = False
    experience_level: str | None = None  # junior, mid, senior
    salary_min: int | None = None
    salary_max: int | None = None


class BaseJobScraper(ABC):
    """Abstract base class for job scrapers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Scraper name identifier."""
        ...

    @abstractmethod
    async def search(
        self,
        *,
        filters: SearchFilters,
        limit: int = 50,
    ) -> list[Job]:
        """Search for jobs matching the filters.

        Args:
            filters: Search filter criteria
            limit: Maximum number of results

        Returns:
            List of matching jobs
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the scraper is functioning.

        Returns:
            True if the scraper is healthy
        """
        ...
