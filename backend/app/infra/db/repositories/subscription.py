"""Subscription repository implementation."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.subscription import Plan, Subscription, SubscriptionStatus
from app.infra.db.models import SubscriptionModel


class SQLSubscriptionRepository:
    """SQLAlchemy implementation of SubscriptionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Subscription | None:
        """Get subscription by user ID."""
        stmt = select(SubscriptionModel).where(SubscriptionModel.user_id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_stripe_customer_id(self, customer_id: str) -> Subscription | None:
        """Get subscription by Stripe customer ID."""
        stmt = select(SubscriptionModel).where(
            SubscriptionModel.stripe_customer_id == customer_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription."""
        model = SubscriptionModel(
            id=subscription.id,
            user_id=subscription.user_id,
            plan=subscription.plan,
            status=subscription.status,
            stripe_customer_id=subscription.stripe_customer_id,
            stripe_subscription_id=subscription.stripe_subscription_id,
            daily_limit=subscription.daily_limit,
            used_today=subscription.used_today,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            created_at=subscription.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, subscription: Subscription) -> Subscription:
        """Update an existing subscription."""
        model = await self._session.get(SubscriptionModel, subscription.id)
        if model:
            model.plan = subscription.plan
            model.status = subscription.status
            model.stripe_customer_id = subscription.stripe_customer_id
            model.stripe_subscription_id = subscription.stripe_subscription_id
            model.daily_limit = subscription.daily_limit
            model.used_today = subscription.used_today
            model.current_period_start = subscription.current_period_start
            model.current_period_end = subscription.current_period_end
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Subscription {subscription.id} not found")

    async def reset_daily_usage(self) -> int:
        """Reset daily usage counters, return count of updated records."""
        stmt = (
            update(SubscriptionModel)
            .where(SubscriptionModel.used_today > 0)
            .values(used_today=0)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    def _to_domain(self, model: SubscriptionModel) -> Subscription:
        """Convert ORM model to domain entity."""
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            plan=model.plan,
            status=model.status,
            stripe_customer_id=model.stripe_customer_id,
            stripe_subscription_id=model.stripe_subscription_id,
            daily_limit=model.daily_limit,
            used_today=model.used_today,
            current_period_start=model.current_period_start,
            current_period_end=model.current_period_end,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
