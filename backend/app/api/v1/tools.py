"""Career tools API endpoints.

Standards: python_clean.mdc
- Async operations
- Proper error handling
- kw-only args
"""

import structlog
from fastapi import APIRouter, HTTPException, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.config import get_settings
from app.infra.llm.together_client import TogetherLLMClient
from app.schemas.career_tools import (
    CareerAssessRequest,
    CareerAssessResponse,
    CareerPathsRequest,
    CareerPathsResponse,
    InterviewEndRequest,
    InterviewEndResponse,
    InterviewRespondRequest,
    InterviewRespondResponse,
    InterviewStartRequest,
    InterviewStartResponse,
    NegotiationAnalyzeRequest,
    NegotiationAnalyzeResponse,
    NegotiationStrategyRequest,
    NegotiationStrategyResponse,
)

router = APIRouter()
logger = structlog.get_logger()


def _get_llm_client() -> TogetherLLMClient:
    """Get configured LLM client."""
    settings = get_settings()
    return TogetherLLMClient(
        api_key=settings.together_api_key.get_secret_value(),
    )


# =============================================================================
# Interview Roleplay Endpoints
# =============================================================================


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(
    request: InterviewStartRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> InterviewStartResponse:
    """Start a new mock interview session.

    Creates an interview session with questions tailored to the target role
    and experience level. Uses the user's resume for personalization if available.
    """
    from app.core.services.career_tools import InterviewRoleplayService
    from app.infra.db.repositories.resume import SQLResumeRepository

    try:
        llm = _get_llm_client()
        service = InterviewRoleplayService(llm_client=llm)

        # Get user's resume for context
        resume_context = None
        resume_repo = SQLResumeRepository(session=db)
        resume = await resume_repo.get_primary(user_id=current_user.id)
        if resume and resume.parsed_data:
            skills = resume.parsed_data.skills[:15] if resume.parsed_data.skills else []
            resume_context = f"Skills: {', '.join(skills)}"

        response = await service.start_session(
            user_id=current_user.id,
            target_role=request.target_role,
            company_name=request.company_name,
            interview_type=request.interview_type,
            experience_level=request.experience_level,
            focus_areas=request.focus_areas,
            resume_context=resume_context,
        )

        logger.info(
            "interview_started",
            user_id=current_user.id,
            session_id=response.session_id,
            target_role=request.target_role,
        )

        return response

    except Exception as e:
        logger.error("interview_start_error", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start interview session",
        )


@router.post("/interview/respond", response_model=InterviewRespondResponse)
async def respond_to_question(
    request: InterviewRespondRequest,
    current_user: CurrentUser,
) -> InterviewRespondResponse:
    """Submit an answer to the current interview question.

    Returns feedback on the answer and the next question if available.
    """
    from app.core.services.career_tools import InterviewRoleplayService

    try:
        llm = _get_llm_client()
        service = InterviewRoleplayService(llm_client=llm)

        feedback, next_question, remaining, score = await service.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
        )

        return InterviewRespondResponse(
            feedback=feedback,
            next_question=next_question,
            questions_remaining=remaining,
            current_score=score,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "interview_respond_error",
            error=str(e),
            user_id=current_user.id,
            session_id=request.session_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process answer",
        )


@router.post("/interview/end", response_model=InterviewEndResponse)
async def end_interview(
    request: InterviewEndRequest,
    current_user: CurrentUser,
) -> InterviewEndResponse:
    """End the interview session and get summary.

    Returns overall performance summary with recommendations.
    """
    from app.core.services.career_tools import InterviewRoleplayService

    try:
        llm = _get_llm_client()
        service = InterviewRoleplayService(llm_client=llm)

        summary = await service.end_session(session_id=request.session_id)

        logger.info(
            "interview_ended",
            user_id=current_user.id,
            session_id=request.session_id,
            overall_score=summary.overall_score,
        )

        return InterviewEndResponse(summary=summary)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "interview_end_error",
            error=str(e),
            user_id=current_user.id,
            session_id=request.session_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end interview session",
        )


# =============================================================================
# Offer Negotiation Endpoints
# =============================================================================


