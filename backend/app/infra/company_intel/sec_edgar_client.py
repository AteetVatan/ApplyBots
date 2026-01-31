"""SEC EDGAR API client for company financials.

Standards: python_clean.mdc
- Async HTTP client
- Free API, no auth required (US public companies only)
"""

import httpx
import structlog

from app.core.domain.company_intel import CompanyFinancials

logger = structlog.get_logger(__name__)

SEC_COMPANY_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts"


class SECEdgarClient:
    """Client for SEC EDGAR API."""

    def __init__(self, *, timeout: float = 15.0) -> None:
        self._timeout = timeout
        # SEC requires a User-Agent header with contact info
        self._headers = {
            "User-Agent": "ApplyBots/1.0 (contact@applybots.com)",
            "Accept": "application/json",
        }

    async def get_company_financials(
        self,
        company_name: str,
    ) -> CompanyFinancials | None:
        """Get financial data for a US public company.

        Args:
            company_name: Company name or ticker symbol

        Returns:
            CompanyFinancials or None if not found/not public
        """
        try:
            # First, search for the company CIK
            cik = await self._search_company_cik(company_name)
            if not cik:
                return None

            # Get company facts
            return await self._get_company_facts(cik)

        except Exception as e:
            logger.warning(
                "sec_edgar_lookup_failed",
                company=company_name,
                error=str(e),
            )
            return None

    async def _search_company_cik(self, company_name: str) -> str | None:
        """Search for company CIK number.

        Args:
            company_name: Company name or ticker

        Returns:
            CIK number (padded to 10 digits) or None
        """
        # Try company tickers first (more reliable)
        ticker_url = "https://www.sec.gov/files/company_tickers.json"

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                headers=self._headers,
            ) as client:
                response = await client.get(ticker_url)
                response.raise_for_status()
                tickers_data = response.json()

            # Search by company name or ticker
            name_lower = company_name.lower().strip()

            for _, company in tickers_data.items():
                ticker = company.get("ticker", "").lower()
                title = company.get("title", "").lower()

                if name_lower == ticker or name_lower in title:
                    cik = str(company.get("cik_str", ""))
                    return cik.zfill(10)  # Pad to 10 digits

            return None

        except Exception as e:
            logger.debug("sec_cik_search_failed", error=str(e))
            return None

    async def _get_company_facts(self, cik: str) -> CompanyFinancials | None:
        """Get company financial facts from SEC.

        Args:
            cik: Company CIK number (10 digits)

        Returns:
            CompanyFinancials or None
        """
        url = f"{SEC_COMPANY_FACTS_URL}/CIK{cik}.json"

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                headers=self._headers,
            ) as client:
                response = await client.get(url)

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                data = response.json()

            # Extract key financial metrics
            facts = data.get("facts", {})
            us_gaap = facts.get("us-gaap", {})

            # Get latest fiscal year data
            revenue = self._get_latest_value(us_gaap.get("Revenues", {}))
            if not revenue:
                revenue = self._get_latest_value(us_gaap.get("RevenueFromContractWithCustomerExcludingAssessedTax", {}))

            net_income = self._get_latest_value(us_gaap.get("NetIncomeLoss", {}))
            total_assets = self._get_latest_value(us_gaap.get("Assets", {}))

            # Get employee count if available
            employees = None
            dei = facts.get("dei", {})
            emp_data = dei.get("EntityCommonStockSharesOutstanding", {})
            # Employee count is not always in SEC data

            if not any([revenue, net_income, total_assets]):
                return None

            # Determine fiscal year from the data
            fiscal_year = datetime.now().year - 1  # Default to last year

            return CompanyFinancials(
                fiscal_year=fiscal_year,
                revenue=revenue,
                net_income=net_income,
                total_assets=total_assets,
                employees=employees,
                currency="USD",
            )

        except Exception as e:
            logger.debug("sec_facts_fetch_failed", cik=cik, error=str(e))
            return None

    def _get_latest_value(self, metric_data: dict) -> float | None:
        """Extract latest value from SEC metric data.

        Args:
            metric_data: SEC API metric response

        Returns:
            Latest value or None
        """
        units = metric_data.get("units", {})

        # Try USD first, then pure numbers
        for unit_type in ["USD", "pure", "shares"]:
            if unit_type in units:
                values = units[unit_type]
                if values:
                    # Get most recent 10-K or 10-Q filing
                    annual_values = [
                        v for v in values
                        if v.get("form") in ("10-K", "10-K/A")
                    ]
                    if annual_values:
                        latest = max(
                            annual_values,
                            key=lambda x: x.get("end", ""),
                        )
                        return float(latest.get("val", 0))

        return None


# Import datetime at module level
from datetime import datetime
