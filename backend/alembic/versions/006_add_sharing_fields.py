"""Add sharing fields to stories

Revision ID: 006_add_sharing_fields
Revises: 005_update_embedding_size
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_add_sharing_fields'
down_revision = '005_update_embedding_size'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns
    op.add_column('stories', sa.Column('share_token', sa.String(length=100), nullable=True))
    op.add_column('stories', sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    # Create index
    op.create_index(op.f('ix_stories_share_token'), 'stories', ['share_token'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_stories_share_token'), table_name='stories')
    op.drop_column('stories', 'is_public')
    op.drop_column('stories', 'share_token')
