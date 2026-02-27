from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from app.models import UserProfile, Subscription, SubscriptionTier, SubscriptionStatus
from app.core.database import SessionLocal

class UserRepository:
    def __init__(self, db_session: Session = None):
        self.db = db_session if db_session else SessionLocal()

    def get_profile_by_auth_id(self, auth_user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by Supabase auth ID."""
        return self.db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()

    def get_profile_by_id(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by internal ID."""
        return self.db.query(UserProfile).filter(UserProfile.id == user_id).first()

    def create_profile(self, auth_user_id: UUID, subscription_tier: SubscriptionTier = SubscriptionTier.FREE) -> UserProfile:
        """Create a new user profile linked to Supabase auth."""
        try:
            profile = UserProfile(
                auth_user_id=auth_user_id,
                subscription_tier=subscription_tier,
                credits_remaining=10 if subscription_tier == SubscriptionTier.FREE else 100,
                xp=0,
                level=1,
                preferences={},
                statistics={}
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception as e:
            self.db.rollback()
            raise e

    def update_profile(self, user_id: UUID, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile."""
        profile = self.get_profile_by_id(user_id)
        if not profile:
            return None
            
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception as e:
            self.db.rollback()
            raise e

    def add_xp(self, user_id: UUID, amount: int) -> UserProfile:
        """Add XP to user and handle leveling up."""
        profile = self.get_profile_by_id(user_id)
        if not profile:
            return None
            
        profile.xp += amount
        
        # Simple level calculation: Level = 1 + (XP / 1000)
        new_level = 1 + (profile.xp // 1000)
        if new_level > profile.level:
            profile.level = new_level
            # Bonus credits on level up?
            profile.credits_remaining += 5
            
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def consume_credit(self, user_id: UUID, amount: int = 1) -> bool:
        """Consume credits. Return False if insufficient."""
        profile = self.get_profile_by_id(user_id)
        if not profile:
            return False
            
        if profile.credits_remaining < amount:
            return False
            
        profile.credits_remaining -= amount
        self.db.commit()
        self.db.refresh(profile)
        return True

    def update_subscription(
        self, 
        user_id: UUID, 
        tier: SubscriptionTier, 
        stripe_customer_id: str = None,
        stripe_subscription_id: str = None,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    ) -> UserProfile:
        """Update subscription status."""
        profile = self.get_profile_by_id(user_id)
        if not profile:
            return None
            
        profile.subscription_tier = tier
        
        # Check if subscription record exists
        sub = self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
        if sub:
            sub.plan_type = tier
            sub.status = status
            if stripe_subscription_id:
                sub.stripe_subscription_id = stripe_subscription_id
        else:
            # Create new subscription record
            sub = Subscription(
                user_id=user_id,
                plan_type=tier,
                status=status,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                currency="TRY",
                metadata={}
            )
            self.db.add(sub)
            
        self.db.commit()
        self.db.refresh(profile)
        return profile


def get_user_repository(db: Session) -> UserRepository:
    """Helper to get user repository instance."""
    return UserRepository(db)

