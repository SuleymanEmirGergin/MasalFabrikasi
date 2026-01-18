"""add enhancement history column

Revision ID: 009_add_enhancement_history
Revises: 008_add_auth_and_gdpr_tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_enhancement_history'
down_revision = '008_add_auth_and_gdpr_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Check if metadata column exists, if not create it (stories table usually has it)
    # But just in case, we are relying on JSONB for now.
    pass

def downgrade():
    pass
