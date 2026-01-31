"""Career tools services for Interview, Negotiation, and Career Advisor.

Standards: python_clean.mdc
- Async operations
- Protocol for LLM client
- kw-only args
- Structured logging
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

import structlog

from app.agents.config import Models
from app.agents.prompts import (
    CAREER_ADVISOR_PROMPT,
    INTERVIEW_ROLEPLAY_PROMPT,
    NEGOTIATION_ADVISOR_PROMPT,
)
from app.core.ports.llm import LLMClient, LLMMessage
from app.schemas.career_tools import (
    AnswerFeedback,
    CareerAssessResponse,
    CareerPath,
    CareerPathsResponse,
    ExperienceLevel,
    FeedbackRating,
    InterviewQuestion,
    InterviewStartResponse,
    InterviewSummary,
    InterviewType,
    LearningResource,
    MarketComparison,
    NegotiationAnalyzeResponse,
    NegotiationScript,
    NegotiationStrategyResponse,
    OfferDetails,
    SkillAssessment,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Interview Session State
# =============================================================================


@dataclass
class InterviewSessionState:
    """State for an ongoing interview session."""

    session_id: str
    user_id: str
    target_role: str
    company_name: str | None
    interview_type: InterviewType
    experience_level: ExperienceLevel
    focus_areas: list[str]
    questions: list[InterviewQuestion] = field(default_factory=list)
    answers: list[dict] = field(default_factory=list)
    current_question_idx: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    total_score: float = 0.0


# In-memory session store (replace with Redis in production)
_interview_sessions: dict[str, InterviewSessionState] = {}


# =============================================================================
# Interview Roleplay Service
# =============================================================================


class InterviewRoleplayService:
    """Service for conducting mock interviews.

    Uses Llama-4-Scout for fast, conversational responses.
    """

    def __init__(self, *, llm_client: LLMClient) -> None:
        self._llm = llm_client
        self._model = Models.LLAMA4_SCOUT

    async def start_session(
        self,
        *,
        user_id: str,
        target_role: str,
        company_name: str | None = None,
        interview_type: InterviewType = InterviewType.MIXED,
        experience_level: ExperienceLevel = ExperienceLevel.MID,
        focus_areas: list[str] | None = None,
        resume_context: str | None = None,
    ) -> InterviewStartResponse:
        """Start a new interview session."""
        session_id = str(uuid.uuid4())

        # Generate initial questions
        questions = await self._generate_questions(
            target_role=target_role,
            company_name=company_name,
            interview_type=interview_type,
            experience_level=experience_level,
            focus_areas=focus_areas or [],
            resume_context=resume_context,
        )

        # Create session state
        session = InterviewSessionState(
            session_id=session_id,
            user_id=user_id,
            target_role=target_role,
            company_name=company_name,
            interview_type=interview_type,
            experience_level=experience_level,
            focus_areas=focus_areas or [],
            questions=questions,
        )

        _interview_sessions[session_id] = session

        logger.info(
            "interview_session_started",
            session_id=session_id,
            user_id=user_id,
            target_role=target_role,
            question_count=len(questions),
        )

        return InterviewStartResponse(
            session_id=session_id,
            target_role=target_role,
            first_question=questions[0],
            total_questions=len(questions),
            estimated_duration_minutes=len(questions) * 5,
        )

    async def _generate_questions(
        self,
        *,
        target_role: str,
        company_name: str | None,
        interview_type: InterviewType,
        experience_level: ExperienceLevel,
        focus_areas: list[str],
        resume_context: str | None,
    ) -> list[InterviewQuestion]:
        """Generate interview questions using LLM."""
        company_text = f" at {company_name}" if company_name else ""
        focus_text = f"\nFocus areas: {', '.join(focus_areas)}" if focus_areas else ""
        resume_text = f"\nCandidate background:\n{resume_context}" if resume_context else ""

        prompt = f"""Generate 5-7 interview questions for a {experience_level.value}-level {target_role} position{company_text}.

Interview type: {interview_type.value}
{focus_text}
{resume_text}

Return a JSON array of questions with this structure:
[
  {{
    "question_text": "The interview question",
    "question_type": "behavioral|technical|situational",
    "difficulty": "easy|medium|hard",
    "context": "Optional context or what you're looking for"
  }}
]

