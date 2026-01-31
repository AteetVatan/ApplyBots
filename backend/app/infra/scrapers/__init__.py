"""Job scraper implementations.

Standards: python_clean.mdc
"""

from app.infra.scrapers.adzuna import AdzunaAdapter
from app.infra.scrapers.base import BaseJobScraper
from app.infra.scrapers.jooble import JoobleAdapter
from app.infra.scrapers.stackoverflow import StackOverflowAdapter
from app.infra.scrapers.themuse import TheMuseAdapter
from app.infra.scrapers.wellfound import WellFoundAdapter

__all__ = [
    "AdzunaAdapter",
    "BaseJobScraper",
    "JoobleAdapter",
    "StackOverflowAdapter",
    "TheMuseAdapter",
    "WellFoundAdapter",
]
