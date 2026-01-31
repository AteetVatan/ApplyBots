"""Billing service for Stripe integration.

Standards: python_clean.mdc
- Handles webhook events
"""

from datetime import datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.subscription import PLAN_DAILY_LIMITS, Plan, Subscription, SubscriptionStatus
from app.infra.db.repositories.subscription import SQLSubscriptionRepository

logger = structlog.get_logger()


class BillingService:
    """Service for handling Stripe billing events."""

    def __init__(self, *, db_session: AsyncSession) -> None:
        self._db = db_session
        self._sub_repo = SQLSubscriptionRepository(session=db_session)

    async def handle_checkout_completed(self, session: dict) -> None:
        """Handle checkout.session.completed event."""
        user_id = session.get("metadata", {}).get("user_id")
        plan_name = session.get("metadata", {}).get("plan")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        if not user_id or not plan_name:
            logger.warning("checkout_missing_metadata", session_id=session.get("id"))
            return

        plan = Plan.PREMIUM if plan_name == "premium" else Plan.ELITE

        # Get or create subscription
        subscription = await self._sub_repo.get_by_user_id(user_id)

        if subscription:
            subscription.plan = plan
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.stripe_customer_id = customer_id
            subscription.stripe_subscription_id = subscription_id
            subscription.daily_limit = PLAN_DAILY_LIMITS[plan]
            await self._sub_repo.update(subscription)
        else:
            import uuid
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                plan=plan,
                status=SubscriptionStatus.ACTIVE,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                daily_limit=PLAN_DAILY_LIMITS[plan],
            )
            await self._sub_repo.create(subscription)

        logger.info(
            "subscription_created",
            user_id=user_id,
            plan=plan.value,
        )

    async def handle_subscription_updated(self, stripe_sub: dict) -> None:
        """Handle customer.subscription.updated event."""
        customer_id = stripe_sub.get("customer")

        subscription = await self._sub_repo.get_by_stripe_customer_id(customer_id)
        if not subscription:
            logger.warning("subscription_not_found", customer_id=customer_id)
            return

        # Update status
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "trialing": SubscriptionStatus.TRIALING,
        }
        stripe_status = stripe_sub.get("status", "active")
        subscription.status = status_map.get(stripe_status, SubscriptionStatus.ACTIVE)

        # Update period end
        period_end = stripe_sub.get("current_period_end")
        if period_end:
            subscription.current_period_end = datetime.fromtimestamp(period_end)

        await self._sub_repo.update(subscription)

        logger.info(
            "subscription_updated",
            user_id=subscription.user_id,
            status=subscription.status.value,
        )

    async def handle_subscription_deleted(self, stripe_sub: dict) -> None:
        """Handle customer.subscription.deleted event."""
        customer_id = stripe_sub.get("customer")

        subscription = await self._sub_repo.get_by_stripe_customer_id(customer_id)
        if not subscription:
            return

        # Downgrade to free
        subscription.plan = Plan.FREE
        subscription.status = SubscriptionStatus.CANCELED
        subscription.daily_limit = PLAN_DAILY_LIMITS[Plan.FREE]
        subscription.stripe_subscription_id = None

        await self._sub_repo.update(subscription)

        logger.info(
            "subscription_canceled",
            user_id=subscription.user_id,
        )

    async def handle_payment_failed(self, invoice: dict) -> None:
        """Handle invoice.payment_failed event."""
        customer_id = invoice.get("customer")

        subscription = await self._sub_repo.get_by_stripe_customer_id(customer_id)
        if not subscription:
            return

        subscription.status = SubscriptionStatus.PAST_DUE
        await self._sub_repo.update(subscription)

        logger.warning(
            "payment_failed",
            user_id=subscription.user_id,
        )