Generate questions appropriate for the experience level.
For mixed interviews, include a variety of question types."""

        messages = [
            LLMMessage(role="system", content=INTERVIEW_ROLEPLAY_PROMPT),
            LLMMessage(role="user", content=prompt),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.6,
            max_tokens=1500,
        )

        # Parse JSON response
        try:
            questions_data = json.loads(self._extract_json(response.content))
        except json.JSONDecodeError:
            logger.warning("interview_questions_parse_error", content=response.content[:200])
            questions_data = self._get_fallback_questions(interview_type)

        questions = []
        for i, q in enumerate(questions_data[:7]):
            q_type = q.get("question_type", "behavioral")
            try:
                question_type = InterviewType(q_type)
            except ValueError:
                question_type = InterviewType.BEHAVIORAL

            questions.append(
                InterviewQuestion(
                    question_id=f"q_{i}",
                    question_text=q.get("question_text", "Tell me about yourself."),
                    question_type=question_type,
                    difficulty=q.get("difficulty", "medium"),
                    context=q.get("context"),
                )
            )

        return questions or self._get_fallback_questions_parsed()

    def _extract_json(self, content: str) -> str:
        """Extract JSON from LLM response."""
        # Find JSON array in response
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            return content[start:end]
        return "[]"

    def _get_fallback_questions(self, interview_type: InterviewType) -> list[dict]:
        """Fallback questions if generation fails."""
        return [
            {
                "question_text": "Tell me about yourself and your professional background.",
                "question_type": "behavioral",
                "difficulty": "easy",
            },
            {
                "question_text": "What interests you about this role?",
                "question_type": "behavioral",
                "difficulty": "easy",
            },
            {
                "question_text": "Describe a challenging project you worked on and how you handled it.",
                "question_type": "behavioral",
                "difficulty": "medium",
            },
            {
                "question_text": "How do you prioritize tasks when you have multiple deadlines?",
                "question_type": "situational",
                "difficulty": "medium",
            },
            {
                "question_text": "Where do you see yourself in 5 years?",
                "question_type": "behavioral",
                "difficulty": "easy",
            },
        ]

    def _get_fallback_questions_parsed(self) -> list[InterviewQuestion]:
        """Get parsed fallback questions."""
        fallback = self._get_fallback_questions(InterviewType.MIXED)
        return [
            InterviewQuestion(
                question_id=f"q_{i}",
                question_text=q["question_text"],
                question_type=InterviewType(q["question_type"]),
                difficulty=q["difficulty"],
            )
            for i, q in enumerate(fallback)
        ]

    async def submit_answer(
        self,
        *,
        session_id: str,
        question_id: str,
        answer: str,
    ) -> tuple[AnswerFeedback, InterviewQuestion | None, int, float]:
        """Submit an answer and get feedback."""
        session = _interview_sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        current_question = session.questions[session.current_question_idx]

        # Generate feedback using LLM
        feedback = await self._generate_feedback(
            question=current_question,
            answer=answer,
            target_role=session.target_role,
            experience_level=session.experience_level,
        )

        # Store answer
        session.answers.append({
            "question_id": question_id,
            "answer": answer,
            "feedback": feedback,
        })
        session.total_score += feedback.score

        # Move to next question
        session.current_question_idx += 1
        questions_remaining = len(session.questions) - session.current_question_idx

        next_question = None
        if questions_remaining > 0:
            next_question = session.questions[session.current_question_idx]

        current_avg_score = session.total_score / len(session.answers)

        logger.info(
            "interview_answer_submitted",
            session_id=session_id,
            question_idx=session.current_question_idx - 1,
            score=feedback.score,
        )

        return feedback, next_question, questions_remaining, current_avg_score

    async def _generate_feedback(
        self,
        *,
        question: InterviewQuestion,
        answer: str,
        target_role: str,
        experience_level: ExperienceLevel,
    ) -> AnswerFeedback:
        """Generate feedback for an answer using LLM."""
        prompt = f"""Evaluate this interview answer for a {experience_level.value}-level {target_role} position.

Question: {question.question_text}
Question Type: {question.question_type.value}

Candidate's Answer:
{answer}

