"""Remote work intelligence service.

Standards: python_clean.mdc
- LLM-powered analysis
- Keyword-based fallback
"""

import re
from dataclasses import dataclass

import structlog

from app.core.domain.job import RemoteIntelligence, RemoteType
from app.core.ports.llm import LLMClient, LLMMessage

logger = structlog.get_logger(__name__)


# Keyword patterns for remote work detection
REMOTE_PATTERNS = {
    RemoteType.REMOTE_GLOBAL: [
        r"remote\s*\(?worldwide\)?",
        r"fully\s*remote",
        r"100%\s*remote",
        r"remote\s*first",
        r"work\s*from\s*anywhere",
        r"global\s*remote",
    ],
    RemoteType.REMOTE_US: [
        r"remote\s*\(?us\s*only\)?",
        r"remote\s*\(?usa\)?",
        r"remote\s*-\s*united\s*states",
        r"us\s*based\s*remote",
        r"remote.*must\s*be\s*in\s*(the\s*)?us",
    ],
    RemoteType.REMOTE: [
        r"\bremote\b",
        r"work\s*from\s*home",
        r"wfh",
        r"telecommute",
        r"virtual\s*position",
    ],
    RemoteType.HYBRID: [
        r"hybrid",
        r"\d+\s*days?\s*(in\s*)?office",
        r"office\s*\d+\s*days?",
        r"flexible\s*work",
        r"remote.*onsite",
        r"partial\s*remote",
    ],
    RemoteType.ONSITE: [
        r"on-?site\s*only",
        r"in-?office\s*required",
        r"must\s*work\s*(in|from)\s*office",
        r"no\s*remote",
        r"office\s*based",
    ],
}

# Timezone-related patterns
TIMEZONE_PATTERNS = [
    r"(PST|PDT|MST|MDT|CST|CDT|EST|EDT)",
    r"(pacific|mountain|central|eastern)\s*time",
    r"(PT|MT|CT|ET)\s*hours?",
    r"GMT\s*[+-]\d+",
    r"UTC\s*[+-]\d+",
]

# Travel requirement patterns
TRAVEL_PATTERNS = [
    r"(\d+)%?\s*travel",
    r"travel\s*required",
    r"occasional\s*travel",
    r"frequent\s*travel",
    r"no\s*travel",
    r"minimal\s*travel",
]


