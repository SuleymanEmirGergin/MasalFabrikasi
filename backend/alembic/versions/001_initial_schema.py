"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-03-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enums ---
    # Create enums manually if not creating via SQLAlchemy types in some versions
    # But here we use sa.Enum which usually handles it.
    
    # --- User Profiles ---
    op.create_table('user_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('auth_user_id', sa.UUID(), nullable=False),
        sa.Column('xp', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('credits_remaining', sa.Integer(), nullable=False),
        sa.Column('subscription_tier', sa.Enum('FREE', 'PREMIUM', 'PRO', name='subscriptiontier'), nullable=False),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('statistics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_profiles_auth_user_id', 'user_profiles', ['auth_user_id'], unique=True)
    op.create_index('ix_user_profiles_tier', 'user_profiles', ['subscription_tier'], unique=False)

    # --- Stories ---
    op.create_table('stories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('theme', sa.String(length=500), nullable=False),
        sa.Column('story_text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('story_type', sa.String(length=50), nullable=False),
        sa.Column('image_url', sa.String(length=1000), nullable=True),
        sa.Column('image_public_id', sa.String(length=500), nullable=True),
        sa.Column('audio_url', sa.String(length=1000), nullable=True),
        sa.Column('audio_public_id', sa.String(length=500), nullable=True),
        sa.Column('audio_duration_seconds', sa.Float(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('like_count', sa.Integer(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stories_created_at', 'stories', ['created_at'], unique=False)
    op.create_index('ix_stories_is_favorite', 'stories', ['is_favorite'], unique=False)
    op.create_index('ix_stories_language', 'stories', ['language'], unique=False)
    op.create_index('ix_stories_story_type', 'stories', ['story_type'], unique=False)
    op.create_index('ix_stories_theme', 'stories', ['theme'], unique=False)
    op.create_index('ix_stories_user_created', 'stories', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_stories_user_id', 'stories', ['user_id'], unique=False)

    # --- Jobs ---
    op.create_table('jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('story_id', sa.UUID(), nullable=True),
        sa.Column('job_type', sa.Enum('STORY_GENERATION', 'IMAGE_GENERATION', 'TTS_GENERATION', 'COMPLETE_STORY', name='jobtype'), nullable=False),
        sa.Column('status', sa.Enum('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED', name='jobstatus'), nullable=False),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_jobs_celery_task_id', 'jobs', ['celery_task_id'], unique=True)
    op.create_index('ix_jobs_created_at', 'jobs', ['created_at'], unique=False)
    op.create_index('ix_jobs_status', 'jobs', ['status'], unique=False)
    op.create_index('ix_jobs_user_created', 'jobs', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'], unique=False)
    op.create_index('ix_jobs_user_status', 'jobs', ['user_id', 'status'], unique=False)

    # --- Subscriptions ---
    op.create_table('subscriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('plan_type', sa.Enum('FREE', 'PREMIUM', 'PRO', name='subscriptiontier'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'CANCELLED', 'PAST_DUE', 'TRIALING', name='subscriptionstatus'), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'], unique=False)
    op.create_index('ix_subscriptions_stripe_customer_id', 'subscriptions', ['stripe_customer_id'], unique=True)
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'], unique=False)
    # Note: stripe_subscription_id is also unique but not explicitly indexed in models as much as customer_id usually.
    # But model said unique=True so let's add it.
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True)

    # --- Story Analytics ---
    op.create_table('story_analytics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('story_id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_story_analytics_created_at', 'story_analytics', ['created_at'], unique=False)
    op.create_index('ix_story_analytics_event_type', 'story_analytics', ['event_type'], unique=False)
    op.create_index('ix_story_analytics_story_event', 'story_analytics', ['story_id', 'event_type'], unique=False)
    op.create_index('ix_story_analytics_story_id', 'story_analytics', ['story_id'], unique=False)


def downgrade() -> None:
    op.drop_table('story_analytics')
    op.drop_table('subscriptions')
    op.drop_table('jobs')
    op.drop_table('stories')
    op.drop_table('user_profiles')
    
    # Drop enums
    sa.Enum(name='subscriptiontier').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='jobtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='jobstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptionstatus').drop(op.get_bind(), checkfirst=True)
