import stripe
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

class StripeService:
    """
    Stripe payment service for credit purchases and premium subscriptions.
    """
    
    # Product prices (in TRY - Turkish Lira)
    PRODUCTS = {
        "credits_100": {
            "name": "100 Kredi",
            "credits": 100,
            "price": 19.99,
            "currency": "TRY"
        },
        "credits_500": {
            "name": "500 Kredi",
            "credits": 500,
            "price": 79.99,
            "currency": "TRY"
        },
        "credits_1000": {
            "name": "1000 Kredi",
            "credits": 1000,
            "price": 139.99,
            "currency": "TRY"
        },
        "premium_monthly": {
            "name": "Premium Aylık",
            "credits": 0,  # No credits, just premium access
            "price": 49.99,
            "currency": "TRY",
            "type": "subscription"
        },
        "premium_yearly": {
            "name": "Premium Yıllık",
            "credits": 0,
            "price": 399.99,
            "currency": "TRY",
            "type": "subscription"
        }
    }
    
    @staticmethod
    def create_payment_intent(
        product_id: str,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a Stripe Payment Intent for one-time purchases.
        
        Args:
            product_id: Product ID (e.g., 'credits_100')
            user_id: User ID for tracking
            metadata: Additional metadata
            
        Returns:
            Payment Intent details
        """
        if product_id not in StripeService.PRODUCTS:
            raise ValueError(f"Invalid product: {product_id}")
        
        product = StripeService.PRODUCTS[product_id]
        
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(product["price"] * 100),  # Convert to cents
                currency=product["currency"].lower(),
                metadata={
                    "product_id": product_id,
                    "user_id": user_id,
                    "credits": product["credits"],
                    **(metadata or {})
                },
                description=f"{product['name']} - User {user_id}"
            )
            
            logger.info(f"Created payment intent: {intent.id} for user {user_id}")
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": product["price"],
                "currency": product["currency"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise
    
    @staticmethod
    def create_subscription(
        product_id: str,
        user_id: str,
        payment_method_id: str
    ) -> Dict:
        """
        Create a Stripe Subscription for premium access.
        
        Args:
            product_id: Subscription product ID
            user_id: User ID
            payment_method_id: Payment method from frontend
            
        Returns:
            Subscription details
        """
        if product_id not in StripeService.PRODUCTS:
            raise ValueError(f"Invalid product: {product_id}")
        
        product = StripeService.PRODUCTS[product_id]
        
        if product.get("type") != "subscription":
            raise ValueError(f"Product {product_id} is not a subscription")
        
        try:
            # Create or get customer
            customer = stripe.Customer.create(
                payment_method=payment_method_id,
                email=f"user_{user_id}@masalfabrikasi.com",  # Replace with actual email
                invoice_settings={
                    "default_payment_method": payment_method_id
                },
                metadata={"user_id": user_id}
            )
            
            # Create price (or use existing)
            price = stripe.Price.create(
                unit_amount=int(product["price"] * 100),
                currency=product["currency"].lower(),
                recurring={
                    "interval": "month" if "monthly" in product_id else "year"
                },
                product_data={
                    "name": product["name"]
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price.id}],
                metadata={
                    "user_id": user_id,
                    "product_id": product_id
                }
            )
            
            logger.info(f"Created subscription: {subscription.id} for user {user_id}")
            
            return {
                "subscription_id": subscription.id,
                "customer_id": customer.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    @staticmethod
    def verify_webhook(payload: bytes, signature: str) -> Optional[Dict]:
        """
        Verify Stripe webhook signature and parse event.
        
        Args:
            payload: Request body
            signature: Stripe-Signature header
            
        Returns:
            Webhook event data or None
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a subscription."""
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled subscription: {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    @staticmethod
    def get_products() -> Dict:
        """Get all available products."""
        return StripeService.PRODUCTS

# Export
stripe_service = StripeService()
