from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.services.iap_service import iap_service
from app.repositories.user_repository import UserRepository
from app.core.database import get_db
from app.models import Purchase, Subscription, SubscriptionTier
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AppleReceiptRequest(BaseModel):
    user_id: str
    receipt_data: str
    product_id: str

class GoogleReceiptRequest(BaseModel):
    user_id: str
    package_name: str
    product_id: str
    purchase_token: str

@router.post("/validate/apple")
async def validate_apple_purchase(
    request: AppleReceiptRequest,
    db: Session = Depends(get_db)
):
    """
    Validate Apple In-App Purchase receipt.
    """
    # Validate receipt
    result = await iap_service.validate_apple_receipt(request.receipt_data)
    
    if not result or not result.get("is_valid"):
        raise HTTPException(status_code=400, detail="Invalid receipt")
    
    # Check if already processed
    existing = db.query(Purchase).filter(
        Purchase.transaction_id == result["transaction_id"]
    ).first()
    
    if existing:
        return {"status": "already_processed", "purchase": existing}
    
    # Process purchase
    credits = iap_service.get_product_credits(request.product_id)
    is_premium = iap_service.is_premium_product(request.product_id)
    
    # Record purchase
    purchase = Purchase(
        user_id=request.user_id,
        product_id=request.product_id,
        amount=0,  # Price not available from receipt
        currency="USD",
        credits_added=credits,
        payment_method="app_store",
        transaction_id=result["transaction_id"],
        receipt_data={"receipt": request.receipt_data},
        status="completed",
        completed_at=datetime.now()
    )
    db.add(purchase)
    
    # Add credits
    if credits > 0:
        user_repo = UserRepository(db)
        # Kredi ekleme (negatif tüketim)
        user_repo.consume_credits(request.user_id, -credits)
    
    # Add premium if subscription
    if is_premium:
        # Create or update subscription
        expires_at = datetime.now() + timedelta(days=30 if "monthly" in request.product_id else 365)
        
        subscription = Subscription(
            user_id=request.user_id,
            plan=request.product_id,
            status="active",
            started_at=datetime.now(),
            expires_at=expires_at,
            subscription_id=result["transaction_id"],
            auto_renew=True
        )
        db.add(subscription)
        
        # Update user
        # Update user
        user_repo.update_subscription(request.user_id, SubscriptionTier.PREMIUM)
    
    db.commit()
    
    logger.info(f"Processed Apple purchase for user {request.user_id}")
    
    return {
        "status": "success",
        "credits_added": credits,
        "is_premium": is_premium
    }

@router.post("/validate/google")
async def validate_google_purchase(
    request: GoogleReceiptRequest,
    db: Session = Depends(get_db)
):
    """
    Validate Google Play Store purchase.
    """
    # Validate receipt
    result = await iap_service.validate_google_receipt(
        package_name=request.package_name,
        product_id=request.product_id,
        purchase_token=request.purchase_token
    )
    
    if not result or not result.get("is_valid"):
        raise HTTPException(status_code=400, detail="Invalid receipt")
    
    # Check if already processed
    existing = db.query(Purchase).filter(
        Purchase.transaction_id == result["purchase_token"]
    ).first()
    
    if existing:
        return {"status": "already_processed", "purchase": existing}
    
    # Process purchase (same as Apple)
    credits = iap_service.get_product_credits(request.product_id)
    is_premium = iap_service.is_premium_product(request.product_id)
    
    # Record purchase
    purchase = Purchase(
        user_id=request.user_id,
        product_id=request.product_id,
        amount=0,
        currency="USD",
        credits_added=credits,
        payment_method="google_play",
        transaction_id=result["purchase_token"],
        receipt_data={"token": request.purchase_token},
        status="completed",
        completed_at=datetime.now()
    )
    db.add(purchase)
    
    # Add credits
    if credits > 0:
        user_repo = UserRepository(db)
        user_repo.consume_credits(request.user_id, -credits)
    
    # Add premium
    if is_premium:
        expires_at = datetime.now() + timedelta(days=30 if "monthly" in request.product_id else 365)
        
        subscription = Subscription(
            user_id=request.user_id,
            plan=request.product_id,
            status="active",
            started_at=datetime.now(),
            expires_at=expires_at,
            subscription_id=result["purchase_token"],
            auto_renew=True
        )
        db.add(subscription)
        
        user_repo = UserRepository(db)
        user_repo.update_subscription(request.user_id, SubscriptionTier.PREMIUM)
    
    db.commit()
    
    logger.info(f"Processed Google purchase for user {request.user_id}")
    
    return {
        "status": "success",
        "credits_added": credits,
        "is_premium": is_premium
    }