@router.post("/negotiation/analyze", response_model=NegotiationAnalyzeResponse)
async def analyze_offer(
    request: NegotiationAnalyzeRequest,
    current_user: CurrentUser,
) -> NegotiationAnalyzeResponse:
    """Analyze a job offer against market data.

    Returns market comparison, strengths, concerns, and negotiation room.
    """
    from app.core.services.career_tools import OfferNegotiationService

    try:
        llm = _get_llm_client()
        service = OfferNegotiationService(llm_client=llm)

        response = await service.analyze_offer(
            offer=request.offer,
            target_role=request.target_role,
            location=request.location,
            years_experience=request.years_experience,
            competing_offers=request.competing_offers,
            current_salary=request.current_salary,
        )

        logger.info(
            "offer_analyzed",
            user_id=current_user.id,
            target_role=request.target_role,
            market_position=response.market_comparison.position,
        )

        return response

    except Exception as e:
        logger.error("offer_analyze_error", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze offer",
        )


@router.post("/negotiation/strategy", response_model=NegotiationStrategyResponse)
async def get_negotiation_strategy(
    request: NegotiationStrategyRequest,
    current_user: CurrentUser,
) -> NegotiationStrategyResponse:
    """Get negotiation strategy and scripts.

    Returns recommended counter, justification points, and ready-to-use scripts.
    """
    from app.core.services.career_tools import OfferNegotiationService

    try:
        llm = _get_llm_client()
        service = OfferNegotiationService(llm_client=llm)

        response = await service.get_strategy(
            offer=request.offer,
            target_role=request.target_role,
            location=request.location,
            years_experience=request.years_experience,
            target_salary=request.target_salary,
            priorities=request.priorities,
            risk_tolerance=request.risk_tolerance,
        )

        logger.info(
            "negotiation_strategy_generated",
            user_id=current_user.id,
            target_role=request.target_role,
            recommended_counter=response.recommended_counter,
        )

        return response

    except Exception as e:
        logger.error("negotiation_strategy_error", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate negotiation strategy",
        )


# =============================================================================
# Career Advisor Endpoints
# =============================================================================


@router.post("/career/assess", response_model=CareerAssessResponse)
async def assess_career(
    request: CareerAssessRequest,
    current_user: CurrentUser,
) -> CareerAssessResponse:
    """Assess current career position and skills.

    Returns strengths, transferable skills, and market position analysis.
    """
    from app.core.services.career_tools import CareerAdvisorService

    try:
        llm = _get_llm_client()
        service = CareerAdvisorService(llm_client=llm)

        response = await service.assess_career(
            current_role=request.current_role,
            years_in_role=request.years_in_role,
            total_experience=request.total_experience,
            current_industry=request.current_industry,
            skills=request.skills,
            interests=request.interests,
            goals=request.goals,
            constraints=request.constraints,
        )

        logger.info(
            "career_assessed",
            user_id=current_user.id,
            current_role=request.current_role,
            growth_potential=response.growth_potential,
        )

        return response

    except Exception as e:
        logger.error("career_assess_error", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess career",
        )


@router.post("/career/paths", response_model=CareerPathsResponse)
async def get_career_paths(
    request: CareerPathsRequest,
    current_user: CurrentUser,
) -> CareerPathsResponse:
    """Get recommended career paths.

    Returns career path recommendations with transition steps and learning roadmap.
    """
    from app.core.services.career_tools import CareerAdvisorService

    try:
        llm = _get_llm_client()
        service = CareerAdvisorService(llm_client=llm)

        response = await service.get_career_paths(
            current_role=request.current_role,
            years_experience=request.years_experience,
            skills=request.skills,
            target_industries=request.target_industries,
            salary_expectation=request.salary_expectation,
            willing_to_relocate=request.willing_to_relocate,
            willing_to_reskill=request.willing_to_reskill,
            timeline_months=request.timeline_months,
        )

        logger.info(
            "career_paths_generated",
            user_id=current_user.id,
            current_role=request.current_role,
            paths_count=len(response.recommended_paths),
        )

        return response

    except Exception as e:
        logger.error("career_paths_error", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate career paths",
        )