Provide feedback in this JSON format:
{{
  "score": <1-10>,
  "rating": "poor|needs_improvement|good|excellent",
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1", "improvement2"],
  "example_answer": "A brief example of a strong answer",
  "tips": ["tip1", "tip2"]
}}

Be constructive and specific. Consider:
- Clarity and structure (STAR method for behavioral)
- Relevance to the question
- Demonstration of skills/experience
- Communication quality"""

        messages = [
            LLMMessage(role="system", content=INTERVIEW_ROLEPLAY_PROMPT),
            LLMMessage(role="user", content=prompt),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.5,
            max_tokens=800,
        )

        try:
            feedback_data = json.loads(self._extract_json_object(response.content))
        except json.JSONDecodeError:
            feedback_data = self._get_fallback_feedback(answer)

        # Map rating string to enum
        rating_str = feedback_data.get("rating", "good").lower().replace(" ", "_")
        try:
            rating = FeedbackRating(rating_str)
        except ValueError:
            rating = FeedbackRating.GOOD

        return AnswerFeedback(
            score=min(10, max(1, feedback_data.get("score", 5))),
            rating=rating,
            strengths=feedback_data.get("strengths", ["Good effort"]),
            improvements=feedback_data.get("improvements", ["Consider adding more detail"]),
            example_answer=feedback_data.get("example_answer"),
            tips=feedback_data.get("tips", []),
        )

    def _extract_json_object(self, content: str) -> str:
        """Extract JSON object from LLM response."""
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return content[start:end]
        return "{}"

    def _get_fallback_feedback(self, answer: str) -> dict:
        """Fallback feedback if generation fails."""
        word_count = len(answer.split())
        score = 5
        if word_count > 100:
            score = 7
        elif word_count > 50:
            score = 6
        elif word_count < 20:
            score = 4

        return {
            "score": score,
            "rating": "good" if score >= 6 else "needs_improvement",
            "strengths": ["You provided a response to the question"],
            "improvements": ["Consider adding more specific examples"],
            "tips": ["Use the STAR method for behavioral questions"],
        }

    async def end_session(self, *, session_id: str) -> InterviewSummary:
        """End an interview session and get summary."""
        session = _interview_sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        questions_answered = len(session.answers)
        overall_score = session.total_score / questions_answered if questions_answered > 0 else 0

        # Determine overall rating
        if overall_score >= 8:
            overall_rating = FeedbackRating.EXCELLENT
        elif overall_score >= 6:
            overall_rating = FeedbackRating.GOOD
        elif overall_score >= 4:
            overall_rating = FeedbackRating.NEEDS_IMPROVEMENT
        else:
            overall_rating = FeedbackRating.POOR

        # Aggregate strengths and improvements
        all_strengths: list[str] = []
        all_improvements: list[str] = []
        for ans in session.answers:
            fb = ans.get("feedback")
            if fb:
                all_strengths.extend(fb.strengths[:2])
                all_improvements.extend(fb.improvements[:2])

        # Deduplicate
        strengths = list(dict.fromkeys(all_strengths))[:5]
        improvements = list(dict.fromkeys(all_improvements))[:5]

        duration = int((datetime.utcnow() - session.started_at).total_seconds() / 60)

        summary = InterviewSummary(
            session_id=session_id,
            target_role=session.target_role,
            total_questions=len(session.questions),
            questions_answered=questions_answered,
            overall_score=round(overall_score, 1),
            overall_rating=overall_rating,
            strengths=strengths,
            areas_to_improve=improvements,
            recommendations=self._get_recommendations(overall_score, session.interview_type),
            duration_minutes=duration,
        )

        # Clean up session
        del _interview_sessions[session_id]

        logger.info(
            "interview_session_ended",
            session_id=session_id,
            overall_score=overall_score,
            questions_answered=questions_answered,
        )

        return summary

    def _get_recommendations(self, score: float, interview_type: InterviewType) -> list[str]:
        """Get recommendations based on performance."""
        recs = []
        if score < 6:
            recs.append("Practice more with the STAR method for behavioral questions")
            recs.append("Prepare specific examples from your experience before interviews")
        if score < 8:
            recs.append("Work on quantifying your achievements with metrics")
            recs.append("Research the company thoroughly before your interview")
        if interview_type == InterviewType.TECHNICAL:
            recs.append("Review fundamental concepts for your technical domain")
        return recs[:4]


# =============================================================================
# Offer Negotiation Service
# =============================================================================


class OfferNegotiationService:
    """Service for offer analysis and negotiation advice.

    Uses Llama-3.3-70B for strong reasoning on financial analysis.
    """

    def __init__(self, *, llm_client: LLMClient) -> None:
        self._llm = llm_client
        self._model = Models.LLAMA3_70B

    async def analyze_offer(
        self,
        *,
        offer: OfferDetails,
        target_role: str,
        location: str,
        years_experience: int,
        competing_offers: int = 0,
        current_salary: float | None = None,
    ) -> NegotiationAnalyzeResponse:
        """Analyze a job offer against market data."""
        # Calculate total compensation
        total_comp = self._calculate_total_compensation(offer)

        # Get market analysis from LLM
        prompt = f"""Analyze this job offer for a {target_role} position in {location}:

