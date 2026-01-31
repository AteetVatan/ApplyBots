"""Recommendation mode service for campaign job discovery.

Standards: python_clean.mdc
- Manages transition from keyword to learned mode
- Integrates with JobPreferenceService for similarity-based recommendations
"""

from datetime import datetime

import structlog

from app.core.domain.campaign import Campaign, RecommendationMode
from app.core.services.job_preference import JobPreferenceService

logger = structlog.get_logger(__name__)

# Minimum days before switching to learned mode
MIN_DAYS_FOR_LEARNED_MODE = 3

# Minimum applied jobs before switching to learned mode
MIN_APPLICATIONS_FOR_LEARNED_MODE = 5


def get_effective_recommendation_mode(
    *,
    campaign: Campaign,
    applied_count: int,
) -> RecommendationMode:
    """Determine the effective recommendation mode for a campaign.

    After 3 days of activation and with enough applied jobs,
    switches from keyword matching to learned (ML-based) recommendations.

    Args:
        campaign: The campaign to evaluate
        applied_count: Number of jobs the user has applied to

    Returns:
        The effective recommendation mode to use
    """
    # If not activated yet, use keyword mode
    if not campaign.activated_at:
        logger.debug(
            "recommendation_mode_keyword_not_activated",
            campaign_id=campaign.id,
        )
        return RecommendationMode.KEYWORD

    # Calculate days since activation
    days_active = (datetime.utcnow() - campaign.activated_at).days

    # If less than 3 days active, use keyword mode
    if days_active < MIN_DAYS_FOR_LEARNED_MODE:
        logger.debug(
            "recommendation_mode_keyword_too_early",
            campaign_id=campaign.id,
            days_active=days_active,
        )
        return RecommendationMode.KEYWORD

    # If not enough applied jobs, use keyword mode
    if applied_count < MIN_APPLICATIONS_FOR_LEARNED_MODE:
        logger.debug(
            "recommendation_mode_keyword_insufficient_data",
            campaign_id=campaign.id,
            days_active=days_active,
            applied_count=applied_count,
            min_required=MIN_APPLICATIONS_FOR_LEARNED_MODE,
        )
        return RecommendationMode.KEYWORD

    # Ready for learned mode
    logger.debug(
        "recommendation_mode_learned",
        campaign_id=campaign.id,
        days_active=days_active,
        applied_count=applied_count,
    )
    return RecommendationMode.LEARNED


async def check_and_update_recommendation_mode(
    *,
    campaign: Campaign,
    job_preference_service: JobPreferenceService,
) -> tuple[RecommendationMode, bool]:
    """Check if campaign should switch recommendation mode and update if needed.

    Args:
        campaign: The campaign to check
        job_preference_service: Service to query applied job count

    Returns:
        Tuple of (effective mode, whether mode changed)
    """
    # Get applied count from preference service
    applied_count = await job_preference_service.get_applied_count(campaign.user_id)

    # Determine effective mode
    effective_mode = get_effective_recommendation_mode(
        campaign=campaign,
        applied_count=applied_count,
    )

    # Check if mode changed
    mode_changed = effective_mode != campaign.recommendation_mode

    if mode_changed:
        logger.info(
            "recommendation_mode_changed",
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            old_mode=campaign.recommendation_mode.value,
            new_mode=effective_mode.value,
            applied_count=applied_count,
        )

    return effective_mode, mode_changed


def should_use_semantic_search(mode: RecommendationMode) -> bool:
    """Determine if semantic search should be used for job discovery.

    In LEARNED mode, we use semantic similarity from applied jobs.
    In KEYWORD mode, we use traditional keyword/filter matching.

    Args:
        mode: The recommendation mode

    Returns:
        True if semantic search should be used
    """
    return mode == RecommendationMode.LEARNED
