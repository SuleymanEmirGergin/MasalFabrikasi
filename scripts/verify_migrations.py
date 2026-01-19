import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.core.config import settings

async def verify_migrations():
    """
    Verifies that critical database constraints exist.
    """
    print("🔍 Verifying database constraints...")

    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url)

    async with engine.connect() as conn:
        # Check password_reset_tokens table
        try:
            # Check table existence
            await conn.execute(text("SELECT 1 FROM password_reset_tokens LIMIT 1"))
            print("✅ Table 'password_reset_tokens' exists.")

            # Check token_hash column
            await conn.execute(text("SELECT token_hash FROM password_reset_tokens LIMIT 1"))
            print("✅ Column 'token_hash' exists in 'password_reset_tokens'.")

            # Check consumed_at column
            await conn.execute(text("SELECT consumed_at FROM password_reset_tokens LIMIT 1"))
            print("✅ Column 'consumed_at' exists in 'password_reset_tokens'.")

        except Exception as e:
            print(f"❌ Verification failed for 'password_reset_tokens': {e}")
            sys.exit(1)

        # Check processed_stripe_events table
        try:
            await conn.execute(text("SELECT 1 FROM processed_stripe_events LIMIT 1"))
            print("✅ Table 'processed_stripe_events' exists.")

            await conn.execute(text("SELECT event_id FROM processed_stripe_events LIMIT 1"))
            print("✅ Column 'event_id' exists in 'processed_stripe_events'.")

        except Exception as e:
            print(f"❌ Verification failed for 'processed_stripe_events': {e}")
            sys.exit(1)

    print("✅ Migration verification successful!")

if __name__ == "__main__":
    asyncio.run(verify_migrations())
