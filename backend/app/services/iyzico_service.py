"""
iyzico (iyzipay) ödeme servisi – Türkiye odaklı ödeme altyapısı.
Checkout Form ile tek seferlik ödeme (kredi paketleri, premium tek çekim).
"""
import logging
from typing import Dict, Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# iyzipay import (opsiyonel – API key yoksa servis devre dışı)
try:
    import iyzipay
    IYZIPAY_AVAILABLE = True
except ImportError:
    iyzipay = None
    IYZIPAY_AVAILABLE = False


def _options() -> Dict[str, str]:
    return {
        "api_key": settings.IYZICO_API_KEY,
        "secret_key": settings.IYZICO_SECRET_KEY,
        "base_url": settings.IYZICO_BASE_URL,
    }


class IyzicoService:
    """
    iyzico Checkout Form ile kredi ve premium satın alma.
    """

    PRODUCTS = {
        "credits_100": {
            "name": "100 Kredi",
            "credits": 100,
            "price": 19.99,
            "currency": "TRY",
        },
        "credits_500": {
            "name": "500 Kredi",
            "credits": 500,
            "price": 79.99,
            "currency": "TRY",
        },
        "credits_1000": {
            "name": "1000 Kredi",
            "credits": 1000,
            "price": 139.99,
            "currency": "TRY",
        },
        "premium_monthly": {
            "name": "Premium Aylık",
            "credits": 0,
            "price": 49.99,
            "currency": "TRY",
            "type": "subscription",
        },
        "premium_yearly": {
            "name": "Premium Yıllık",
            "credits": 0,
            "price": 399.99,
            "currency": "TRY",
            "type": "subscription",
        },
    }

    @classmethod
    def is_available(cls) -> bool:
        return bool(IYZIPAY_AVAILABLE and settings.IYZICO_API_KEY and settings.IYZICO_SECRET_KEY)

    @classmethod
    def create_checkout_form(
        cls,
        product_id: str,
        user_id: str,
        callback_url: str,
        buyer_email: str = "",
        buyer_name: str = "Kullanıcı",
        locale: str = "tr",
    ) -> Dict[str, Any]:
        """
        Checkout Form başlatır; kullanıcıyı iyzico ödeme sayfasına yönlendirmek için
        token ve paymentPageUrl döner.
        """
        if not cls.is_available():
            raise RuntimeError("iyzico yapılandırılmamış (IYZICO_API_KEY, IYZICO_SECRET_KEY)")
        if product_id not in cls.PRODUCTS:
            raise ValueError(f"Geçersiz ürün: {product_id}")

        product = cls.PRODUCTS[product_id]
        price_str = f"{product['price']:.2f}"
        # conversationId ile callback'ta user_id ve product_id geri alınır
        conversation_id = f"{user_id}|{product_id}"

        buyer = {
            "id": user_id[:50],
            "name": (buyer_name or "Kullanıcı")[:50],
            "surname": ".",
            "gsmNumber": "+905350000000",
            "email": (buyer_email or f"user_{user_id}@masalfabrikasi.com")[:100],
            "identityNumber": "11111111110",
            "lastLoginDate": "2020-01-01 00:00:00",
            "registrationDate": "2020-01-01 00:00:00",
            "registrationAddress": "Adres",
            "ip": "85.34.78.112",
            "city": "Istanbul",
            "country": "Turkey",
            "zipCode": "34732",
        }

        address = {
            "contactName": f"{buyer_name} ."[:50],
            "city": "Istanbul",
            "country": "Turkey",
            "address": "Adres",
            "zipCode": "34732",
        }

        basket_items = [
            {
                "id": product_id,
                "name": product["name"][:100],
                "category1": "Dijital",
                "category2": "Kredi" if product.get("credits") else "Abonelik",
                "itemType": "VIRTUAL",
                "price": price_str,
            }
        ]

        request = {
            "locale": locale,
            "conversationId": conversation_id,
            "price": price_str,
            "paidPrice": price_str,
            "currency": product["currency"],
            "basketId": conversation_id[:50],
            "paymentGroup": "PRODUCT",
            "callbackUrl": callback_url,
            "enabledInstallments": ["1", "2", "3", "6", "9"],
            "buyer": buyer,
            "shippingAddress": address,
            "billingAddress": address,
            "basketItems": basket_items,
        }

        try:
            result = iyzipay.CheckoutFormInitialize().create(request, _options())
            if result.get("status") == "success":
                return {
                    "token": result.get("token"),
                    "paymentPageUrl": result.get("paymentPageUrl"),
                    "checkoutFormContent": result.get("checkoutFormContent"),
                    "conversationId": conversation_id,
                }
            logger.error(f"iyzico CheckoutFormInitialize failed: {result}")
            raise RuntimeError(result.get("errorMessage", "iyzico ödeme başlatılamadı"))
        except Exception as e:
            logger.exception(f"iyzico create_checkout_form: {e}")
            raise

    @classmethod
    def retrieve_checkout_form(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Callback'tan gelen token ile ödeme sonucunu alır.
        Dönen dict: status, paidPrice, currency, conversationId, paymentId, vb.
        """
        if not cls.is_available() or not token:
            return None
        request = {"locale": "tr", "token": token}
        try:
            result = iyzipay.CheckoutForm().retrieve(request, _options())
            # result içinde status, paymentStatus, paidPrice, conversationId var
            return result
        except Exception as e:
            logger.exception(f"iyzico retrieve_checkout_form: {e}")
            return None

    @classmethod
    def get_products(cls) -> Dict:
        """Tüm ürünleri döner (Stripe ile uyumlu arayüz)."""
        return cls.PRODUCTS


iyzico_service = IyzicoService()
