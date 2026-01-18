"""add stripe events

Revision ID: 010_add_stripe_events
Revises: 009_harden_auth_tokens
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_add_stripe_events'
down_revision = '009_harden_auth_tokens'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('processed_stripe_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processed_stripe_events_event_id'), 'processed_stripe_events', ['event_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_processed_stripe_events_event_id'), table_name='processed_stripe_events')
    op.drop_table('processed_stripe_events')
