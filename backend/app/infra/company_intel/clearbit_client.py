"""Clearbit Logo API client.

Standards: python_clean.mdc
- Free API for company logos
- No auth required
"""

import structlog

logger = structlog.get_logger(__name__)

CLEARBIT_LOGO_URL = "https://logo.clearbit.com"


class ClearbitLogoClient:
    """Client for Clearbit Logo API (free)."""

    def get_logo_url(self, domain: str) -> str | None:
        """Get company logo URL from domain.

        Args:
            domain: Company domain (e.g., "google.com")

        Returns:
            Logo URL or None
        """
        if not domain:
            return None

        # Clean the domain
        domain = domain.lower().strip()
        if domain.startswith("http"):
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                parsed = urlparse(domain)
                domain = parsed.netloc or parsed.path
            except Exception:
                pass

        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]

        if not domain or "." not in domain:
            return None

        return f"{CLEARBIT_LOGO_URL}/{domain}"

    def get_logo_url_from_company_name(self, company_name: str) -> str | None:
        """Attempt to get logo URL from company name.

        Args:
            company_name: Company name

        Returns:
            Logo URL or None (guess based on common patterns)
        """
        if not company_name:
            return None

        # Clean and guess domain
        name = company_name.lower().strip()

        # Remove common suffixes
        for suffix in [" inc", " inc.", " llc", " ltd", " corp", " corporation", " company"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)]

        # Replace spaces with nothing (most companies use single-word domains)
        domain_guess = name.replace(" ", "").replace(",", "").replace(".", "")

        # Try common TLDs
        return f"{CLEARBIT_LOGO_URL}/{domain_guess}.com"