Offer Details:
- Base Salary: {offer.currency} {offer.base_salary:,.0f}
- Signing Bonus: {offer.currency} {offer.signing_bonus:,.0f if offer.signing_bonus else 'None'}
- Annual Bonus: {offer.annual_bonus_percent}% if {offer.annual_bonus_percent else 'None'}
- Equity Value: {offer.currency} {offer.equity_value:,.0f if offer.equity_value else 'None'} over {offer.equity_vesting_years or 4} years
- PTO: {offer.pto_days or 'Not specified'} days
- Remote: {offer.remote_policy or 'Not specified'}
- Other Benefits: {', '.join(offer.other_benefits) if offer.other_benefits else 'None listed'}

Candidate Info:
- Years of Experience: {years_experience}
- Competing Offers: {competing_offers}
- Current Salary: {offer.currency} {current_salary:,.0f if current_salary else 'Not disclosed'}

Provide analysis in this JSON format:
{{
  "market_percentile": <0-100>,
  "market_low": <number>,
  "market_median": <number>,
  "market_high": <number>,
  "position": "below_market|at_market|above_market",
  "strengths": ["strength1", "strength2"],
  "concerns": ["concern1", "concern2"],
  "negotiation_room": "low|medium|high",
  "priority_items": ["item1", "item2"]
}}

Base your analysis on typical market rates for this role, location, and experience level."""

        messages = [
            LLMMessage(role="system", content=NEGOTIATION_ADVISOR_PROMPT),
            LLMMessage(role="user", content=prompt),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.4,
            max_tokens=1000,
        )

        try:
            analysis = json.loads(self._extract_json_object(response.content))
        except json.JSONDecodeError:
            analysis = self._get_fallback_analysis(offer, years_experience)

        # Build market comparison
        position_str = analysis.get("position", "at_market")
        try:
            position: Literal["below_market", "at_market", "above_market"] = position_str
        except ValueError:
            position = "at_market"

        market_comparison = MarketComparison(
            percentile=analysis.get("market_percentile", 50),
            market_low=analysis.get("market_low", offer.base_salary * 0.8),
            market_median=analysis.get("market_median", offer.base_salary),
            market_high=analysis.get("market_high", offer.base_salary * 1.3),
            position=position,
        )

        neg_room = analysis.get("negotiation_room", "medium")
        if neg_room not in ("low", "medium", "high"):
            neg_room = "medium"

        logger.info(
            "offer_analyzed",
            target_role=target_role,
            total_comp=total_comp,
            market_position=position,
        )

        return NegotiationAnalyzeResponse(
            total_compensation=total_comp,
            market_comparison=market_comparison,
            strengths=analysis.get("strengths", []),
            concerns=analysis.get("concerns", []),
            negotiation_room=neg_room,
            priority_items=analysis.get("priority_items", []),
        )

    def _calculate_total_compensation(self, offer: OfferDetails) -> float:
        """Calculate total annual compensation value."""
        total = offer.base_salary

        if offer.signing_bonus:
            total += offer.signing_bonus / 4  # Amortize over 4 years

        if offer.annual_bonus_percent:
            total += offer.base_salary * (offer.annual_bonus_percent / 100)

        if offer.equity_value and offer.equity_vesting_years:
            total += offer.equity_value / offer.equity_vesting_years

        return total

    def _extract_json_object(self, content: str) -> str:
        """Extract JSON object from LLM response."""
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return content[start:end]
        return "{}"

    def _get_fallback_analysis(self, offer: OfferDetails, years: int) -> dict:
        """Fallback analysis if LLM fails."""
        base = offer.base_salary
        return {
            "market_percentile": 50,
            "market_low": base * 0.85,
            "market_median": base,
            "market_high": base * 1.25,
            "position": "at_market",
            "strengths": ["Offer received"],
            "concerns": ["Market comparison unavailable"],
            "negotiation_room": "medium",
            "priority_items": ["Base salary", "Equity"],
        }

    async def get_strategy(
        self,
        *,
        offer: OfferDetails,
        target_role: str,
        location: str,
        years_experience: int,
        target_salary: float | None = None,
        priorities: list[str] | None = None,
        risk_tolerance: Literal["low", "medium", "high"] = "medium",
    ) -> NegotiationStrategyResponse:
        """Get negotiation strategy and scripts."""
        target = target_salary or offer.base_salary * 1.15

        prompt = f"""Create a negotiation strategy for this {target_role} offer in {location}:

