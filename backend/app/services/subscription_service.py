
import stripe
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import UserProfile, Subscription, SubscriptionTier, SubscriptionStatus
from app.repositories.user_repository import UserRepository
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def create_checkout_session(self, user_id: str, price_id: str, success_url: str, cancel_url: str) -> str:
        """
        Creates a Stripe Checkout Session for a subscription.
        """
        try:
            user_profile = self.user_repo.get_profile_by_auth_id(user_id)
            if not user_profile:
                # In a real app, you might create one here or raise an error
                raise ValueError("User profile not found")

            # Get user email - in this simple setup we don't have it directly in UserProfile, 
            # ideally we fetch it from Auth provider or if stored in profile
            # For now, we'll let Stripe handle email collection or pass a dummy if needed.
            # Assuming 'user_id' is the Auth UUID.
            
            # Check if customer exists
            # We need to store stripe_customer_id in UserProfile or Subscription model
            # Let's assume we check/create customer
            customer_id = self._get_or_create_stripe_customer(user_profile)

            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user_id)
                }
            )
            return checkout_session.url
        except Exception as e:
            print(f"Checkout Session creation failed: {str(e)}")
            raise

    def create_portal_session(self, user_id: str, return_url: str) -> str:
        """
        Creates a Stripe Customer Portal session for managing subscriptions.
        """
        try:
            user_profile = self.user_repo.get_profile_by_auth_id(user_id)
            customer_id = self._get_stripe_customer_id(user_profile)
            
            if not customer_id:
                raise ValueError("No Stripe customer found for this user")

            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return portal_session.url
        except Exception as e:
            print(f"Portal Session creation failed: {str(e)}")
            raise

    def handle_webhook(self, payload: bytes, sig_header: str):
        """
        Handles Stripe webhooks to update local subscription state.
        """
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise ValueError("Invalid signature")

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_session_completed(session)
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            self._handle_subscription_updated(subscription)
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            self._handle_subscription_deleted(subscription)
        
        return {"status": "success"}

    def _get_or_create_stripe_customer(self, user_profile: UserProfile) -> str:
        """Helper to get or create a Stripe customer for a user."""
        # Check if we have a subscription record with customer_id
        # In a real app we might store stripe_customer_id directly on UserProfile or a separate mapping
        
        existing_sub = self.db.query(Subscription).filter(Subscription.user_id == user_profile.id).first()
        
        if existing_sub and existing_sub.stripe_customer_id:
            return existing_sub.stripe_customer_id
        
        # Create new customer
        customer = stripe.Customer.create(
            metadata={'user_id': str(user_profile.auth_user_id)}
        )
        
        # Create a placeholder subscription record to store customer_id? 
        # Or better, UserProfile should have it. But UserProfile model is defined in models.py 
        # and doesn't seem to have stripe_customer_id (it was in Subscription model).
        # We will create a dummy/inactive subscription to store the customer ID if needed, 
        # or just rely on creating it when a real sub starts. 
        # Actually, best practice: Create customer, return ID. We'll save it when webhook fires 
        # OR we save it now. Let's save it now if we can.
        
        # NOTE: Ideally UserProfile has stripe_customer_id. 
        # Given existing schema, Subscription has it.
        # We'll return customer.id and let the webhook logic simplify persistence for now,
        # or creating a prelim Subscription record.
        
        return customer.id

    def _get_stripe_customer_id(self, user_profile: UserProfile) -> Optional[str]:
        existing_sub = self.db.query(Subscription).filter(Subscription.user_id == user_profile.id).first()
        return existing_sub.stripe_customer_id if existing_sub else None

    def _handle_checkout_session_completed(self, session):
        # Retrieve user_id from metadata
        user_auth_id = session.get('metadata', {}).get('user_id')
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        
        if user_auth_id and subscription_id:
            # Fetch subscription details from Stripe to get plan/status
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            self._update_local_subscription(user_auth_id, customer_id, stripe_sub)

    def _handle_subscription_updated(self, stripe_sub):
        # Find user by customer_id
        customer_id = stripe_sub.get('customer')
        # We need to find the user associated with this customer_id
        # This requires a reverse lookup. 
        # Since we put user_id in metadata of customer or subscription, we can try that.
        # Or query DB for subscription with this customer_id.
        
        self._update_subscription_from_stripe_object(stripe_sub)

    def _handle_subscription_deleted(self, stripe_sub):
        self._update_subscription_from_stripe_object(stripe_sub, is_deleted=True)

    def _update_local_subscription(self, user_auth_id: str, customer_id: str, stripe_sub):
        user_profile = self.user_repo.get_profile_by_auth_id(user_auth_id)
        if not user_profile:
            return

        self._upsert_subscription(user_profile, customer_id, stripe_sub)

    def _update_subscription_from_stripe_object(self, stripe_sub, is_deleted=False):
        customer_id = stripe_sub.get('customer')
        # Find local subscription
        local_sub = self.db.query(Subscription).filter(Subscription.stripe_customer_id == customer_id).first()
        if local_sub:
            user_profile = local_sub.user
            self._upsert_subscription(user_profile, customer_id, stripe_sub, is_deleted)

    def _upsert_subscription(self, user_profile, customer_id, stripe_sub, is_deleted=False):
        # Map Stripe Price ID to internal Tier
        price_id = stripe_sub['items']['data'][0]['price']['id']
        tier = SubscriptionTier.FREE
        if price_id == settings.STRIPE_PRICE_ID_PREMIUM_MONTHLY:
            tier = SubscriptionTier.PREMIUM
        elif price_id == settings.STRIPE_PRICE_ID_PRO_MONTHLY:
            tier = SubscriptionTier.PRO
        
        status_map = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELLED,
            'past_due': SubscriptionStatus.PAST_DUE,
            'trialing': SubscriptionStatus.TRIALING
        }
        status = status_map.get(stripe_sub['status'], SubscriptionStatus.ACTIVE)
        
        if is_deleted:
            status = SubscriptionStatus.CANCELLED
            tier = SubscriptionTier.FREE # Revert to free? Or keep history?
            # Usually we keep record but downgrade user access.

        # Check existing
        sub = self.db.query(Subscription).filter(Subscription.user_id == user_profile.id).first()
        if not sub:
            sub = Subscription(user_id=user_profile.id)
            self.db.add(sub)
        
        sub.stripe_customer_id = customer_id
        sub.stripe_subscription_id = stripe_sub['id']
        sub.plan_type = tier
        sub.status = status
        sub.current_period_end = None # timestamp conversion needed if strictly utilizing
        
        # Update User Profile tier as well
        user_profile.subscription_tier = tier
        
        self.db.commit()
