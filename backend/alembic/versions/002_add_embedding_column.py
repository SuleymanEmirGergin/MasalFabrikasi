
import asyncio
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '002_add_embedding_column'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Enable vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # 2. Add column
    op.add_column('stories', sa.Column('embedding', Vector(1536), nullable=True))
    
    # Optional: Add index for faster search (requires more rows to be effective usually)
    # op.create_index('ix_stories_embedding', 'stories', ['embedding'], postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})

def downgrade() -> None:
    op.drop_column('stories', 'embedding')
    # op.execute("DROP EXTENSION vector") # Usually we don't drop extension in migration as other tables might use it
