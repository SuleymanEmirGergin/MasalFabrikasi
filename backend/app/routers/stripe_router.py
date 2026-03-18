from fastapi import APIRouter, HTTPException, Header, Request, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.stripe_service import stripe_service
from app.repositories.user_repository import UserRepository
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models import Purchase, Subscription, UserProfile, SubscriptionTier, SubscriptionStatus
from app.core.rate_limiter import limiter
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CreatePaymentRequest(BaseModel):
    product_id: str
    user_id: str

class CreateSubscriptionRequest(BaseModel):
    product_id: str
    user_id: str
    payment_method_id: str

@router.post("/create-payment-intent")
async def create_payment_intent(request: CreatePaymentRequest):
    """
    Create a Stripe Payment Intent for credit purchase.
    """
    try:
        intent = stripe_service.create_payment_intent(
            product_id=request.product_id,
            user_id=request.user_id
        )
        return intent
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create-subscription")
async def create_subscription(request: CreateSubscriptionRequest):
    """
    Create a Stripe Subscription for premium access.
    """
    try:
        subscription = stripe_service.create_subscription(
            product_id=request.product_id,
            user_id=request.user_id,
            payment_method_id=request.payment_method_id
        )
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
@limiter.exempt
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks for payment confirmations. Exempt from rate limit (called by Stripe).
    """
    payload = await request.body()
    
    # Verify webhook
    event = stripe_service.verify_webhook(payload, stripe_signature)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event["type"]
    data = event["data"]["object"]
    
    logger.info(f"Received Stripe webhook: {event_type}")
    
    # Handle payment_intent.succeeded
    if event_type == "payment_intent.succeeded":
        await handle_payment_success(data, db)
    
    # Handle subscription events
    elif event_type == "customer.subscription.created":
        await handle_subscription_created(data, db)
    
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data, db)
    
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_cancelled(data, db)
    
    return {"status": "success"}

async def handle_payment_success(payment_intent: dict, db: Session):
    """Handle successful payment."""
    metadata = payment_intent.get("metadata", {})
    user_id = metadata.get("user_id")
    product_id = metadata.get("product_id")
    credits = int(metadata.get("credits", 0))
    
    if not user_id or not product_id:
        logger.error("Missing metadata in payment intent")
        return

    user_repo = UserRepository(db)
    try:
        profile = user_repo.get_profile_by_auth_id(UUID(user_id))
    except (ValueError, TypeError):
        profile = None
    if not profile:
        logger.error(f"No profile for user_id {user_id}; cannot record purchase or add credits")
        db.rollback()
        return

    purchase = Purchase(
        user_id=profile.id,
        product_id=product_id,
        amount=payment_intent["amount"] / 100,
        currency=payment_intent["currency"].upper(),
        credits_added=credits,
        payment_method="stripe",
        transaction_id=payment_intent["id"],
        status="completed",
        completed_at=datetime.now()
    )
    db.add(purchase)
    if credits > 0:
        try:
            user_repo.consume_credits(profile.id, -credits)
            logger.info(f"Added {credits} credits to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add credits to user {user_id}: {e}")
    db.commit()

async def handle_subscription_created(subscription: dict, db: Session):
    """Handle subscription creation. Metadata user_id is Supabase auth_user_id."""
    metadata = subscription.get("metadata", {})
    auth_user_id_str = metadata.get("user_id")
    product_id = metadata.get("product_id")
    
    if not auth_user_id_str:
        logger.error("Missing user_id in subscription metadata")
        return
    
    user_repo = UserRepository(db)
    try:
        profile = user_repo.get_profile_by_auth_id(UUID(auth_user_id_str))
    except (ValueError, TypeError):
        logger.error(f"Invalid user_id in subscription metadata: {auth_user_id_str}")
        return
    if not profile:
        logger.error(f"No profile found for auth_user_id {auth_user_id_str}")
        return

    period_end = datetime.fromtimestamp(subscription["current_period_end"])
    period_start = datetime.fromtimestamp(subscription["current_period_start"]) if subscription.get("current_period_start") else datetime.now()

    db_subscription = Subscription(
        user_id=profile.id,
        plan_type=SubscriptionTier.PREMIUM,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=period_start,
        current_period_end=period_end,
        stripe_subscription_id=subscription["id"],
    )
    db.add(db_subscription)
    user_repo.update_subscription(profile.id, SubscriptionTier.PREMIUM)

    db.commit()
    logger.info(f"Created subscription for user {auth_user_id_str}")

def _stripe_status_to_enum(status: str) -> SubscriptionStatus:
    """Map Stripe subscription status string to SubscriptionStatus."""
    m = {"active": SubscriptionStatus.ACTIVE, "canceled": SubscriptionStatus.CANCELLED, "cancelled": SubscriptionStatus.CANCELLED, "past_due": SubscriptionStatus.PAST_DUE, "trialing": SubscriptionStatus.TRIALING}
    return m.get(status, SubscriptionStatus.ACTIVE)


async def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription updates."""
    subscription_id = subscription["id"]
    db_subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    if db_subscription:
        db_subscription.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
        if subscription.get("current_period_start"):
            db_subscription.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
        db_subscription.status = _stripe_status_to_enum(subscription.get("status", "active"))
        db.commit()
        logger.info(f"Updated subscription {subscription_id}")

async def handle_subscription_cancelled(subscription: dict, db: Session):
    """Handle subscription cancellation."""
    subscription_id = subscription["id"]
    db_subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    if db_subscription:
        db_subscription.status = SubscriptionStatus.CANCELLED
        db_subscription.cancelled_at = datetime.now()
        user_repo = UserRepository(db)
        user_repo.update_subscription(db_subscription.user_id, SubscriptionTier.FREE)
        db.commit()
        logger.info(f"Cancelled subscription for user {db_subscription.user_id}")

@router.get("/products")
async def get_products():
    """Get all available products and pricing."""
    return stripe_service.get_products()
