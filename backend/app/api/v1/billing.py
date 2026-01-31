"""Billing endpoints.

Standards: python_clean.mdc
- Stripe integration
- Webhook handling
"""

import structlog
from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.domain.subscription import PLAN_CONCURRENT_LIMITS, PLAN_DAILY_LIMITS, Plan
from app.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PlanDetails,
    PlansResponse,
    PortalResponse,
    UsageResponse,
)

router = APIRouter()
logger = structlog.get_logger()


@router.get("/plans", response_model=PlansResponse)
async def list_plans() -> PlansResponse:
    """List available subscription plans."""
    plans = [
        PlanDetails(
            id="free",
            name="Free",
            price_monthly=0,
            price_yearly=0,
            daily_apply_limit=PLAN_DAILY_LIMITS[Plan.FREE],
            concurrent_limit=PLAN_CONCURRENT_LIMITS[Plan.FREE],
            features=[
                "5 applications per day",
                "Basic job matching",
                "Manual review required",
            ],
        ),
        PlanDetails(
            id="premium",
            name="Premium",
            price_monthly=2990,  # $29.90
            price_yearly=29900,  # $299.00
            daily_apply_limit=PLAN_DAILY_LIMITS[Plan.PREMIUM],
            concurrent_limit=PLAN_CONCURRENT_LIMITS[Plan.PREMIUM],
            features=[
                "20 applications per day",
                "AI-powered cover letters",
                "3 concurrent operations",
                "Priority support",
            ],
        ),
        PlanDetails(
            id="elite",
            name="Elite",
            price_monthly=3990,  # $39.90
            price_yearly=39900,  # $399.00
            daily_apply_limit=PLAN_DAILY_LIMITS[Plan.ELITE],
            concurrent_limit=PLAN_CONCURRENT_LIMITS[Plan.ELITE],
            features=[
                "50 applications per day",
                "AI-powered cover letters",
                "5 concurrent operations",
                "Priority support",
                "Resume optimization",
                "Interview preparation",
            ],
        ),
    ]

    return PlansResponse(plans=plans)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> CheckoutResponse:
    """Create Stripe checkout session."""
    import stripe

    stripe.api_key = settings.stripe_secret_key.get_secret_value()

    # Validate plan
    if request.plan not in ["premium", "elite"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan",
        )

    # Get price ID
    price_id = (
        settings.stripe_price_id_premium
        if request.plan == "premium"
        else settings.stripe_price_id_elite
    )

    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe not configured",
        )

    # Get or create Stripe customer
    from app.infra.db.repositories.subscription import SQLSubscriptionRepository

    sub_repo = SQLSubscriptionRepository(session=db)
    subscription = await sub_repo.get_by_user_id(current_user.id)

    customer_id = None
    if subscription and subscription.stripe_customer_id:
        customer_id = subscription.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=current_user.email,
            metadata={"user_id": current_user.id},
        )
        customer_id = customer.id

    # Create checkout session
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={"user_id": current_user.id, "plan": request.plan},
        )

        logger.info(
            "checkout_created",
            user_id=current_user.id,
            plan=request.plan,
            session_id=session.id,
        )

        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )

    except stripe.error.StripeError as e:
        logger.error("stripe_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment service error",
        )


@router.post("/portal", response_model=PortalResponse)
async def create_portal(
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> PortalResponse:
    """Create Stripe customer portal session."""
    import stripe

    stripe.api_key = settings.stripe_secret_key.get_secret_value()

    from app.infra.db.repositories.subscription import SQLSubscriptionRepository

    sub_repo = SQLSubscriptionRepository(session=db)
    subscription = await sub_repo.get_by_user_id(current_user.id)

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription",
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=f"{settings.app_name}/dashboard",
        )

        return PortalResponse(portal_url=session.url)

    except stripe.error.StripeError as e:
        logger.error("stripe_portal_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment service error",
        )


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: CurrentUser,
    db: DBSession,
) -> UsageResponse:
    """Get current usage and limits."""
    from app.core.services.plan_gating import PlanGatingService
    from app.infra.db.repositories.subscription import SQLSubscriptionRepository

    sub_repo = SQLSubscriptionRepository(session=db)
    subscription = await sub_repo.get_by_user_id(current_user.id)

    if not subscription:
        # Return free tier defaults
        return UsageResponse(
            plan="free",
            daily_limit=PLAN_DAILY_LIMITS[Plan.FREE],
            used_today=0,
            remaining_today=PLAN_DAILY_LIMITS[Plan.FREE],
            current_period_end=None,
            subscription_status="active",
        )

    gating = PlanGatingService()
    remaining = gating.get_remaining_today(subscription=subscription)

    return UsageResponse(
        plan=subscription.plan.value,
        daily_limit=subscription.daily_limit,
        used_today=subscription.used_today,
        remaining_today=remaining,
        current_period_end=subscription.current_period_end,
        subscription_status=subscription.status.value,
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: DBSession,
    settings: AppSettings,
) -> dict[str, str]:
    """Handle Stripe webhook events."""
    import stripe

    stripe.api_key = settings.stripe_secret_key.get_secret_value()

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret.get_secret_value(),
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    from app.infra.services.billing_service import BillingService

    billing_service = BillingService(db_session=db)

    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await billing_service.handle_checkout_completed(session)

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await billing_service.handle_subscription_updated(subscription)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await billing_service.handle_subscription_deleted(subscription)

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await billing_service.handle_payment_failed(invoice)

    logger.info("stripe_webhook_processed", event_type=event["type"])

    return {"status": "ok"}
