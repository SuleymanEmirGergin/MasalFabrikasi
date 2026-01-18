import pytest
from unittest.mock import MagicMock, patch
from app.services.stripe_service import StripeService

@pytest.fixture
def mock_stripe():
    with patch("app.services.stripe_service.stripe") as mock:
        yield mock

def test_create_payment_intent_success(mock_stripe):
    mock_stripe.PaymentIntent.create.return_value = MagicMock(
        client_secret="secret",
        id="pi_123"
    )

    result = StripeService.create_payment_intent("credits_100", "user_123")

    assert result["client_secret"] == "secret"
    assert result["payment_intent_id"] == "pi_123"
    assert result["amount"] == 19.99

    mock_stripe.PaymentIntent.create.assert_called_once()

def test_create_payment_intent_invalid_product(mock_stripe):
    with pytest.raises(ValueError, match="Invalid product"):
        StripeService.create_payment_intent("invalid_product", "user_123")

def test_create_subscription_success(mock_stripe):
    mock_stripe.Customer.create.return_value = MagicMock(id="cus_123")
    mock_stripe.Price.create.return_value = MagicMock(id="price_123")
    mock_stripe.Subscription.create.return_value = MagicMock(
        id="sub_123",
        status="active",
        current_period_end=1234567890
    )

    result = StripeService.create_subscription("premium_monthly", "user_123", "pm_123")

    assert result["subscription_id"] == "sub_123"
    assert result["customer_id"] == "cus_123"
    assert result["status"] == "active"

def test_verify_webhook_success(mock_stripe):
    mock_stripe.Webhook.construct_event.return_value = {"type": "test_event"}

    event = StripeService.verify_webhook(b"payload", "sig_123")
    assert event == {"type": "test_event"}

def test_verify_webhook_failure(mock_stripe):
    mock_stripe.Webhook.construct_event.side_effect = ValueError("Invalid payload")

    event = StripeService.verify_webhook(b"payload", "sig_123")
    assert event is None
