"""ATS (Applicant Tracking System) scoring service.

Standards: python_clean.mdc
- Pure business logic scoring
- Keyword matching algorithms
- No external dependencies
"""

import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser

import structlog

from app.core.domain.resume import ATSScoreResult, ResumeContent

logger = structlog.get_logger(__name__)


# Weights for ATS scoring criteria
ATS_SCORING_WEIGHTS = {
    "keyword_match": 30,  # Keywords from job description
    "formatting": 20,  # Clean structure
    "section_completeness": 20,  # Required sections present
    "quantified_achievements": 15,  # Numbers in bullet points
    "length_appropriateness": 10,  # 1-2 pages
    "contact_info": 5,  # Complete contact details
}

# Required sections for a complete resume
REQUIRED_SECTIONS = [
    "contact",  # Name, email at minimum
    "experience",  # Work experience
    "education",  # Education history
    "skills",  # Skills section
]

# Common ATS-unfriendly patterns
ATS_UNFRIENDLY_PATTERNS = [
    r"[^\x00-\x7F]+",  # Non-ASCII characters
    r"[\u2022\u2023\u25E6\u2043\u2219]",  # Fancy bullets
    r"[│┃┆┊╎]",  # Line drawing characters
]

# Common action verbs that ATS systems look for
ACTION_VERBS = {
    "achieved", "improved", "trained", "managed", "created", "resolved",
    "developed", "launched", "implemented", "designed", "led", "increased",
    "decreased", "negotiated", "generated", "delivered", "analyzed", "built",
    "coordinated", "executed", "established", "reduced", "streamlined",
    "optimized", "collaborated", "mentored", "pioneered", "spearheaded",
}


