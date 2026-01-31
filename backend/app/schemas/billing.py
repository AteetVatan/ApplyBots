"""Billing schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime

from pydantic import BaseModel


class PlanDetails(BaseModel):
    """Subscription plan details."""

    id: str
    name: str
    price_monthly: int  # cents
    price_yearly: int  # cents
    daily_apply_limit: int
    concurrent_limit: int
    features: list[str]


class PlansResponse(BaseModel):
    """Available subscription plans."""

    plans: list[PlanDetails]


class CheckoutRequest(BaseModel):
    """Request to create checkout session."""

    plan: str  # "premium" or "elite"
    billing_period: str = "monthly"  # "monthly" or "yearly"
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    """Checkout session response."""

    checkout_url: str
    session_id: str


class PortalResponse(BaseModel):
    """Customer portal URL response."""

    portal_url: str


class UsageResponse(BaseModel):
    """Current usage and limits."""

    plan: str
    daily_limit: int
    used_today: int
    remaining_today: int
    current_period_end: datetime | None
    subscription_status: str