class RemoteIntelligenceService:
    """Service for analyzing remote work policies from job descriptions."""

    def __init__(
        self,
        *,
        llm_client: LLMClient | None = None,
    ) -> None:
        """Initialize remote intelligence service.

        Args:
            llm_client: Optional LLM client for advanced extraction
        """
        self._llm = llm_client

    def analyze(self, job_description: str) -> RemoteIntelligence:
        """Analyze remote work policy from job description.

        Args:
            job_description: Full job description text

        Returns:
            RemoteIntelligence with analysis results
        """
        description_lower = job_description.lower()

        # Detect remote type
        remote_type = self._detect_remote_type(description_lower)

        # Extract timezone requirements
        timezones = self._extract_timezones(description_lower)

        # Extract office locations
        offices = self._extract_office_locations(job_description)

        # Calculate remote score
        remote_score = self._calculate_remote_score(remote_type, description_lower)

        # Detect travel requirements
        travel_required = self._detect_travel(description_lower)

        logger.debug(
            "remote_analysis_complete",
            remote_type=remote_type.value,
            remote_score=remote_score,
            timezones=timezones,
        )

        return RemoteIntelligence(
            remote_type=remote_type,
            timezone_requirements=timezones if timezones else None,
            office_locations=offices,
            remote_score=remote_score,
            travel_required=travel_required,
        )

    async def analyze_with_llm(self, job_description: str) -> RemoteIntelligence:
        """Analyze remote work policy using LLM for better accuracy.

        Args:
            job_description: Full job description text

        Returns:
            RemoteIntelligence with analysis results
        """
        if not self._llm:
            return self.analyze(job_description)

        # First get keyword-based analysis as fallback
        keyword_result = self.analyze(job_description)

        try:
            from app.agents.config import Models

            prompt = f"""Analyze this job description for remote work policy.

Job Description:
{job_description[:2000]}

Extract:
1. Remote type: "onsite", "hybrid", "remote", "remote_us", or "remote_global"
2. Timezone requirements (if any)
3. Office locations (if any)
4. Travel requirements (yes/no/percentage)

Respond in this exact format:
REMOTE_TYPE: [type]
TIMEZONES: [comma-separated list or "none"]
OFFICES: [comma-separated list or "none"]
TRAVEL: [yes/no/percentage]
"""

            messages = [LLMMessage(role="user", content=prompt)]
            response = await self._llm.complete(
                messages=messages,
                model=Models.LLAMA3_8B,
                temperature=0.1,
                max_tokens=200,
            )

            # Parse LLM response
            return self._parse_llm_response(response.content, keyword_result)

        except Exception as e:
            logger.warning("llm_remote_analysis_failed", error=str(e))
            return keyword_result

    def calculate_timezone_compatibility(
        self,
        *,
        user_timezone: str,
        job_timezones: list[str] | None,
    ) -> int:
        """Calculate compatibility between user and job timezones.

        Args:
            user_timezone: User's timezone (e.g., "America/New_York")
            job_timezones: Required job timezones

        Returns:
            Compatibility score 0-100
        """
        if not job_timezones:
            return 100  # No restrictions = fully compatible

        # Map common timezone abbreviations to UTC offsets
        tz_offsets = {
            "PST": -8, "PDT": -7, "PT": -8,
            "MST": -7, "MDT": -6, "MT": -7,
            "CST": -6, "CDT": -5, "CT": -6,
            "EST": -5, "EDT": -4, "ET": -5,
            "GMT": 0, "UTC": 0,
        }

        # Simplified user timezone mapping
        user_offsets = {
            "America/Los_Angeles": -8,
            "America/Denver": -7,
            "America/Chicago": -6,
            "America/New_York": -5,
            "Europe/London": 0,
            "Europe/Paris": 1,
            "Asia/Tokyo": 9,
        }

        user_offset = user_offsets.get(user_timezone, -5)  # Default to EST

        # Find best match
        min_diff = float("inf")
        for tz in job_timezones:
            tz_upper = tz.upper()
            for abbrev, offset in tz_offsets.items():
                if abbrev in tz_upper:
                    diff = abs(user_offset - offset)
                    min_diff = min(min_diff, diff)
                    break

        if min_diff == float("inf"):
            return 80  # Unknown timezone requirements

        # Score based on hour difference (0 diff = 100, 12+ diff = 0)
        return max(0, 100 - int(min_diff * 8))

    def _detect_remote_type(self, description: str) -> RemoteType:
        """Detect remote work type from description."""
        # Check patterns in order of specificity
        for remote_type in [
            RemoteType.REMOTE_GLOBAL,
            RemoteType.REMOTE_US,
            RemoteType.ONSITE,
            RemoteType.HYBRID,
            RemoteType.REMOTE,
        ]:
            for pattern in REMOTE_PATTERNS[remote_type]:
                if re.search(pattern, description, re.IGNORECASE):
                    return remote_type

        return RemoteType.ONSITE  # Default to onsite

    def _extract_timezones(self, description: str) -> list[str]:
        """Extract timezone requirements from description."""
        timezones = []
        for pattern in TIMEZONE_PATTERNS:
            matches = re.findall(pattern, description, re.IGNORECASE)
            timezones.extend(matches)
        return list(set(timezones))

    def _extract_office_locations(self, description: str) -> list[str]:
        """Extract office locations from description."""
        # Common city patterns
        city_patterns = [
            r"located\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"office\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"based\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"headquarters\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        ]

        locations = []
        for pattern in city_patterns:
            matches = re.findall(pattern, description)
            locations.extend(matches)

        return list(set(locations))[:5]  # Limit to 5 locations

    def _calculate_remote_score(
        self,
        remote_type: RemoteType,
        description: str,
    ) -> int:
        """Calculate remote-friendliness score."""
        base_scores = {
            RemoteType.REMOTE_GLOBAL: 100,
            RemoteType.REMOTE: 90,
            RemoteType.REMOTE_US: 85,
            RemoteType.HYBRID: 50,
            RemoteType.ONSITE: 0,
        }

        score = base_scores[remote_type]

        # Boost for positive signals
        if "flexible" in description:
            score = min(100, score + 5)
        if "work-life balance" in description:
            score = min(100, score + 5)
        if "async" in description or "asynchronous" in description:
            score = min(100, score + 10)

        # Penalty for restrictions
        if "must be in" in description or "required to be" in description:
            score = max(0, score - 10)

        return score

    def _detect_travel(self, description: str) -> bool | None:
        """Detect if travel is required."""
        if "no travel" in description:
            return False
        if re.search(r"(\d+)%\s*travel", description):
            return True
        if "travel required" in description:
            return True
        if "occasional travel" in description:
            return True
        return None  # Unknown

    def _parse_llm_response(
        self,
        response: str,
        fallback: RemoteIntelligence,
    ) -> RemoteIntelligence:
        """Parse LLM response into RemoteIntelligence."""
        try:
            lines = response.strip().split("\n")
            data = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    data[key.strip().upper()] = value.strip()

            remote_type_str = data.get("REMOTE_TYPE", "onsite").lower()
            remote_type_map = {
                "onsite": RemoteType.ONSITE,
                "hybrid": RemoteType.HYBRID,
                "remote": RemoteType.REMOTE,
                "remote_us": RemoteType.REMOTE_US,
                "remote_global": RemoteType.REMOTE_GLOBAL,
            }
            remote_type = remote_type_map.get(remote_type_str, fallback.remote_type)

            timezones_str = data.get("TIMEZONES", "none")
            timezones = (
                None if timezones_str.lower() == "none"
                else [t.strip() for t in timezones_str.split(",")]
            )

            offices_str = data.get("OFFICES", "none")
            offices = (
                [] if offices_str.lower() == "none"
                else [o.strip() for o in offices_str.split(",")]
            )

            travel_str = data.get("TRAVEL", "").lower()
            travel = (
                True if "yes" in travel_str or "%" in travel_str
                else False if "no" in travel_str
                else None
            )

            return RemoteIntelligence(
                remote_type=remote_type,
                timezone_requirements=timezones,
                office_locations=offices,
                remote_score=fallback.remote_score,
                travel_required=travel,
            )

        except Exception as e:
            logger.warning("llm_response_parse_failed", error=str(e))
            return fallback
