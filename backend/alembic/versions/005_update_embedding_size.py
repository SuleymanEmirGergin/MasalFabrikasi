"""Update embedding vector size for Gemini

Revision ID: 005_update_embedding_size
Revises: 004_add_users_table
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '005_update_embedding_size'
down_revision = '004_add_users_table'
branch_labels = None
depends_on = None


def upgrade():
    # Change embedding column from Vector(1536) to Vector(768) for Gemini
    # PostgreSQL doesn't support ALTER TYPE directly for vector, so we need to:
    # 1. Drop the old column
    # 2. Create a new one with correct dimensions
    
    op.drop_column('stories', 'embedding')
    op.add_column('stories', sa.Column('embedding', Vector(768), nullable=True))
    
    # Recreate index if it existed
    # op.create_index('ix_stories_embedding', 'stories', ['embedding'], postgresql_using='ivfflat')


def downgrade():
    # Revert back to Vector(1536)
    op.drop_column('stories', 'embedding')
    op.add_column('stories', sa.Column('embedding', Vector(1536), nullable=True))