Current Offer: {offer.currency} {offer.base_salary:,.0f} base
Target: {offer.currency} {target:,.0f}
Years Experience: {years_experience}
Priorities: {', '.join(priorities) if priorities else 'Not specified'}
Risk Tolerance: {risk_tolerance}

Provide strategy in this JSON format:
{{
  "recommended_counter": <number>,
  "justification_points": ["point1", "point2", "point3"],
  "initial_response": "Script for verbal response to offer",
  "counter_offer_email": "Email template for counter offer",
  "phone_script": "Script for phone negotiation",
  "fallback_positions": ["fallback1", "fallback2"],
  "timing_advice": "When and how to respond",
  "risk_assessment": "Assessment of negotiation risks",
  "alternative_asks": ["alt1", "alt2"]
}}

Consider the risk tolerance when crafting the strategy."""

        messages = [
            LLMMessage(role="system", content=NEGOTIATION_ADVISOR_PROMPT),
            LLMMessage(role="user", content=prompt),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.5,
            max_tokens=1500,
        )

        try:
            strategy = json.loads(self._extract_json_object(response.content))
        except json.JSONDecodeError:
            strategy = self._get_fallback_strategy(offer, target)

        scripts = NegotiationScript(
            initial_response=strategy.get("initial_response", "Thank you for the offer. I'm excited about the opportunity and would like to discuss the compensation package."),
            counter_offer_email=strategy.get("counter_offer_email", "Draft email template unavailable"),
            phone_script=strategy.get("phone_script", "Phone script unavailable"),
            fallback_positions=strategy.get("fallback_positions", ["Additional PTO", "Signing bonus"]),
        )

        logger.info(
            "negotiation_strategy_generated",
            target_role=target_role,
            recommended_counter=strategy.get("recommended_counter", target),
        )

        return NegotiationStrategyResponse(
            recommended_counter=strategy.get("recommended_counter", target),
            justification_points=strategy.get("justification_points", []),
            scripts=scripts,
            timing_advice=strategy.get("timing_advice", "Respond within 24-48 hours"),
            risk_assessment=strategy.get("risk_assessment", "Moderate risk with standard negotiation"),
            alternative_asks=strategy.get("alternative_asks", []),
        )

    def _get_fallback_strategy(self, offer: OfferDetails, target: float) -> dict:
        """Fallback strategy if LLM fails."""
        return {
            "recommended_counter": target,
            "justification_points": [
                "Market research supports this compensation level",
                "Your experience adds significant value",
            ],
            "initial_response": "Thank you for the offer. I'm very excited about this opportunity and would like to discuss the compensation.",
            "counter_offer_email": "Email template generation failed. Please draft manually.",
            "phone_script": "Script generation failed.",
            "fallback_positions": ["Additional equity", "Signing bonus", "Extra PTO"],
            "timing_advice": "Respond within 24-48 hours",
            "risk_assessment": "Standard negotiation risk",
            "alternative_asks": ["Remote flexibility", "Professional development budget"],
        }


# =============================================================================
# Career Advisor Service
# =============================================================================


class CareerAdvisorService:
    """Service for career assessment and path recommendations.

    Uses Llama-4-Maverick for analytical capability.
    """

    def __init__(self, *, llm_client: LLMClient) -> None:
        self._llm = llm_client
        self._model = Models.LLAMA4_MAVERICK

    async def assess_career(
        self,
        *,
        current_role: str,
        years_in_role: int,
        total_experience: int,
        current_industry: str,
        skills: list[str],
        interests: list[str] | None = None,
        goals: list[str] | None = None,
        constraints: list[str] | None = None,
    ) -> CareerAssessResponse:
        """Assess current career position and skills."""
        prompt = f"""Assess this professional's career position:

