"""
Database migration: Add performance indexes
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '003_add_performance_indexes'
down_revision = '002_add_embedding_column'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for better query performance"""
    
    # Stories table indexes
    op.create_index('idx_stories_user_id', 'stories', ['user_id'])
    op.create_index('idx_stories_created_at', 'stories', ['created_at'])
    op.create_index('idx_stories_story_type', 'stories', ['story_type'])
    op.create_index('idx_stories_language', 'stories', ['language'])
    op.create_index('idx_stories_is_favorite', 'stories', ['is_favorite'])
    op.create_index('idx_stories_user_created', 'stories', ['user_id', 'created_at'])
    
    # Jobs table indexes
    op.create_index('idx_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('idx_jobs_status', 'jobs', ['status'])
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'])
    
    # User profiles indexes
    # User profiles indexes
    op.create_index('idx_user_profiles_auth_id', 'user_profiles', ['auth_user_id'])
    op.create_index('idx_user_profiles_xp', 'user_profiles', ['xp'])
    
    # Achievements indexes - Table not created yet
    # op.create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    # op.create_index('idx_user_achievements_unlocked_at', 'user_achievements', ['unlocked_at'])


def downgrade():
    """Remove indexes"""
    
    # Stories indexes
    op.drop_index('idx_stories_user_id')
    op.drop_index('idx_stories_created_at')
    op.drop_index('idx_stories_story_type')
    op.drop_index('idx_stories_language')
    op.drop_index('idx_stories_is_favorite')
    op.drop_index('idx_stories_user_created')
    
    # Jobs indexes
    op.drop_index('idx_jobs_user_id')
    op.drop_index('idx_jobs_status')
    op.drop_index('idx_jobs_created_at')
    
    # User profiles indexes
    # User profiles indexes
    op.drop_index('idx_user_profiles_auth_id')
    op.drop_index('idx_user_profiles_xp')
    
    # Achievements indexes
    # op.drop_index('idx_user_achievements_user_id')
    # op.drop_index('idx_user_achievements_unlocked_at')
