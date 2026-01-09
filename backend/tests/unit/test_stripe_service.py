"""
Unit tests for StripeService

Tests cover:
- Payment intent creation
- Subscription creation
- Webhook verification
- Product listing
"""
import pytest
from unittest.mock import patch, MagicMock
import json

from app.services.stripe_service import StripeService, stripe_service


class TestProductsConfiguration:
    """Tests for product configuration."""
    
    def test_products_exist(self):
        """Test that products are defined."""
        products = StripeService.PRODUCTS
        
        assert products is not None
        assert len(products) > 0
    
    def test_credit_products_exist(self):
        """Test that credit products exist."""
        products = StripeService.PRODUCTS
        
        credit_products = [k for k in products.keys() if "credits" in k]
        assert len(credit_products) > 0
    
    def test_subscription_products_exist(self):
        """Test that subscription products exist."""
        products = StripeService.PRODUCTS
        
        subscription_products = [
            k for k, v in products.items() 
            if v.get("type") == "subscription"
        ]
        assert len(subscription_products) > 0
    
    def test_products_have_required_fields(self):
        """Test that all products have required fields."""
        products = StripeService.PRODUCTS
        
        required_fields = ["name", "credits", "price", "currency"]
        
        for product_id, product in products.items():
            for field in required_fields:
                assert field in product, f"{product_id} missing {field}"
    
    def test_products_have_valid_prices(self):
        """Test that all products have positive prices."""
        products = StripeService.PRODUCTS
        
        for product_id, product in products.items():
            assert product["price"] > 0, f"{product_id} has invalid price"
    
    def test_products_have_valid_currency(self):
        """Test that all products have valid currency."""
        products = StripeService.PRODUCTS
        valid_currencies = ["TRY", "USD", "EUR"]
        
        for product_id, product in products.items():
            assert product["currency"] in valid_currencies


class TestPaymentIntentCreation:
    """Tests for payment intent creation."""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create):
        """Test successful payment intent creation."""
        mock_create.return_value = MagicMock(
            client_secret="pi_secret_123",
            id="pi_123"
        )
        
        result = StripeService.create_payment_intent(
            product_id="credits_100",
            user_id="user_123"
        )
        
        assert result is not None
        assert "client_secret" in result
        assert "payment_intent_id" in result
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_with_metadata(self, mock_create):
        """Test payment intent with custom metadata."""
        mock_create.return_value = MagicMock(
            client_secret="pi_secret_123",
            id="pi_123"
        )
        
        result = StripeService.create_payment_intent(
            product_id="credits_100",
            user_id="user_123",
            metadata={"campaign": "summer_sale"}
        )
        
        assert result is not None
        mock_create.assert_called_once()
    
    def test_create_payment_intent_invalid_product(self):
        """Test payment intent with invalid product."""
        with pytest.raises(ValueError) as exc_info:
            StripeService.create_payment_intent(
                product_id="invalid_product",
                user_id="user_123"
            )
        
        assert "Invalid product" in str(exc_info.value)
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_amount_conversion(self, mock_create):
        """Test that amount is converted to cents correctly."""
        mock_create.return_value = MagicMock(
            client_secret="pi_secret_123",
            id="pi_123"
        )
        
        StripeService.create_payment_intent(
            product_id="credits_100",
            user_id="user_123"
        )
        
        # Get the call arguments
        call_args = mock_create.call_args
        amount = call_args[1]["amount"]
        
        # credits_100 is 19.99 TRY = 1999 cents
        expected_amount = int(StripeService.PRODUCTS["credits_100"]["price"] * 100)
        assert amount == expected_amount


class TestSubscriptionCreation:
    """Tests for subscription creation."""
    
    @patch('stripe.Subscription.create')
    @patch('stripe.Price.create')
    @patch('stripe.Customer.create')
    def test_create_subscription_success(
        self, mock_customer, mock_price, mock_subscription
    ):
        """Test successful subscription creation."""
        mock_customer.return_value = MagicMock(id="cus_123")
        mock_price.return_value = MagicMock(id="price_123")
        mock_subscription.return_value = MagicMock(
            id="sub_123",
            status="active",
            current_period_end=1704067200
        )
        
        result = StripeService.create_subscription(
            product_id="premium_monthly",
            user_id="user_123",
            payment_method_id="pm_123"
        )
        
        assert result is not None
        assert "subscription_id" in result
        assert "customer_id" in result
    
    def test_create_subscription_invalid_product(self):
        """Test subscription with invalid product."""
        with pytest.raises(ValueError) as exc_info:
            StripeService.create_subscription(
                product_id="invalid_product",
                user_id="user_123",
                payment_method_id="pm_123"
            )
        
        assert "Invalid product" in str(exc_info.value)
    
    def test_create_subscription_non_subscription_product(self):
        """Test subscription with non-subscription product."""
        with pytest.raises(ValueError) as exc_info:
            StripeService.create_subscription(
                product_id="credits_100",  # This is not a subscription
                user_id="user_123",
                payment_method_id="pm_123"
            )
        
        assert "not a subscription" in str(exc_info.value)


class TestWebhookVerification:
    """Tests for webhook signature verification."""
    
    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_success(self, mock_construct):
        """Test successful webhook verification."""
        mock_event = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_123"}}
        }
        mock_construct.return_value = mock_event
        
        result = StripeService.verify_webhook(
            payload=b'{"test": "payload"}',
            signature="valid_signature"
        )
        
        assert result is not None
        assert result["type"] == "payment_intent.succeeded"
    
    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_invalid_signature(self, mock_construct):
        """Test webhook with invalid signature."""
        import stripe
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "sig_header"
        )
        
        result = StripeService.verify_webhook(
            payload=b'{"test": "payload"}',
            signature="invalid_signature"
        )
        
        assert result is None
    
    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_invalid_payload(self, mock_construct):
        """Test webhook with invalid payload."""
        mock_construct.side_effect = ValueError("Invalid payload")
        
        result = StripeService.verify_webhook(
            payload=b'invalid payload',
            signature="some_signature"
        )
        
        assert result is None


class TestSubscriptionCancellation:
    """Tests for subscription cancellation."""
    
    @patch('stripe.Subscription.delete')
    def test_cancel_subscription_success(self, mock_delete):
        """Test successful subscription cancellation."""
        mock_delete.return_value = MagicMock()
        
        result = StripeService.cancel_subscription("sub_123")
        
        assert result is True
        mock_delete.assert_called_once_with("sub_123")
    
    @patch('stripe.Subscription.delete')
    def test_cancel_subscription_failure(self, mock_delete):
        """Test subscription cancellation failure."""
        mock_delete.side_effect = Exception("Subscription not found")
        
        result = StripeService.cancel_subscription("sub_invalid")
        
        assert result is False


class TestGetProducts:
    """Tests for product listing."""
    
    def test_get_products_returns_dict(self):
        """Test that get_products returns a dictionary."""
        result = StripeService.get_products()
        
        assert isinstance(result, dict)
    
    def test_get_products_not_empty(self):
        """Test that get_products returns products."""
        result = StripeService.get_products()
        
        assert len(result) > 0
    
    def test_get_products_matches_class_products(self):
        """Test that get_products returns class PRODUCTS."""
        result = StripeService.get_products()
        
        assert result == StripeService.PRODUCTS


class TestStripeServiceInstance:
    """Tests for stripe_service instance."""
    
    def test_stripe_service_instance_exists(self):
        """Test that stripe_service instance is created."""
        assert stripe_service is not None
        assert isinstance(stripe_service, StripeService)
