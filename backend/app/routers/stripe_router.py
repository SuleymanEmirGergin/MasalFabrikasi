from fastapi import APIRouter, HTTPException, Header, Request, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.stripe_service import stripe_service
from app.repositories.user_repository import UserRepository
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models import Purchase, Subscription, UserProfile, ProcessedStripeEvent
from app.core.business_metrics import stripe_webhooks_total, stripe_webhook_failures_total
from datetime import datetime, timedelta
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
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks for payment confirmations.
    """
    # Read payload first (awaitable)
    payload = await request.body()
    
    # Process webhook
    return await process_webhook_async(payload, stripe_signature, db)

async def process_webhook_async(payload, stripe_signature, db):
    # Verify webhook
    event = stripe_service.verify_webhook(payload, stripe_signature)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_id = event["id"]

    # Idempotency check
    existing_event = db.query(ProcessedStripeEvent).filter(ProcessedStripeEvent.event_id == event_id).first()
    if existing_event:
        logger.info(f"Event {event_id} already processed. Skipping.")
        stripe_webhooks_total.labels(event_type=event["type"], status="skipped").inc()
        return {"status": "skipped", "reason": "already processed"}

    event_type = event["type"]
    data = event["data"]["object"]
    
    logger.info(f"Received Stripe webhook: {event_type} (ID: {event_id})")
    
    try:
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

        # Record processed event
        processed_event = ProcessedStripeEvent(event_id=event_id)
        db.add(processed_event)
        db.commit()
        stripe_webhooks_total.labels(event_type=event_type, status="processed").inc()

    except Exception as e:
        logger.error(f"Error processing webhook {event_id}: {e}")
        stripe_webhook_failures_total.labels(event_type=event_type).inc()
        raise HTTPException(status_code=500, detail="Internal server error")
    
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
    
    # Record purchase
    purchase = Purchase(
        user_id=user_id,
        product_id=product_id,
        amount=payment_intent["amount"] / 100,  # Convert from cents
        currency=payment_intent["currency"].upper(),
        credits_added=credits,
        payment_method="stripe",
        transaction_id=payment_intent["id"],
        status="completed",
        completed_at=datetime.now()
    )
    db.add(purchase)
    
    # Add credits to user
    if credits > 0:
        user_repo = UserRepository(db)
        # Auth ID ve User ID ayrımına dikkat (Auth ID -> UUID mapping gerekirse)
        # Şimdilik direkt UUID kabul ediyoruz.
        try:
            user_profile = user_repo.get_profile(user_id)
            if user_profile:
                user_repo.consume_credits(user_profile.id, -credits)
                logger.info(f"Added {credits} credits to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add credits to user {user_id}: {e}")
    
    db.commit()

async def handle_subscription_created(subscription: dict, db: Session):
    """Handle subscription creation."""
    metadata = subscription.get("metadata", {})
    user_id = metadata.get("user_id")
    product_id = metadata.get("product_id")
    
    if not user_id:
        logger.error("Missing user_id in subscription metadata")
        return
    
    # Create subscription record
    expires_at = datetime.fromtimestamp(subscription["current_period_end"])
    
    db_subscription = Subscription(
        user_id=user_id,
        plan=product_id,
        status="active",
        started_at=datetime.now(),
        expires_at=expires_at,
        subscription_id=subscription["id"],
        auto_renew=True
    )
    db.add(db_subscription)
    
    # Update user to premium
    user_repo = UserRepository(db)
    user_repo.update_subscription(user_id, SubscriptionTier.PREMIUM)
    
    db.commit()
    logger.info(f"Created subscription for user {user_id}")

async def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription updates."""
    subscription_id = subscription["id"]
    
    db_subscription = db.query(Subscription).filter(
        Subscription.subscription_id == subscription_id
    ).first()
    
    if db_subscription:
        db_subscription.expires_at = datetime.fromtimestamp(subscription["current_period_end"])
        db_subscription.status = subscription["status"]
        db.commit()
        logger.info(f"Updated subscription {subscription_id}")

async def handle_subscription_cancelled(subscription: dict, db: Session):
    """Handle subscription cancellation."""
    subscription_id = subscription["id"]
    
    db_subscription = db.query(Subscription).filter(
        Subscription.subscription_id == subscription_id
    ).first()
    
    if db_subscription:
        db_subscription.status = "cancelled"
        db_subscription.cancelled_at = datetime.now()
        db_subscription.auto_renew = False
        
        # Remove premium status
        user_repo = UserRepository(db)
        user_repo.update_subscription(db_subscription.user_id, SubscriptionTier.FREE)
        
        db.commit()
        logger.info(f"Cancelled subscription for user {db_subscription.user_id}")

@router.get("/products")
async def get_products():
    """Get all available products and pricing."""
    return stripe_service.get_products()
