"""Plan gating service.

Standards: python_clean.mdc
- Pure business logic, no IO
- No magic numbers (use PLAN_DAILY_LIMITS)
"""

from app.core.domain.subscription import (
    PLAN_CONCURRENT_LIMITS,
    PLAN_DAILY_LIMITS,
    Plan,
    Subscription,
)
from app.core.exceptions import PlanLimitExceededError


class PlanGatingService:
    """Enforce subscription plan limits.

    Pure business logic - no IO dependencies.
    """

    def check_daily_limit(
        self,
        *,
        subscription: Subscription,
        action_count: int = 1,
    ) -> None:
        """Check if user can perform more actions today.

        Args:
            subscription: User's subscription
            action_count: Number of actions to perform

        Raises:
            PlanLimitExceededError: If limit would be exceeded
        """
        limit = PLAN_DAILY_LIMITS.get(subscription.plan, PLAN_DAILY_LIMITS[Plan.FREE])

        if subscription.used_today + action_count > limit:
            raise PlanLimitExceededError("applications", limit)

    def check_concurrent_limit(
        self,
        *,
        subscription: Subscription,
        current_active: int,
    ) -> None:
        """Check if user can start more concurrent operations.

        Args:
            subscription: User's subscription
            current_active: Current number of active operations

        Raises:
            PlanLimitExceededError: If limit would be exceeded
        """
        limit = PLAN_CONCURRENT_LIMITS.get(
            subscription.plan, PLAN_CONCURRENT_LIMITS[Plan.FREE]
        )

        if current_active >= limit:
            raise PlanLimitExceededError("concurrent operations", limit)

    def get_remaining_today(self, *, subscription: Subscription) -> int:
        """Get remaining actions for today."""
        limit = PLAN_DAILY_LIMITS.get(subscription.plan, PLAN_DAILY_LIMITS[Plan.FREE])
        return max(0, limit - subscription.used_today)

    def get_limits(self, *, plan: Plan) -> dict[str, int]:
        """Get all limits for a plan."""
        return {
            "daily_applications": PLAN_DAILY_LIMITS.get(plan, PLAN_DAILY_LIMITS[Plan.FREE]),
            "concurrent_operations": PLAN_CONCURRENT_LIMITS.get(
                plan, PLAN_CONCURRENT_LIMITS[Plan.FREE]
            ),
        }
