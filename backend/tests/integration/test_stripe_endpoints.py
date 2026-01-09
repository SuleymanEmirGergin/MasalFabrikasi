"""
Integration tests for Stripe API Endpoints

Tests cover:
- Payment intent creation endpoint
- Subscription creation endpoint
- Webhook handler endpoint
- Products listing endpoint
"""
import pytest
import json


@pytest.mark.integration
class TestPaymentIntentEndpoint:
    """Tests for POST /api/stripe/create-payment-intent endpoint."""
    
    def test_payment_intent_endpoint_exists(self, client):
        """Test that payment intent endpoint exists."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={
                "product_id": "credits_100",
                "user_id": "test_user"
            }
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    def test_payment_intent_missing_product_id(self, client):
        """Test payment intent without product_id."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={
                "user_id": "test_user"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_payment_intent_missing_user_id(self, client):
        """Test payment intent without user_id."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={
                "product_id": "credits_100"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_payment_intent_invalid_product(self, client):
        """Test payment intent with invalid product."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={
                "product_id": "invalid_product",
                "user_id": "test_user"
            }
        )
        
        # Should return 400 (bad request)
        assert response.status_code == 400


@pytest.mark.integration
class TestSubscriptionEndpoint:
    """Tests for POST /api/stripe/create-subscription endpoint."""
    
    def test_subscription_endpoint_exists(self, client):
        """Test that subscription endpoint exists."""
        response = client.post(
            "/api/stripe/create-subscription",
            json={
                "product_id": "premium_monthly",
                "user_id": "test_user",
                "payment_method_id": "pm_test_123"
            }
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    def test_subscription_missing_payment_method(self, client):
        """Test subscription without payment_method_id."""
        response = client.post(
            "/api/stripe/create-subscription",
            json={
                "product_id": "premium_monthly",
                "user_id": "test_user"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_subscription_invalid_product(self, client):
        """Test subscription with invalid product."""
        response = client.post(
            "/api/stripe/create-subscription",
            json={
                "product_id": "invalid_subscription",
                "user_id": "test_user",
                "payment_method_id": "pm_test_123"
            }
        )
        
        # Should return 400
        assert response.status_code == 400


@pytest.mark.integration
class TestWebhookEndpoint:
    """Tests for POST /api/stripe/webhook endpoint."""
    
    def test_webhook_endpoint_exists(self, client):
        """Test that webhook endpoint exists."""
        response = client.post(
            "/api/stripe/webhook",
            data=json.dumps({"type": "test"}),
            headers={"Content-Type": "application/json"}
        )
        
        # Should not return 404 (400 is ok - invalid signature)
        assert response.status_code != 404
    
    def test_webhook_without_signature(self, client):
        """Test webhook without Stripe signature header."""
        response = client.post(
            "/api/stripe/webhook",
            data=json.dumps({
                "type": "payment_intent.succeeded",
                "data": {"object": {"id": "pi_123"}}
            }),
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 400 (invalid signature)
        assert response.status_code == 400
    
    def test_webhook_with_invalid_signature(self, client):
        """Test webhook with invalid signature."""
        response = client.post(
            "/api/stripe/webhook",
            data=json.dumps({
                "type": "payment_intent.succeeded",
                "data": {"object": {"id": "pi_123"}}
            }),
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "invalid_signature"
            }
        )
        
        # Should return 400 (invalid signature)
        assert response.status_code == 400
    
    def test_webhook_empty_body(self, client):
        """Test webhook with empty body."""
        response = client.post(
            "/api/stripe/webhook",
            data="",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return error
        assert response.status_code in [400, 422]


@pytest.mark.integration
class TestProductsEndpoint:
    """Tests for GET /api/stripe/products endpoint."""
    
    def test_products_endpoint_exists(self, client):
        """Test that products endpoint exists."""
        response = client.get("/api/stripe/products")
        
        # Should return 200
        assert response.status_code == 200
    
    def test_products_returns_json(self, client):
        """Test that products returns JSON."""
        response = client.get("/api/stripe/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data is not None
    
    def test_products_has_items(self, client):
        """Test that products list is not empty."""
        response = client.get("/api/stripe/products")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_products_structure(self, client):
        """Test products response structure."""
        response = client.get("/api/stripe/products")
        
        assert response.status_code == 200
        data = response.json()
        
        # Each product should have name, price, currency
        for product_id, product in data.items():
            assert "name" in product
            assert "price" in product
            assert "currency" in product


@pytest.mark.integration
class TestStripeEndpointValidation:
    """Tests for input validation on Stripe endpoints."""
    
    def test_payment_intent_empty_json(self, client):
        """Test payment intent with empty JSON."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_subscription_empty_json(self, client):
        """Test subscription with empty JSON."""
        response = client.post(
            "/api/stripe/create-subscription",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_payment_intent_with_null_values(self, client):
        """Test payment intent with null values."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={
                "product_id": None,
                "user_id": None
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_payment_intent_sql_injection(self, client):
        """Test payment intent with SQL injection attempt."""
        response = client.post(
            "/api/stripe/create-payment-intent",
            json={
                "product_id": "'; DROP TABLE products; --",
                "user_id": "test_user"
            }
        )
        
        # Should return 400 (invalid product) not crash
        assert response.status_code == 400


@pytest.mark.integration
class TestStripeEndpointSecurity:
    """Tests for security on Stripe endpoints."""
    
    def test_products_no_auth_required(self, client):
        """Test that products endpoint is public."""
        response = client.get("/api/stripe/products")
        
        # Products should be public
        assert response.status_code == 200
    
    def test_webhook_accepts_post_only(self, client):
        """Test that webhook only accepts POST."""
        get_response = client.get("/api/stripe/webhook")
        
        # GET should not be allowed
        assert get_response.status_code in [405, 404]
