"""Subscription domain model.

Standards: python_clean.mdc
- Enum for plan and status
- No magic numbers for limits
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Plan(Enum):
    """Subscription plan enumeration."""

    FREE = "free"
    PREMIUM = "premium"
    ELITE = "elite"


class SubscriptionStatus(Enum):
    """Subscription status enumeration."""

    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


# Plan limits - no magic numbers
PLAN_DAILY_LIMITS: dict[Plan, int] = {
    Plan.FREE: 5,
    Plan.PREMIUM: 20,
    Plan.ELITE: 50,
}

PLAN_CONCURRENT_LIMITS: dict[Plan, int] = {
    Plan.FREE: 1,
    Plan.PREMIUM: 3,
    Plan.ELITE: 5,
}


@dataclass
class Subscription:
    """User subscription domain entity."""

    id: str
    user_id: str
    plan: Plan = Plan.FREE
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    daily_limit: int = PLAN_DAILY_LIMITS[Plan.FREE]
    used_today: int = 0
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