Current Role: {current_role}
Years in Role: {years_in_role}
Total Experience: {total_experience} years
Industry: {current_industry}
Skills: {', '.join(skills)}
Interests: {', '.join(interests) if interests else 'Not specified'}
Goals: {', '.join(goals) if goals else 'Not specified'}
Constraints: {', '.join(constraints) if constraints else 'None'}

Provide assessment in this JSON format:
{{
  "strengths": ["strength1", "strength2", "strength3"],
  "transferable_skills": ["skill1", "skill2", "skill3"],
  "skill_assessments": [
    {{
      "category": "Technical",
      "skills": ["skill1", "skill2"],
      "proficiency": "beginner|intermediate|advanced|expert",
      "market_demand": "low|medium|high"
    }}
  ],
  "market_position": "Description of market positioning",
  "growth_potential": "low|medium|high",
  "key_insights": ["insight1", "insight2"]
}}

Consider current job market trends and industry demands."""

        messages = [
            LLMMessage(role="system", content=CAREER_ADVISOR_PROMPT),
            LLMMessage(role="user", content=prompt),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.5,
            max_tokens=1200,
        )

        try:
            assessment = json.loads(self._extract_json_object(response.content))
        except json.JSONDecodeError:
            assessment = self._get_fallback_assessment(skills, total_experience)

        # Parse skill assessments
        skill_assessments = []
        for sa in assessment.get("skill_assessments", []):
            prof = sa.get("proficiency", "intermediate")
            if prof not in ("beginner", "intermediate", "advanced", "expert"):
                prof = "intermediate"

            demand = sa.get("market_demand", "medium")
            if demand not in ("low", "medium", "high"):
                demand = "medium"

            skill_assessments.append(
                SkillAssessment(
                    category=sa.get("category", "General"),
                    skills=sa.get("skills", []),
                    proficiency=prof,
                    market_demand=demand,
                )
            )

        growth = assessment.get("growth_potential", "medium")
        if growth not in ("low", "medium", "high"):
            growth = "medium"

        logger.info(
            "career_assessed",
            current_role=current_role,
            growth_potential=growth,
        )

        return CareerAssessResponse(
            strengths=assessment.get("strengths", []),
            transferable_skills=assessment.get("transferable_skills", []),
            skill_assessments=skill_assessments,
            market_position=assessment.get("market_position", "Stable market position"),
            growth_potential=growth,
            key_insights=assessment.get("key_insights", []),
        )

    def _extract_json_object(self, content: str) -> str:
        """Extract JSON object from LLM response."""
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return content[start:end]
        return "{}"

    def _get_fallback_assessment(self, skills: list[str], years: int) -> dict:
        """Fallback assessment if LLM fails."""
        return {
            "strengths": skills[:3] if skills else ["Experience in field"],
            "transferable_skills": skills[:5] if skills else [],
            "skill_assessments": [],
            "market_position": "Assessment unavailable",
            "growth_potential": "medium",
            "key_insights": ["Consider updating technical skills"],
        }

    async def get_career_paths(
        self,
        *,
        current_role: str,
        years_experience: int,
        skills: list[str],
        target_industries: list[str] | None = None,
        salary_expectation: float | None = None,
        willing_to_relocate: bool = False,
        willing_to_reskill: bool = True,
        timeline_months: int = 12,
    ) -> CareerPathsResponse:
        """Get recommended career paths."""
        prompt = f"""Recommend career paths for this professional:

Current Role: {current_role}
Experience: {years_experience} years
Skills: {', '.join(skills)}
Target Industries: {', '.join(target_industries) if target_industries else 'Open to all'}
Salary Expectation: {'$' + str(int(salary_expectation)) if salary_expectation else 'Not specified'}
Willing to Relocate: {willing_to_relocate}
Willing to Reskill: {willing_to_reskill}
Timeline: {timeline_months} months

