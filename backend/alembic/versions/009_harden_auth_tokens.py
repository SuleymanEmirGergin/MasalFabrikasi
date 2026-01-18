"""harden auth tokens

Revision ID: 009_harden_auth_tokens
Revises: 008_add_auth_tokens
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_harden_auth_tokens'
down_revision = '008_add_auth_tokens'
branch_labels = None
depends_on = None


def upgrade():
    # Password Reset Tokens
    op.alter_column('password_reset_tokens', 'token', new_column_name='token_hash')
    op.add_column('password_reset_tokens', sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_password_reset_tokens_consumed_at'), 'password_reset_tokens', ['consumed_at'], unique=False)
    # Re-create index for renamed column if needed (Alembic usually handles this, but let's be safe)
    # op.drop_index('ix_password_reset_tokens_token', table_name='password_reset_tokens')
    # op.create_index(op.f('ix_password_reset_tokens_token_hash'), 'password_reset_tokens', ['token_hash'], unique=True)

    # Email Verification Tokens
    op.alter_column('email_verification_tokens', 'token', new_column_name='token_hash')
    op.add_column('email_verification_tokens', sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_email_verification_tokens_consumed_at'), 'email_verification_tokens', ['consumed_at'], unique=False)


def downgrade():
    # Email Verification Tokens
    op.drop_index(op.f('ix_email_verification_tokens_consumed_at'), table_name='email_verification_tokens')
    op.drop_column('email_verification_tokens', 'consumed_at')
    op.alter_column('email_verification_tokens', 'token_hash', new_column_name='token')

    # Password Reset Tokens
    op.drop_index(op.f('ix_password_reset_tokens_consumed_at'), table_name='password_reset_tokens')
    op.drop_column('password_reset_tokens', 'consumed_at')
    op.alter_column('password_reset_tokens', 'token_hash', new_column_name='token')
