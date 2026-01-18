"""
SQLAlchemy Database Models - Unified Package
"""



import sys
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, Enum, Index, CheckConstraint, DECIMAL, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
import enum

from app.core.database import Base


# Enums
class JobStatus(str, enum.Enum):
    """Job queue status"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Job types for async processing"""
    STORY_GENERATION = "story_generation"
    IMAGE_GENERATION = "image_generation"
    TTS_GENERATION = "tts_generation"
    COMPLETE_STORY = "complete_story"


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers"""
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


# Models
class User(Base):
    """
    Local Authentication User
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class PasswordResetToken(Base):
    """
    Password reset tokens
    """
    __tablename__ = "password_reset_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")


class EmailVerificationToken(Base):
    """
    Email verification tokens
    """
    __tablename__ = "email_verification_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")


class UserProfile(Base):
    """
    User profile - Supabase auth.users'a referans yapar
    """
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Supabase auth.users.id ile eşleşir
    auth_user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    
    # User stats
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    # Credits and Gamification
    credits = Column(Integer, default=10, nullable=False)
    streak_count = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Referral system
    referral_code = Column(String(50), unique=True, index=True, nullable=True)
    referred_by = Column(String(50), nullable=True)
    
    # Subscription info
    subscription_tier = Column(
        Enum(SubscriptionTier), 
        default=SubscriptionTier.FREE, 
        nullable=False
    )
    
    # Preferences and statistics (JSONB for flexibility)
    preferences = Column(JSONB, default=dict, nullable=False)
    statistics = Column(JSONB, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes and Table Args
    __table_args__ = (
        Index('ix_user_profiles_auth_user_id', 'auth_user_id'),
        Index('ix_user_profiles_tier', 'subscription_tier'),
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, level={self.level}, tier={self.subscription_tier})>"


class Story(Base):
    """
    Story metadata
    """
    __tablename__ = "stories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Story content
    title = Column(String(255), nullable=True)
    theme = Column(String(500), nullable=False)
    story_text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False, default="tr")
    story_type = Column(String(50), nullable=False, default="masal")
    
    # URLs
    image_url = Column(String(1000), nullable=True)
    image_public_id = Column(String(500), nullable=True)
    
    audio_url = Column(String(1000), nullable=True)
    audio_public_id = Column(String(500), nullable=True)
    audio_duration_seconds = Column(Float, nullable=True)
    
    # Metadata
    is_favorite = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    
    # Extra metadata
    meta_data = Column("metadata", JSONB, default=dict, nullable=False)
    
    # Embedding (Gemini embedding: 768 dimensions)
    embedding = Column(Vector(768), nullable=True)

    # Sharing (Viral Growth Engine)
    share_token = Column(String(100), unique=True, index=True, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("UserProfile", back_populates="stories")
    jobs = relationship("Job", back_populates="story")
    analytics = relationship("StoryAnalytics", back_populates="story", cascade="all, delete-orphan")
    analysis = relationship("StoryAnalysis", back_populates="story", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Story(id={self.id}, theme='{self.theme[:30]}...')>"


class Job(Base):
    """Job queue"""
    __tablename__ = "jobs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True)
    celery_task_id = Column(String(255), nullable=True, unique=True, index=True)
    
    input_data = Column(JSONB, nullable=False)
    result_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    
    progress_percent = Column(Integer, default=0, nullable=False)
    current_step = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("UserProfile", back_populates="jobs")
    story = relationship("Story", back_populates="jobs")


class Purchase(Base):
    """Purchases"""
    __tablename__ = "purchases"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    product_id = Column(String(255), nullable=False)
    credits_added = Column(Integer, default=0, nullable=False)
    
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(255), nullable=False, unique=True, index=True)
    
    receipt_data = Column(JSONB, nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("UserProfile")


class InteractiveStory(Base):
    __tablename__ = "interactive_stories"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    character_name = Column(String(100), nullable=True)
    theme = Column(String(255), nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("UserProfile")
    segments = relationship("StorySegment", back_populates="story", cascade="all, delete-orphan")


class StorySegment(Base):
    __tablename__ = "story_segments"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("interactive_stories.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    image_url = Column(String(1000), nullable=True)
    audio_url = Column(String(1000), nullable=True)
    step_number = Column(Integer, default=1, nullable=False)
    is_ending = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    story = relationship("InteractiveStory", back_populates="segments")
    choices = relationship("StoryChoice", back_populates="segment", cascade="all, delete-orphan", foreign_keys="[StoryChoice.segment_id]")


class StoryChoice(Base):
    __tablename__ = "story_choices"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("story_segments.id", ondelete="CASCADE"), nullable=False, index=True)
    choice_text = Column(String(500), nullable=False)
    next_segment_id = Column(UUID(as_uuid=True), ForeignKey("story_segments.id", ondelete="SET NULL"), nullable=True)
    is_selected = Column(Boolean, default=False)
    
    segment = relationship("StorySegment", foreign_keys=[segment_id], back_populates="choices")
    next_segment = relationship("StorySegment", foreign_keys=[next_segment_id])


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True, index=True)
    plan_type = Column(Enum(SubscriptionTier), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=True)
    currency = Column(String(3), default="TRY", nullable=False)
    meta_data = Column("metadata", JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("UserProfile", back_populates="subscriptions")


class StoryAnalytics(Base):
    __tablename__ = "story_analytics"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    meta_data = Column("metadata", JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    story = relationship("Story", back_populates="analytics")


class DailyQuest(Base):
    __tablename__ = "daily_quests"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    quest_type = Column(String(50), nullable=False)
    target_count = Column(Integer, default=1, nullable=False)
    current_progress = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    xp_reward = Column(Integer, default=10, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("UserProfile")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(String(100), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("UserProfile")


class StoryAnalysis(Base):
    __tablename__ = "story_analyses"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, unique=True)
    vocabulary_count = Column(Integer, default=0)
    unique_words = Column(Integer, default=0)
    complexity_score = Column(Float, default=0.0)
    educational_themes = Column(JSONB, nullable=True)
    keywords = Column(JSONB, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    story = relationship("Story", back_populates="analysis")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("UserProfile")
    story = relationship("Story")


# Import sub-modules for easier access


class Character(Base):
    """
    AI Characters for chat and interaction.
    """
    __tablename__ = "characters"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    avatar_url = Column(String(1000), nullable=True)
    voice_id = Column(String(100), nullable=True)
    
    is_public = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    creator = relationship("UserProfile")


class UserDevice(Base):
    """
    Stores user device information for push notifications.
    """
    __tablename__ = "user_devices"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    push_token = Column(String, nullable=False, unique=True, index=True)
    platform = Column(String, nullable=True)  # ios, android, web
    device_name = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("UserProfile", backref="devices")

class Waitlist(Base):
    """
    Landing page email waitlist
    """
    __tablename__ = "waitlist"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    source = Column(String(50), nullable=True, default="landing_page")
    meta_data = Column("metadata", JSONB, default=dict, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Waitlist(email={self.email})>"


class ProcessedStripeEvent(Base):
    """
    Track processed Stripe webhook events for idempotency
    """
    __tablename__ = "processed_stripe_events"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), unique=True, index=True, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