Provide recommendations in this JSON format:
{{
  "recommended_paths": [
    {{
      "target_role": "Role title",
      "target_industry": "Industry",
      "fit_score": <0-100>,
      "salary_range_low": <number>,
      "salary_range_high": <number>,
      "time_to_transition_months": <number>,
      "skill_gaps": ["gap1", "gap2"],
      "required_certifications": ["cert1"],
      "steps": ["step1", "step2", "step3"],
      "pros": ["pro1", "pro2"],
      "cons": ["con1", "con2"]
    }}
  ],
  "learning_roadmap": [
    {{
      "skill": "Skill name",
      "resource_type": "course|certification|book|project|mentorship",
      "name": "Resource name",
      "provider": "Provider name",
      "estimated_hours": <number>,
      "priority": "critical|important|nice_to_have"
    }}
  ],
  "quick_wins": ["win1", "win2"],
  "long_term_goals": ["goal1", "goal2"],
  "networking_suggestions": ["suggestion1", "suggestion2"]
}}

Provide 3-5 career paths ranked by fit score."""

        messages = [
            LLMMessage(role="system", content=CAREER_ADVISOR_PROMPT),
            LLMMessage(role="user", content=prompt),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=self._model,
            temperature=0.5,
            max_tokens=2000,
        )

        try:
            paths_data = json.loads(self._extract_json_object(response.content))
        except json.JSONDecodeError:
            paths_data = self._get_fallback_paths(current_role, years_experience)

        # Parse career paths
        paths = []
        for p in paths_data.get("recommended_paths", [])[:5]:
            paths.append(
                CareerPath(
                    target_role=p.get("target_role", "Senior " + current_role),
                    target_industry=p.get("target_industry", "Technology"),
                    fit_score=min(100, max(0, p.get("fit_score", 70))),
                    salary_range_low=p.get("salary_range_low", 80000),
                    salary_range_high=p.get("salary_range_high", 120000),
                    time_to_transition_months=p.get("time_to_transition_months", 6),
                    skill_gaps=p.get("skill_gaps", []),
                    required_certifications=p.get("required_certifications", []),
                    steps=p.get("steps", []),
                    pros=p.get("pros", []),
                    cons=p.get("cons", []),
                )
            )

        # Parse learning resources
        resources = []
        for r in paths_data.get("learning_roadmap", [])[:10]:
            res_type = r.get("resource_type", "course")
            if res_type not in ("course", "certification", "book", "project", "mentorship"):
                res_type = "course"

            priority = r.get("priority", "important")
            if priority not in ("critical", "important", "nice_to_have"):
                priority = "important"

            resources.append(
                LearningResource(
                    skill=r.get("skill", "General"),
                    resource_type=res_type,
                    name=r.get("name", "Recommended course"),
                    provider=r.get("provider"),
                    estimated_hours=r.get("estimated_hours", 20),
                    priority=priority,
                )
            )

        logger.info(
            "career_paths_generated",
            current_role=current_role,
            paths_count=len(paths),
        )

        return CareerPathsResponse(
            recommended_paths=paths,
            learning_roadmap=resources,
            quick_wins=paths_data.get("quick_wins", []),
            long_term_goals=paths_data.get("long_term_goals", []),
            networking_suggestions=paths_data.get("networking_suggestions", []),
        )

    def _get_fallback_paths(self, current_role: str, years: int) -> dict:
        """Fallback paths if LLM fails."""
        return {
            "recommended_paths": [
                {
                    "target_role": f"Senior {current_role}",
                    "target_industry": "Current Industry",
                    "fit_score": 85,
                    "salary_range_low": 90000,
                    "salary_range_high": 130000,
                    "time_to_transition_months": 6,
                    "skill_gaps": [],
                    "required_certifications": [],
                    "steps": ["Build expertise", "Take on leadership", "Apply for promotion"],
                    "pros": ["Natural progression", "Uses existing skills"],
                    "cons": ["May require patience"],
                }
            ],
            "learning_roadmap": [],
            "quick_wins": ["Update resume", "Expand network"],
            "long_term_goals": ["Achieve senior position"],
            "networking_suggestions": ["Join industry groups"],
        }