class HTMLStripper(HTMLParser):
    """Simple HTML tag stripper."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return "".join(self.fed)


def strip_html(html: str) -> str:
    """Strip HTML tags from text."""
    if not html:
        return ""
    stripper = HTMLStripper()
    try:
        stripper.feed(unescape(html))
        return stripper.get_data()
    except Exception:
        # Fallback to simple regex if parser fails
        return re.sub(r"<[^>]+>", "", html)


@dataclass
class KeywordAnalysis:
    """Result of keyword analysis."""

    matched: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    match_rate: float = 0.0


class ATSScoringService:
    """Service for calculating ATS compatibility scores.

    Evaluates resumes against ATS requirements and job descriptions
    to provide a compatibility score and improvement suggestions.
    """

    def calculate_score(
        self,
        *,
        content: ResumeContent,
        job_description: str | None = None,
    ) -> ATSScoreResult:
        """Calculate ATS compatibility score for resume content.

        Args:
            content: Resume content to evaluate
            job_description: Optional job description for keyword matching

        Returns:
            ATSScoreResult with detailed scores and suggestions
        """
        suggestions: list[str] = []

        # 1. Keyword matching (30 points)
        keyword_result = self._analyze_keywords(
            content=content,
            job_description=job_description,
        )
        keyword_score = int(keyword_result.match_rate * ATS_SCORING_WEIGHTS["keyword_match"])
        if keyword_result.match_rate < 0.5:
            suggestions.append(
                f"Add more relevant keywords from the job description. Missing: {', '.join(keyword_result.missing[:5])}"
            )

        # 2. Formatting score (20 points)
        formatting_score = self._calculate_formatting_score(content)
        if formatting_score < ATS_SCORING_WEIGHTS["formatting"]:
            suggestions.append("Simplify formatting - avoid special characters and complex layouts")

        # 3. Section completeness (20 points)
        section_score = self._calculate_section_score(content)
        if section_score < ATS_SCORING_WEIGHTS["section_completeness"]:
            suggestions.append("Ensure all essential sections are present: Contact, Experience, Education, Skills")

        # 4. Quantified achievements (15 points)
        quantified_score = self._calculate_quantified_score(content)
        if quantified_score < ATS_SCORING_WEIGHTS["quantified_achievements"]:
            suggestions.append("Add more quantified achievements (numbers, percentages, dollar amounts)")

        # 5. Length appropriateness (10 points)
        length_score = self._calculate_length_score(content)
        if length_score < ATS_SCORING_WEIGHTS["length_appropriateness"]:
            suggestions.append("Aim for 1-2 pages - too short or too long hurts ATS compatibility")

        # 6. Contact info completeness (5 points)
        contact_score = self._calculate_contact_score(content)
        if contact_score < ATS_SCORING_WEIGHTS["contact_info"]:
            suggestions.append("Complete your contact information (name, email, phone)")

        # Calculate total score
        total_score = (
            keyword_score
            + formatting_score
            + section_score
            + quantified_score
            + length_score
            + contact_score
        )

        logger.info(
            "ats_score_calculated",
            total_score=total_score,
            keyword_score=keyword_score,
            formatting_score=formatting_score,
            section_score=section_score,
            quantified_score=quantified_score,
            length_score=length_score,
            contact_score=contact_score,
        )

        return ATSScoreResult(
            total_score=min(100, total_score),  # Cap at 100
            keyword_match_score=keyword_score,
            formatting_score=formatting_score,
            section_completeness_score=section_score,
            quantified_achievements_score=quantified_score,
            length_score=length_score,
            contact_info_score=contact_score,
            suggestions=suggestions,
            matched_keywords=keyword_result.matched,
            missing_keywords=keyword_result.missing,
        )

    def _analyze_keywords(
        self,
        *,
        content: ResumeContent,
        job_description: str | None,
    ) -> KeywordAnalysis:
        """Analyze keyword matches between resume and job description.

        Args:
            content: Resume content
            job_description: Job description text

        Returns:
            KeywordAnalysis with matched and missing keywords
        """
        if not job_description:
            # No job description - base score on general resume quality
            return KeywordAnalysis(
                matched=[],
                missing=[],
                match_rate=0.7,  # Default 70% without job description
            )

        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)

        # Get all text from resume
        resume_text = self._get_resume_text(content).lower()

        # Find matches
        matched = []
        missing = []

        for keyword in job_keywords:
            keyword_lower = keyword.lower()
            # Check for exact match or partial match
            if keyword_lower in resume_text or any(
                word in resume_text for word in keyword_lower.split()
            ):
                matched.append(keyword)
            else:
                missing.append(keyword)

        match_rate = len(matched) / len(job_keywords) if job_keywords else 0.5

        return KeywordAnalysis(
            matched=matched[:20],  # Limit to top 20
            missing=missing[:20],
            match_rate=match_rate,
        )

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract important keywords from text.

        Args:
            text: Text to extract keywords from

        Returns:
            List of extracted keywords
        """
        # Common words to ignore
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall", "can",
            "this", "that", "these", "those", "it", "its", "they", "them", "their",
            "we", "our", "you", "your", "he", "she", "him", "her", "his",
            "about", "above", "after", "before", "between", "into", "through",
            "during", "under", "again", "further", "then", "once", "here", "there",
            "when", "where", "why", "how", "all", "each", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "just", "also", "now", "experience",
            "work", "working", "job", "position", "role", "team", "company",
        }

        # Clean and tokenize
        text_clean = re.sub(r"[^\w\s]", " ", text.lower())
        words = text_clean.split()

        # Filter and count
        keywords = []
        seen = set()

        for word in words:
            if (
                len(word) > 2
                and word not in stop_words
                and word not in seen
                and not word.isdigit()
            ):
                keywords.append(word)
                seen.add(word)

        # Also extract multi-word phrases (bigrams)
        bigrams = []
        for i in range(len(words) - 1):
            if words[i] not in stop_words and words[i + 1] not in stop_words:
                bigram = f"{words[i]} {words[i + 1]}"
                if bigram not in seen:
                    bigrams.append(bigram)
                    seen.add(bigram)

        return keywords[:30] + bigrams[:10]

    def _get_resume_text(self, content: ResumeContent) -> str:
        """Get all text content from resume.

        Args:
            content: Resume content (new nested structure)

        Returns:
            Combined text from all sections
        """
        parts = []

        # Summary (strip HTML)
        if content.summary and content.summary.content:
            parts.append(strip_html(content.summary.content))

        # Experience section
        for exp in content.sections.experience.items:
            if not exp.hidden:
                parts.append(f"{exp.title} {exp.company}")
                if exp.description:
                    parts.append(strip_html(exp.description))

        # Education section
        for edu in content.sections.education.items:
            if not edu.hidden:
                parts.append(f"{edu.degree} {edu.school}")
                if edu.area:
                    parts.append(edu.area)
                if edu.description:
                    parts.append(strip_html(edu.description))

        # Skills section
        for skill in content.sections.skills.items:
            if not skill.hidden:
                parts.append(skill.name)
                parts.extend(skill.keywords)

        # Projects section
        for proj in content.sections.projects.items:
            if not proj.hidden:
                parts.append(proj.name)
                if proj.description:
                    parts.append(strip_html(proj.description))

        # Certifications section
        for cert in content.sections.certifications.items:
            if not cert.hidden:
                parts.append(cert.title)
                parts.append(cert.issuer)

        # Awards section
        for award in content.sections.awards.items:
            if not award.hidden:
                parts.append(award.title)
                if award.description:
                    parts.append(strip_html(award.description))

        # Languages section
        for lang in content.sections.languages.items:
            if not lang.hidden:
                parts.append(lang.language)

        # Volunteer section
        for vol in content.sections.volunteer.items:
            if not vol.hidden:
                parts.append(vol.organization)
                if vol.description:
                    parts.append(strip_html(vol.description))

        # Publications section
        for pub in content.sections.publications.items:
            if not pub.hidden:
                parts.append(pub.title)
                if pub.description:
                    parts.append(strip_html(pub.description))

        return " ".join(parts)

    def _calculate_formatting_score(self, content: ResumeContent) -> int:
        """Calculate formatting score based on ATS-friendliness.

        Args:
            content: Resume content

        Returns:
            Score out of 20 points
        """
        score = ATS_SCORING_WEIGHTS["formatting"]  # Start with full score

        text = self._get_resume_text(content)

        # Check for ATS-unfriendly patterns
        for pattern in ATS_UNFRIENDLY_PATTERNS:
            if re.search(pattern, text):
                score -= 3

        # Check for too many special characters
        special_chars = len(re.findall(r"[^\w\s.,;:!?\-()]", text))
        if special_chars > 20:
            score -= 2

        return max(0, score)

    def _calculate_section_score(self, content: ResumeContent) -> int:
        """Calculate section completeness score.

        Args:
            content: Resume content

        Returns:
            Score out of 20 points
        """
        score = 0
        points_per_section = ATS_SCORING_WEIGHTS["section_completeness"] // len(REQUIRED_SECTIONS)

        # Contact section (name and email required)
        if content.basics.name and content.basics.email:
            score += points_per_section

        # Experience section
        visible_experience = [e for e in content.sections.experience.items if not e.hidden]
        if visible_experience:
            score += points_per_section

        # Education section
        visible_education = [e for e in content.sections.education.items if not e.hidden]
        if visible_education:
            score += points_per_section

        # Skills section
        visible_skills = [s for s in content.sections.skills.items if not s.hidden]
        if visible_skills:
            score += points_per_section

        return score

    def _calculate_quantified_score(self, content: ResumeContent) -> int:
        """Calculate score based on quantified achievements.

        Args:
            content: Resume content

        Returns:
            Score out of 15 points
        """
        max_score = ATS_SCORING_WEIGHTS["quantified_achievements"]

        # Count descriptions with numbers and action verbs
        total_items = 0
        quantified_items = 0
        action_verb_items = 0

        # Check experience descriptions
        for exp in content.sections.experience.items:
            if exp.hidden:
                continue
            if not exp.description:
                continue
            
            total_items += 1
            text = strip_html(exp.description)

            # Check for numbers
            if re.search(r"\d+", text):
                quantified_items += 1

            # Check for action verbs (check first word of bullet points)
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                first_word = line.split()[0].lower() if line.split() else ""
                if first_word in ACTION_VERBS:
                    action_verb_items += 1
                    break  # Count once per description

        # Also check projects
        for proj in content.sections.projects.items:
            if proj.hidden:
                continue
            if not proj.description:
                continue
            
            total_items += 1
            text = strip_html(proj.description)

            if re.search(r"\d+", text):
                quantified_items += 1

        if total_items == 0:
            return 0

        # Calculate score based on percentage of quantified items
        quantified_rate = quantified_items / total_items
        action_rate = action_verb_items / total_items if total_items > 0 else 0

        # Weight: 60% quantified, 40% action verbs
        score = int(max_score * (0.6 * quantified_rate + 0.4 * action_rate))

        return min(max_score, score)

    def _calculate_length_score(self, content: ResumeContent) -> int:
        """Calculate score based on resume length.

        Args:
            content: Resume content

        Returns:
            Score out of 10 points
        """
        max_score = ATS_SCORING_WEIGHTS["length_appropriateness"]

        # Estimate word count
        text = self._get_resume_text(content)
        word_count = len(text.split())

        # Ideal range: 300-800 words (roughly 1-2 pages)
        if 300 <= word_count <= 800:
            return max_score
        elif 200 <= word_count < 300 or 800 < word_count <= 1000:
            return int(max_score * 0.7)
        elif 100 <= word_count < 200 or 1000 < word_count <= 1200:
            return int(max_score * 0.4)
        else:
            return int(max_score * 0.2)

    def _calculate_contact_score(self, content: ResumeContent) -> int:
        """Calculate contact information completeness score.

        Args:
            content: Resume content

        Returns:
            Score out of 5 points
        """
        max_score = ATS_SCORING_WEIGHTS["contact_info"]
        score = 0

        # Essential: name and email (3 points)
        if content.basics.name:
            score += 1.5
        if content.basics.email:
            score += 1.5

        # Nice to have: phone and location (2 points)
        if content.basics.phone:
            score += 1
        if content.basics.location:
            score += 1

        return min(max_score, int(score))
