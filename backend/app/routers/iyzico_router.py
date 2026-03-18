"""
iyzico ödeme API – Checkout Form ile tek seferlik ödemeler.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from app.services.iyzico_service import iyzico_service
from app.repositories.user_repository import UserRepository
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models import Purchase, Subscription, UserProfile, SubscriptionTier, SubscriptionStatus
from app.core.rate_limiter import limiter
from datetime import datetime
from uuid import UUID
import calendar
import logging


def _add_months(dt: datetime, months: int) -> datetime:
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

logger = logging.getLogger(__name__)
router = APIRouter()


class CreateCheckoutRequest(BaseModel):
    product_id: str
    user_id: str
    callback_url: str
    buyer_email: Optional[str] = ""
    buyer_name: Optional[str] = "Kullanıcı"
    locale: Optional[str] = "tr"


@router.post("/create-checkout")
async def create_checkout(request: CreateCheckoutRequest):
    """
    iyzico Checkout Form başlatır. Dönen paymentPageUrl'ye yönlendirilir;
    ödeme sonrası callback_url çağrılır (token query ile).
    """
    if not iyzico_service.is_available():
        raise HTTPException(status_code=503, detail="iyzico yapılandırılmamış")
    try:
        result = iyzico_service.create_checkout_form(
            product_id=request.product_id,
            user_id=request.user_id,
            callback_url=request.callback_url,
            buyer_email=request.buyer_email or "",
            buyer_name=request.buyer_name or "Kullanıcı",
            locale=request.locale or "tr",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("create_checkout: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
@limiter.exempt
async def payment_callback(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    iyzico ödeme sonrası kullanıcıyı bu URL'ye yönlendirir (token query ile).
    Ödeme başarılıysa Purchase kaydı ve kredi/abonelik güncellenir. Rate limit yok (iyzico sunucusu çağırır).
    """
    if not token:
        raise HTTPException(status_code=400, detail="token gerekli")
    result = iyzico_service.retrieve_checkout_form(token)
    if not result:
        raise HTTPException(status_code=400, detail="Ödeme sonucu alınamadı")
    if result.get("status") != "success" or result.get("paymentStatus") != "SUCCESS":
        logger.warning("iyzico callback failed: %s", result)
        raise HTTPException(status_code=400, detail=result.get("errorMessage", "Ödeme başarısız"))
    conversation_id = result.get("conversationId") or ""
    if "|" in conversation_id:
        user_id_str, product_id = conversation_id.split("|", 1)
    else:
        logger.error("conversationId format hatası: %s", conversation_id)
        raise HTTPException(status_code=400, detail="Geçersiz ödeme verisi")
    product = iyzico_service.PRODUCTS.get(product_id)
    if not product:
        raise HTTPException(status_code=400, detail="Geçersiz ürün")
    paid_price = float(result.get("paidPrice", 0))
    credits = product.get("credits", 0)
    payment_id = result.get("paymentId") or token[:50]
    user_repo = UserRepository(db)
    try:
        profile = user_repo.get_profile_by_auth_id(UUID(user_id_str))
    except (ValueError, TypeError):
        profile = None
    if not profile:
        logger.error("Profil bulunamadı: %s", user_id_str)
        raise HTTPException(status_code=400, detail="Kullanıcı bulunamadı")
    purchase = Purchase(
        user_id=profile.id,
        product_id=product_id,
        amount=paid_price,
        currency=result.get("currency", "TRY"),
        credits_added=credits,
        payment_method="iyzico",
        transaction_id=payment_id,
        status="completed",
        completed_at=datetime.now(),
    )
    db.add(purchase)
    if credits > 0:
        try:
            user_repo.consume_credits(profile.id, -credits)
            logger.info("Kredi eklendi: user=%s credits=%s", user_id_str, credits)
        except Exception as e:
            logger.exception("Kredi eklenemedi: %s", e)
    if product.get("type") == "subscription":
        period_months = 12 if "yearly" in product_id else 1
        period_end = _add_months(datetime.now(), period_months)
        db_sub = Subscription(
            user_id=profile.id,
            plan_type=SubscriptionTier.PREMIUM,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.now(),
            current_period_end=period_end,
            stripe_subscription_id=f"iyzico_{payment_id}",
        )
        db.add(db_sub)
        user_repo.update_subscription(profile.id, SubscriptionTier.PREMIUM)
    db.commit()
    return {"status": "success", "message": "Ödeme işlendi", "product_id": product_id}


@router.get("/products")
async def get_products():
    """Tüm ürünleri ve fiyatları döner."""
    return iyzico_service.get_products()
