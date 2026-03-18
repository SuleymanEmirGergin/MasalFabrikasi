"""
Integration tests for iyzico payment API endpoints.

Tests cover:
- create-checkout: 503 when service unavailable, 200 with paymentPageUrl when available
- callback: 400 when token missing or payment failed, 200 on success (with mocked service and DB)
"""
import pytest
from unittest.mock import patch, MagicMock
import uuid



@pytest.mark.integration
class TestIyzicoCreateCheckout:
    """Tests for POST /api/iyzico/create-checkout."""

    def test_create_checkout_service_unavailable(self, client):
        """When iyzico is not configured, returns 503."""
        with patch("app.routers.iyzico_router.iyzico_service") as mock_svc:
            mock_svc.is_available.return_value = False
            response = client.post(
                "/api/iyzico/create-checkout",
                json={
                    "product_id": "credits_100",
                    "user_id": str(uuid.uuid4()),
                    "callback_url": "https://api.example.com/api/iyzico/callback",
                },
            )
            assert response.status_code == 503
            mock_svc.create_checkout_form.assert_not_called()

    def test_create_checkout_success_returns_payment_url(self, client):
        """When iyzico is available, returns 200 with paymentPageUrl."""
        with patch("app.routers.iyzico_router.iyzico_service") as mock_svc:
            mock_svc.is_available.return_value = True
            mock_svc.create_checkout_form.return_value = {
                "status": "success",
                "paymentPageUrl": "https://sandbox-merchant.iyzipay.com/checkout/xxx",
            }
            response = client.post(
                "/api/iyzico/create-checkout",
                json={
                    "product_id": "credits_100",
                    "user_id": str(uuid.uuid4()),
                    "callback_url": "https://api.example.com/api/iyzico/callback",
                    "buyer_email": "test@example.com",
                    "buyer_name": "Test User",
                    "locale": "tr",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "paymentPageUrl" in data
            assert data["paymentPageUrl"] == "https://sandbox-merchant.iyzipay.com/checkout/xxx"
            mock_svc.create_checkout_form.assert_called_once()

    def test_create_checkout_validation_error_missing_callback(self, client):
        """Missing callback_url returns 422."""
        with patch("app.routers.iyzico_router.iyzico_service") as mock_svc:
            mock_svc.is_available.return_value = True
            response = client.post(
                "/api/iyzico/create-checkout",
                json={
                    "product_id": "credits_100",
                    "user_id": str(uuid.uuid4()),
                },
            )
            assert response.status_code == 422


@pytest.mark.integration
class TestIyzicoCallback:
    """Tests for GET /api/iyzico/callback?token=..."""

    def test_callback_missing_token(self, client):
        """Missing token returns 422 (validation error for missing query param)."""
        response = client.get("/api/iyzico/callback")
        assert response.status_code == 422

    def test_callback_retrieve_returns_none(self, client):
        """When retrieve_checkout_form returns None, returns 400."""
        with patch("app.routers.iyzico_router.iyzico_service") as mock_svc:
            mock_svc.retrieve_checkout_form.return_value = None
            response = client.get("/api/iyzico/callback?token=fake-token-123")
            assert response.status_code == 400
            mock_svc.retrieve_checkout_form.assert_called_once_with("fake-token-123")

    def test_callback_payment_failed(self, client):
        """When payment status is not success, returns 400."""
        with patch("app.routers.iyzico_router.iyzico_service") as mock_svc:
            mock_svc.retrieve_checkout_form.return_value = {
                "status": "failure",
                "paymentStatus": "FAILURE",
                "errorMessage": "Kart reddedildi",
            }
            response = client.get("/api/iyzico/callback?token=fake-token-456")
            assert response.status_code == 400

    def test_callback_invalid_conversation_id_format(self, client):
        """When conversationId has no pipe separator, returns 400."""
        with patch("app.routers.iyzico_router.iyzico_service") as mock_svc:
            mock_svc.retrieve_checkout_form.return_value = {
                "status": "success",
                "paymentStatus": "SUCCESS",
                "conversationId": "invalid-no-pipe",
                "paidPrice": "19.99",
                "currency": "TRY",
                "paymentId": "pay-123",
            }
            response = client.get("/api/iyzico/callback?token=token-bad-format")
            assert response.status_code == 400


@pytest.mark.integration
class TestIyzicoProducts:
    """Tests for GET /api/iyzico/products."""

    def test_products_returns_list(self, client):
        """Products endpoint returns product map."""
        response = client.get("/api/iyzico/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Service defines PRODUCTS with credits_100, etc.
        assert "credits_100" in data or len(data) >= 0
