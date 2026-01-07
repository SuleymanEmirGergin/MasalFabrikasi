"""add title column

Revision ID: 007_add_title_column
Revises: 006_add_sharing_fields
Create Date: 2026-01-07 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_title_column'
down_revision = '006_add_sharing_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('stories', sa.Column('title', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('stories', 'title')
